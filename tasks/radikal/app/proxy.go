package main

import (
	"io"
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"syscall"
	"time"
)

func main() {
	if len(os.Args) < 6 {
		log.Fatalf("Usage: %s base_path listen_path proxy_port cmd args...", os.Args[0])
	}

	basePath := os.Args[1]
	listenPath := os.Args[2]
	proxyPort := os.Args[3]
	cmdArgs := os.Args[4:]

	targetHost := "127.0.0.1:" + proxyPort

	proxy := &httputil.ReverseProxy{
		Director: func(req *http.Request) {
			req.URL.Scheme = "http"
			req.URL.Host = targetHost
			token := strings.Split(req.URL.Path, "/")[1]
			req.URL.Path = strings.Replace(req.URL.Path, "/"+token, "/"+basePath, 1)
			req.Header.Add("X-Token", token)
		},
		ModifyResponse: func(resp *http.Response) error {
			token := resp.Request.Header.Get("X-Token")

			bodyBytes, err := io.ReadAll(resp.Body)
			if err != nil {
				return err
			}

			resp.Body.Close()

			bodyStr := strings.ReplaceAll(string(bodyBytes), basePath, token)
			newBody := io.NopCloser(strings.NewReader(bodyStr))

			resp.Body = newBody
			resp.ContentLength = int64(len(bodyStr))
			resp.Header.Set("Content-Length", strconv.Itoa(len(bodyStr)))

			if resp.Header.Get("Location") != "" {
				resp.Header.Set("Location", strings.Replace(resp.Header.Get("Location"), "/"+basePath, "/"+token, 1))
			}

			if resp.Header.Get("Refresh") != "" {
				resp.Header.Set("Refresh", strings.Replace(resp.Header.Get("Refresh"), "/"+basePath, "/"+token, 1))
			}

			return nil
		},
	}

	uploadDir := os.Getenv("UPLOAD_DIR")
	if uploadDir == "" {
		log.Fatalf("UPLOAD_DIR environment variable is not set")
	}
	staticFileRegex := regexp.MustCompile(`^/([A-Za-z0-9]+)/uploads/([A-Za-z0-9._-]+)$`)

	client := &http.Client{}

	httpHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token := strings.Split(r.URL.Path, "/")[1]
		checkURL := "http://token:54327/" + token

		req, err := http.NewRequest("GET", checkURL, nil)
		if err != nil {
			log.Printf("Failed to validate URL: %v", err)
			http.Error(w, "Failed", http.StatusInternalServerError)
			return
		}

		resp, err := client.Do(req)
		if err != nil {
			log.Printf("Failed to validate URL: %v", err)
			http.Error(w, "Failed", http.StatusInternalServerError)
			return
		}
		resp.Body.Close()

		if resp.StatusCode == 403 {
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}

		if matches := staticFileRegex.FindStringSubmatch(r.URL.Path); len(matches) == 3 {
			uploadPrefix := matches[1]
			fileRelPath := matches[2]

			fullPath := filepath.Join(uploadDir, uploadPrefix, fileRelPath)
			http.ServeFile(w, r, fullPath)
			return
		}

		proxy.ServeHTTP(w, r)
	})

	childExitChan := make(chan int, 1)
	go func() {
		cmd := exec.Command(cmdArgs[0], cmdArgs[1:]...)
		cmd.Stdin = os.Stdin
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr

		log.Printf("Starting command: %s", strings.Join(cmdArgs, " "))
		if err := cmd.Run(); err != nil {
			if exitErr, ok := err.(*exec.ExitError); ok {
				log.Printf("Command exited with code %d", exitErr.ExitCode())
				childExitChan <- exitErr.ExitCode()
				return
			} else {
				log.Fatalf("Failed to run command: %v", err)
			}
		}
		log.Println("Command exited successfully")
		childExitChan <- 0
	}()

	log.Printf("Waiting for underlying server to accept connections at %s", targetHost)
	for {
		select {
		case exitCode := <-childExitChan:
			log.Printf("Child process exited with code %d before underlying server was available", exitCode)
			os.Exit(exitCode)
		default:
			conn, err := net.DialTimeout("tcp", targetHost, 100*time.Millisecond)
			if err == nil {
				conn.Close()
				log.Printf("Underlying server at %s is now accepting connections", targetHost)
				goto startProxy
			}
			log.Printf("Underlying server at %s not yet available, retrying...", targetHost)
			time.Sleep(100 * time.Millisecond)
		}
	}

startProxy:
	socket, err := net.Listen("unix", listenPath)
	if err != nil {
		log.Fatalf("Failed to listen on %s: %v", listenPath, err)
	}

	if err := os.Chmod(listenPath, 0777); err != nil {
		log.Fatalf("Failed to chmod %s: %v", listenPath, err)
	}

	defer socket.Close()

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-c
		os.Remove(listenPath)
		os.Exit(0)
	}()

	go func() {
		server := http.Server{Handler: httpHandler}
		log.Printf("Starting proxy server on %s forwarding to %s", listenPath, targetHost)
		if err := server.Serve(socket); err != nil {
			log.Fatalf("HTTP server error: %v", err)
		}
	}()

	exitCode := <-childExitChan
	os.Exit(exitCode)
}
