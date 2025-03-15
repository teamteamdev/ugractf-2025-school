#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <getopt.h>

#include <lua.h>
#include <lauxlib.h>
#include <lualib.h>

lua_State *L;

static void _lua_close() {
  lua_close(L);
}

static const size_t MAX_ALLOC_BYTES = 32 * 1024;
static void* _counting_alloc(void* ud, void* ptr, size_t osize, size_t nsize) {
  static size_t total_allocated = 0;
  if (ptr != NULL) {
    if (osize > nsize) {
      total_allocated -= osize - nsize;
    } else {
      total_allocated += nsize - osize;
    }
  } else {
    total_allocated += nsize;
  }
  if (total_allocated > MAX_ALLOC_BYTES) {
    return NULL;
  }

  if (nsize == 0) {
    free(ptr);
    return NULL;
  } else {
    return realloc(ptr, nsize);
  }
}

static void _warn(void* ud, const char* msg, int tocont) {
  fputs(msg, stderr);
  if (!tocont) {
    fputc('\n', stderr);
    fflush(stderr);
  }
}

static void _init_lua() {
  luaL_requiref(L, "_G", &luaopen_base, 1);
  lua_pushnil(L); lua_setfield(L, -2, "dofile");
  lua_pushnil(L); lua_setfield(L, -2, "loadfile");
  lua_pop(L, 1);

  luaL_requiref(L, "coroutine", &luaopen_coroutine, 1); lua_pop(L, 1);
  luaL_requiref(L, "debug", &luaopen_debug, 1); lua_pop(L, 1);
  luaL_requiref(L, "math", &luaopen_math, 1); lua_pop(L, 1);
  luaL_requiref(L, "string", &luaopen_string, 1); lua_pop(L, 1);
  luaL_requiref(L, "table", &luaopen_table, 1); lua_pop(L, 1);
  luaL_requiref(L, "utf8", &luaopen_utf8, 1); lua_pop(L, 1);
}

static int _buf_writer(lua_State* L, const void* p, size_t size, void* ud) {
  luaL_addlstring((luaL_Buffer*)ud, (const char*) p, size);
  return 0;
}

static int _reload_stripped() {
  luaL_Buffer b;
  luaL_buffinit(L, &b);
  lua_dump(L, &_buf_writer, &b, 1);
  lua_pop(L, 1);
  int rc = luaL_loadbuffer(L, luaL_buffaddr(&b), luaL_bufflen(&b), NULL);
  luaL_pushresult(&b); lua_pop(L, 1);
  return rc;
}

static bool trusted = false;
static int is_trusted(lua_State* L) {
  lua_pushboolean(L, (int)trusted);
  return 1;
}

static char* castle_firmware_file = NULL;
static const luaL_Reg castle_funs[] = {
  {"is_trusted", &is_trusted},
  {"open", NULL},
  {NULL, NULL}
};
static int _open_castle(lua_State* L) {
  luaL_newlib(L, castle_funs);
  int rc = luaL_dofile(L, castle_firmware_file);
  if (rc != LUA_OK) {
    const char* err = lua_tostring(L, -1);
    fprintf(stderr, "failed load castle firmware: %s\n", err);
    return luaL_error(L, "failed load castle firmware: %s", err);
  }
  rc = _reload_stripped();
  if (rc != LUA_OK) {
    const char* err = lua_tostring(L, -1);
    fprintf(stderr, "failed strip castle firmware: %s\n", err);
    return luaL_error(L, "failed strip castle firmware: %s", err);
  }
  lua_pushcclosure(L, &is_trusted, 0);
  lua_call(L, 1, 1);
  luaL_checktype(L, -1, LUA_TFUNCTION);
  lua_setfield(L, -2, "open");
  return 1;
}

int main(int argc, char** argv) {
  char* input = NULL;

  int opt;
  while ((opt = getopt(argc, argv, "i:f:th")) != -1) {
    switch (opt) {
      case 'i':
        input = optarg;
        break;
      case 'f':
        castle_firmware_file = optarg;
        break;
      case 't':
        trusted = true;
        break;
      case 'h':
      default:
        fprintf(stderr, "Usage: %s <-f firmwarefile> [-i codefile] [--trusted]\n", argv[0]);
        exit(opt != 'h');
    }
  }

  if (!castle_firmware_file) {
    fputs("missing required argument: firmwarefile\n", stderr);
    exit(1);
  }

  L = lua_newstate(&_counting_alloc, NULL);
  atexit(&_lua_close);
  lua_setwarnf(L, &_warn, NULL);
  _init_lua();
  luaL_requiref(L, "castle", _open_castle, 1); lua_pop(L, 1);

  int rc = luaL_loadfile(L, input);
  switch (rc) {
    case LUA_OK:
      break;
    case LUA_ERRFILE:
      perror("failed load code");
      exit(1);
    case LUA_ERRSYNTAX:
      perror("invalid syntax");
      exit(1);
    case LUA_ERRMEM:
      perror("memory error");
      exit(1);
    default:
      perror("unknown error");
      exit(1);
  }


  rc = lua_pcall(L, 0, 0, 0);
  if (rc != LUA_OK) {
    const char* err = lua_tostring(L, -1);
    switch (rc) {
      case LUA_ERRRUN:
        fprintf(stderr, "runtime error: %s\n", err);
        break;
      case LUA_ERRMEM:
        fprintf(stderr, "memory error: %s\n", err);
        break;
      case LUA_ERRERR:
        fprintf(stderr, "error in error handler: %s\n", err);
        break;
      default:
        fprintf(stderr, "unknown error: %s\n", err);
        break;
    }
    exit(1);
  }

  return 0;
}
