package main

import "html/template"

var (
	t = template.Must(template.New("").Parse(`
<h3>Write your user program for castle</h3>
<form action="/{{.Token}}" method="POST">
  <textarea name="value" rows="30">{{.Value}}</textarea>
	<br />
  <input type="submit" value="Submit">
</form>
{{ if .Output }}
<h3>Output</h3>
<pre>
{{ .Output }}
</pre>
{{ end }}
<style>
	form, textarea, input {
		margin-bottom: 1em;
	  width: 100%;
	}

	h3 {
		text-align: center;
	}
</style>
	`))
)

type tArgs struct {
	Token  string
	Value  string
	Output string
}
