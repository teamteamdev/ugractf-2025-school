package main

import (
	"flag"
	"log"
	"net/http"
)

var (
	addr = flag.String("addr", ":8080", "addr to listen")
)

func main() {
	log.Printf("starting serving at %q...", *addr)

	http.HandleFunc("GET /{token}", getHandler)
	http.HandleFunc("POST /{token}", postHandler)

	if err := http.ListenAndServe(*addr, nil); err != nil {
		log.Fatal(err)
	}
}
