.PHONY: all clean

all: run

run: runner.c
	gcc -std=c17 -g -llua runner.c -o run

run_alpine:
	gcc -I/usr/include/lua5.4 runner.c /usr/lib/lua5.4/liblua.a -o run_alpine

clean:
	rm -rf run run_alpine
