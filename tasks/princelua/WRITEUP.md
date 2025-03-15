# Встроенный Принц: Write-up

Пока отложим в сторону сайт (на котором есть только форма для сдачи), и будем
смотреть на `[runner.c](app/runner/runner.c)`.

С виду это совершенно обычный код, который инициализирует Lua, загружает некую
прошивку и выполняет код пользователя. Первое, на что мы обратим внимание —
фукнция `_open_castle`:

```c
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
```

Отсюда мы узнаем два важных факта о библиотеке ЗВП:
- Есть функция `is_trusted`, которая возвращает, был ли передан флаг `-t`
- Прошивка, которая передаётся снаружи, — на самом деле функция, которая
  принимает `is_trusted` и возвращает другую функцию `open`.

У прошивки стираются отладочные символы, поэтому её исходники больше не будут нам доступны.

Цель очевидна: вызывать функцию `castle.open()`. Только при вызове
мы получаем ошибку про `untrusted mode`. Логично, не просто же так прошивка
принимает на вход `is_trusted`.

Сразу хочется сделать что-то вроде
`castle.is_trusted = function() return true end`. Однако это не сработает.

Направление мысли верное: мы хотим, чтобы `is_trusted` всегда возвращала
`true`, то есть поменять память программы. Каноническим способом делать это
всегда был отладчик.

В `_init_lua` нам подрезали `dofile` и `loadfile`, а библиотеки, работающие
с системой (`os`, `io`, `package`) вообще не подключили. Но нам оставили
библиотеку `debug`.

Немного прочитав про устройство Lua, мы узнаем две важные вещи:
- Есть локальные ячейки, которые можно модифицировать через `debug.getlocal`
  и `debug.setlocal` по номерам;
- Аргументы и возвращаемые значения у функций передаются через них.

План такой: перехватывать все возвращаемые значения и изменять
`false` на `true`. Тогда получится такой скрипт:

```lua
function hook()
  i = 1
  while true do
    name, value = debug.getlocal(2, i) -- пропускаем getlocal() and hook()
    if not name then break end -- out of bounds
    if value == false then
      debug.setlocal(2, i, true)
    end
    i = i + 1
  end
end

debug.sethook(hook, "r") -- добавляем наш хук только на событие return
                         -- из функции castle.open()
```

Запускаем — и нам выводится флаг.

Флаг: **ugra_princ3ss_1s_fre3d_by_y0u_1e0460fb**

## Что могло пойти не так?

Скрипт решения очень простой и довольно прямолинейный: он не пытается понять,
что это был именно вызов функции `is_trusted`. К примеру, у нас бы ничего не
получилось, если бы в прошивке была такая проверка:

```lua
function identity(arg) return not not arg end

if identity(false) then
  warn("Hack detected!")
  return
end
```

Чтобы чуть более точно определить, что это `is_trusted`, можно добавить две
проверки:
- При `call` количество аргументов 0, при `return` только одно значение `false`;
- Между `call` и `return` не было вызовов `line`, так как мы знаем, что
  `is_trusted` из C.

Однако здесь это всё не потребовалось.

## Непредусмотренное решение

Из Lua-кода была доступна функция `string.dump` — с её помощью можно получать
байткод функций. Достаточно было вызвать `string.dump(castle.open)` и
отправить результат в декомпилятор, а затем запустить то, что получилось —
это работало, так как в функции не было внешних зависимостей
(она [вычисляла хеш FNV-1a](./app/post.go#L24) от токена пользователя и соли).
