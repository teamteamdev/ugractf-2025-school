package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"text/template"
	"time"
)

var (
	ft = template.Must(template.New("").Parse(`
return function(is_trusted)
  local w = { is_trusted }
  local function untrusted()
    warn("castle.open() called in untrusted mode!")
  end
  return function()
    if not w[1]() then return untrusted() end
    local s = {{ printf "%q" . }} .. "48vbjw8ds1vFD0ds"
    local h = 2166136261
    for i = 1, #s do
      h = h ~ string.byte(s, i)
      h = (h * 16777619) & 0xffffffff
    end
    if not w[1]() then return untrusted() end
    print("Castle opened!")
    print(string.format("ugra_princ3ss_1s_fre3d_by_y0u_%x", h))
  end
end
	`))
)

func postHandler(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintln(w, err.Error())
		return
	}

	token := r.PathValue("token")
	value := r.FormValue("value")

	firmFile, err := os.CreateTemp("", "firm")
	if err != nil {
		log.Printf("failed create temp file: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		fmt.Fprintln(w, "Internal Server Error")
		return
	}
	defer func() {
		firmFile.Close()
		os.Remove(firmFile.Name())
	}()

	if err := ft.Execute(firmFile, token); err != nil {
		log.Printf("failed write firmware: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		fmt.Fprintln(w, "Internal Server Error")
		return
	}
	firmFile.Close()

	ctx, cancel := context.WithTimeout(r.Context(), 1*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "./run", "-f", firmFile.Name())
	cmd.Stdin = strings.NewReader(value)
	out, _ := cmd.CombinedOutput()
	if cmd.ProcessState.ExitCode() == -1 {
		out = []byte("Timeout")
	}

	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	t.Execute(w, tArgs{
		Token:  token,
		Value:  value,
		Output: string(out),
	})
}
