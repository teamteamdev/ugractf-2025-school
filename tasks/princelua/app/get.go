package main

import (
	"net/http"
)

func getHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	t.Execute(w, tArgs{
		Token: r.PathValue("token"),
	})
}
