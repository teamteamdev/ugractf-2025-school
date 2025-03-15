# Взлёт: Write-up

Переходим на страницу, указанную в задании. Нас встречает сайт-портфолио какого-то очень крутого хакера: здесь и фон из матрицы, и всякие [сомнительные достижения](https://hackerone.com/reports/180074).

Помимо них, владелец сайта оставил свои публичные SSH- и GPG-ключи: `id_ed25519.pub` и `public.pgp`.
Директорию `keys/` мы изучить не можем — выключена индексация. 

Однако, если мы заменим в адресе страницы `public.pgp` eа `private.pgp`, нас встретит приватный GPG-ключ. 
Проделаем то же самое с `id_ed25519` — и получим ещё и SSH-ключ.

Кроме ключей, на сайте нет никакой информации, которая могла бы нам помочь, даже зашифрованной ключом.
Вернёмся к `id_ed25519.pub` — в нём содержится ещё и комментарий к ключу: `ph4nt0m@cyb3ri4n.ru`.

Если мы сохраним к себе приватный ключ и попробуем подключиться по SSH к указанному хосту, нас встретит сообщение:

```shell
$ ssh ph4nt0m@cyb3ri4n.ru -i id_ed25519

Hello!

The server is unavailable.
Please contact the administrator.
Request id: ugra_dont_keep_your_keys_under_the_mat_fzlywupnvllhnrgo

Connection to cyb3ri4n.ru closed.
```

Флаг: **ugra_dont_keep_your_keys_under_the_mat_fzlywupnvllhnrgo**
