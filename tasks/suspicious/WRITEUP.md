# Подозрительный поток: Write-up

Открываем pcapng в wireshark и начинаем исследовать. В условии указано, что перехватить начало не удалось, значит, нужно смотреть на потоки, которые начались до захвата.

Откроем _Statistics_ → _Conversations_ и помедитируем.

![Conversations](./writeup/ipv4-conversations.avif)

В файле чуть больше двух тысяч пакетов. Наибольшее количество пакетов ушло на `135.181.93.68`, [`9.9.9.9`](https://quad9.net) и `45.43.14.223`. Между ними же (кроме `9.9.9.9`) было передано и наибольшее количество данных.

Посмотрим на каждый из этих потока (правый клик на строку в таблице, _Apply as Filter_, _Selected_, _Filter on stream id_).

* 9.9.9.9: честные DNS-запросы;
* 45.43.14.223: честные TLS-запросы;
* 135.181.93.68: какая-то муть — общение с портом 6666; все пакеты, кроме последнего, имеют длину 128; и в них передаётся что-то похожее на base64.

Снова жмём правую кнопку, _Follow_ → _TCP Stream_. Сохраняем в файлик, например `/tmp/meow` и идём смотреть, что происходит.

```shell
$ file /tmp/meow
/tmp/meow: ASCII text, with very long lines (44972), with no line terminators
$ echo $(( $(stat --format=%s /tmp/meow) % 4 ))
0
$ head -c 32 /tmp/meow
VTJ0V1ZXSkhhRzlVVmxaM1ZsWmFkR05G
$ tail -c 32 /tmp/meow
VmRXYms1U1lrWmFUMVZyVWtKUFVUMDk=
```

Звучит как base64-данные. Попробуем раскодировать:

```shell
$ base64 -d /tmp/meow >/tmp/meow2
$ echo $(( $(stat --format=%s /tmp/meow2) % 4 ))
0
$ head -c 32 /tmp/meow2
U2tWVWJHaG9UVlZ3VlZadGNFSmxSbGw1
$ tail -c 32 /tmp/meow2
Vmxaa2VrMVdWbk5SYkZaT1VrUkJPUT09
```

Снова base64? Хорошо, пробуем опять:

```shell
$ base64 -d /tmp/meow2 >/tmp/meow3
$ echo $(( $(stat --format=%s /tmp/meow3) % 4 ))
0
$ head -c 32 /tmp/meow3
SkVUbGhoTVVwVVZtcEJlRll5U2tWVWJH
$ tail -c 32 /tmp/meow3
ZGlXRkpVVlZkek1WVnNRbFZOUkRBOQ==
```

Может, всё сообщение много раз закодировано в base64?

```shell
$ solve() {
> current=$(cat /tmp/meow)
> while true; do
>     current=$(base64 -d <<<$current)
>     xxd -c 48 <<<$current | head -1
>     if (( $(wc -c <<<$current) < 100 )); then
>         break
>     fi
> done
> }
$ solve
00000000: 5532 7457 5657 4a48 6147 3955 566c 5a33 566c 5a61 6447 4e46 536d 7853 6247 7731 5654 4a30 5631 5a58 536b 6868 527a 6c56  U2tWVWJHaG9UVlZ3VlZadGNFSmxSbGw1VTJ0V1ZXSkhhRzlV
00000000: 536b 5655 6247 686f 5456 5677 5656 5a74 6345 4a6c 526c 6c35 5532 7457 5657 4a48 6147 3955 566c 5a33 566c 5a61 6447 4e46  SkVUbGhoTVVwVVZtcEJlRll5U2tWVWJHaG9UVlZ3VlZadGNF
00000000: 4a45 546c 6868 4d55 7055 566d 7042 6546 5979 536b 5655 6247 686f 5456 5677 5656 5a74 6345 4a6c 526c 6c35 5532 7457 5657  JETlhhMUpUVmpBeFYySkVUbGhoTVVwVVZtcEJlRll5U2tWVW
base64: invalid input
00000000: 2444 e586 1314 a545 66a4 1785 6324 a455 46c6 8684 d557 0555 66d7 0426 5465 9795 36b5 6556 2476 86f5 4565 6775 6565 a715  $D.....Ef...c$.UF....W.Uf..&Te..6.eV$v..Eeguee..
base64: invalid input
00000000: 0a                                                                                                                       .
```

«Неверный ввод»? Можно добиться его раскодировки, например, добавляя в начало букв `A`, обеспечивая длину, кратную 4, и исправляя последствия от ранее добавленных `A` (это будут по большей части нулевые байты, но иногда может проскочить и `=`, который нужно обработать отдельно). Пример реализации такого решения — в начале файла [`generator.py`](./generator.py).

```
$ SOLVE=1 python3 generator.py </tmp/meow
33728 b'U2tWVWJHaG9UVlZ3VlZadGNFSmxSbGw1VTJ0V1ZXSkhhRzlVVmxaM1ZsWmFkR05G'
25296 b'SkVUbGhoTVVwVVZtcEJlRll5U2tWVWJHaG9UVlZ3VlZadGNFSmxSbGw1VTJ0V1ZX'
18970 b'JETlhhMUpUVmpBeFYySkVUbGhoTVVwVVZtcEJlRll5U2tWVWJHaG9UVlZ3VlZacV'
14229 b'\x00\x02DNXa1JTVjAxV2JETlhhMUpUVmpBeFYySkVUbGhoTVVwVVZqQmFTMlJIVmtkWGJ'
10673 b'\x00\x00\x00\x003WkRSV01WbDNXa1JTVjAxV2JETlhhMUpUVjBaS2RHVkdXbFpOYWtFeFZtcEJ'
8006 b'\x00\x00\x00\x00\x007ZDRWMVl3WkRSV01WbDNXa1JTV0ZKdGVGWlZNakExVmpBeFYySkVUbGhoTW'
6004 b'\x00\x00\x00\x00\x00;d4V1YwZDRWMVl3WkRSWFJteFZVMjA1VjAxV2JETlhhMk0xVmpKS1IySkVU'
4503 b'\x00\x00\x00\x00\x07xWV0d4V1YwZDRXRmxVU205V01WbDNXa2M1VjJKR2JETlhhMXBQVmxVeFYyT'
3378 b'\x00\x00\x00\x00\x0cVWGxWV0d4WFlUSm9WMVl3Wkc5V2JGbDNXa1pPVlUxV2NIcFhhMXBQWVd4S2'
2533 b'\x00\x00\x00\x00\x00\x15XlVWGxXYTJoV1YwZG9WbFl3WkZOVU1WcHpXa1pPYWxKc1dqQlVWbU0xVmp'
1900 b'\x00\x00\x00\x00\x00\x00\x01yUXlWa2hWV0doVlYwZFNUMVpzWkZOalJsWjBUVmM1VjFKc2JETlhhMUpU'
1424 b'\x00\x00\x00\x00\x002QyVkhVWGhVV0dST1ZsZFNjRlZ0TVc5V1JsbDNXa1JTVjFKc2JETlhhMUpU'
1068 b'\x00\x00\x00\x03d2VHUXhUWGROVldScFVtMW9WRll3WkRSV1JsbDNXa1JTV0ZKdGVIbFhhMXBQ'
800 b'\x00\x00\x00weGQxTXdNVWRpUm1oVFYwZDRWRll3WkRSWFJteHlXa1pPYWxKc1dqQlVWbHBQ'
600 b'\x00\x000xd1MwMUdiRmhTV0d4VFYwZDRXRmxyWkZOalJsWjBUVlpPVmxac2JETldiWFF3'
448 b'\x00\r1wS01GbFhSWGxTV0d4WFlrZFNjRlZ0TVZOVlZsbDNWbXQwV0dKR1NsWlZNbmhQ'
336 b'\x00\rpKMFlXRXlSWGxXYkdScFVtMVNVVll3Vmt0WGJGSlZVMnhPYTAxWGVIbFhhMUpU'
252 b'\x00\nJ0YWEyRXlWbGRpUm1SUVYwVktXbFJVU2xOa01XeHlXa1JTWVdKVmNEQlVNVkpE'
188 b'\x00\x02taa2EyVldiRmRQV0VKWlRUSlNkMWxyWkRSYWJVcDBUMVJDV1UweFdqWlhiRmsx'
140 b'\x00\x0bZka2VWbFdPWEJZTTJSd1lrZDRabUp0T1RCWU0xWjZXbFk1YVZsWVRteE9hbEpt'
104 b'\x00\x06dkeVlWOXBYM2RwYkd4ZmJtOTBYM1Z6WlY5aVlYTmxOalJmWVhOZmNtRnVaRzl0'
76 b'\x00\x07dyYV9pX3dpbGxfbm90X3VzZV9iYXNlNjRfYXNfcmFuZG9tX3NvdXJjZV9uMzZm'
56 b'\x00\x07ra_i_will_not_use_base64_as_random_source_n36fznzg8r9a'
42 b'\x00\n\xda\x02 0\x8aY@\x9e\x8b@\xba\xc7\x80m\xab\x1e\xeb\x80\x1a\xb0\n\xda\x9d\xda&\x02\xca.\xad\xc7\x80\x9f~\x9f\xce|\xe0\xf2\xbfZ'
33 b'\x00\x00\x00\x00\x004\x01\x80\x00\x00\x00\x00\x02`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19'
27 b'\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
21 b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
18 b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
15 b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
12 b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
9 b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'
9 b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'
```

В строке 56 можно увидеть немного поломанный флаг. Восстанавливаем префикс `ugra_` и сдаём.

Флаг: **ugra_i_will_not_use_base64_as_random_source_n36fznzg8r9a**

Автоматическое решение с использованием `tshark`: [`solve.sh`](./solve.sh).

## base64, повторённый много раз? Где-то про это уже рассказывали…

Вообще [у base64 есть неподвижная точка](https://purplesyringa.moe/blog/ru/base64-has-a-fixed-point) (то есть текст, который при кодировании в base64 не изменится). Проведём эксперимент: возьмём строку `ugra_fake_flag`, прогоним её через base64 много раз (но не больше 30, а то может кончиться место на диске), разделим на куски по 128 байт (как пакеты в задании) и посмотрим на разницу между сообщением и полученными строками.

> Вместо строки `ugra_fake_flag` можно было бы взять достаточно любую строку, похожую на флаг — хоть `ugra_`.

```shell
$ cd $(mktemp -d)
$ echo ugra_fake_flag >0
$ for i in {1..30}; do
    base64 -w0 $(($i - 1)) > $i
    #      ^^^ выключаем переносы строк
done
$ compare() {
    Left=$1
    Right=$2
    shift 2
    diff -U3 <(fold -b -w128 "$Left") <(fold -b -w128 "$Right") "$@"
    #               ^^ отсчитывать 128 байт чуть быстрее, чем 128 символов
}
```

Вообще говоря,

$$\mathop{\mathrm{LCP}} \left\[ \mathop{\mathrm{base64}}\nolimits^N\enspace \texttt{"string-one"}, \enspace \mathop{\mathrm{base64}}\nolimits^N\enspace \texttt{"string-two"} \right\] \approx \mathop{\mathrm{base64}}\nolimits^N\enspace \texttt{"string-"},$$

и

$$\mathop{\mathrm{len}} \mathop{\mathrm{base64}}\nolimits^N\enspace Q \approx \left( \frac{4}{3} \right)^N \mathop{\mathrm{len}} Q,$$

то есть если было потеряно немного байт в начале, восстановить исходные данные целиком вполне возможно.

Теперь аккуратно посмотрим на диффы:

```shell
$ for i in {1..30}; do
    printf '\e]0;Comparing file `%d` with flag...\a' $i
    compare $i /tmp/meow --color=always | less
done
```

> Можно было бы сделать что-то на основе `diff -U3 --from-file=/tmp/meow {1..30}`, но такая команда кажется автору менее удобной.

Первые 18 файлов совсем непохожи, а начиная с 19-го, начинают просвечивать хоть какие-то совпадения. После некоторой медитации доходим до файла номер 23 и видим следующую картину:

```diff
--- /dev/fd/63  2025-04-12 23:41:59.144904774 +0300
+++ /dev/fd/62  2025-04-12 23:41:59.146904770 +0300
@@ -1,4 +1,3 @@
-Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSV01WbDNXa1JTVjAxV2JETlhhMUpUVmpBeFYySkVUbGhoTVVwVVZtcEJlRll5U2tWVWJHaG9UVlZ3VlZadGNFSmxSbGw1
 VTJ0V1ZXSkhhRzlVVmxaM1ZsWmFkR05GU214U2JHdzFWVEowVjFaWFNraGhSemxWVm14YU0xWnNXbUZrUjA1R1UyMTRVMkpIZHpGV1ZFb3dWakZhV0ZOcmFHaFNlbXhX
 Vm0xNFlVMHhXbk5YYlVacVZtdGFNRlZ0ZUZOVWJVcEdZMFZ3VjJKVVJYZFpWRVpyVTBaT2NscEhjRk5XUjNob1ZtMXdUMVV4U1hoalJscFlZbFZhY2xWcVFURlNNVlY1
 VFZSU1ZrMXJjRWxhU0hCSFZqRmFSbUl6WkZkaGExcG9WakJhVDJOdFJraGhSazVzWWxob1dGWnRNWGRVTVZGM1RVaG9hbEpzY0ZsWmJGWmhZMnhXY1ZGVVJsTk5XRUpI
@@ -29,84 +28,325 @@
 V1ZWV1UxWnJNWFZoUjJoYVpXdGFNMVZzV2xka1IwNUdUbFprVGxaWGQzcFdiWGhUVXpBeFNGSllhR0ZTVjJoVldXdGtiMkl4Vm5GUmJVWlhZa1p3TVZrd1dtdGhNa3BI
 WWtST1YwMXFWbEJXUkVwTFVtMU9TV05HYUdoTmJFbDZWMVphWVZReFNuTlVia3BwVW0xU1QxbHRlRXRsVm1SWlkwVmtWMkpXV2xoV1J6VlhWa2RLUjFOdVFsZGlSbkF6
 VmpGYVlWSXhiRFpTYld4T1ZqRktTVmRYZEc5U01WcElVbGhvYWxORk5WZFpiRkpIVmtaWmVXVkhkR3BpUm5CV1ZXMTRhMVJzV25WUmFscFlWa1ZLYUZacVJtdFNNV1Ix
-Vkd4U2FFMXRhRzlXVjNSWFdWWnNWMk5HV21GU1dGSlZWbTF6TVdWc2JGWmFSemxWWVhwR1Yxa3dXbXRXTWtwSVZHcFNWV0V5VWxOYVZscGhZMnh3UjFwR2FGTk5NbWcx
-Vm14a2QxRXhiRmhVYTJSWFlteEtjMVV3WkZOak1XeHlWMjVPVDFadVFsZFpWV1F3VjBaS2NtSkVUbGRpV0VKVVZqSnplRk5IUmtabFJtUk9ZbTFvYjFacVFtRldNazV6
-WTBWb1UySkhVbGhVVmxaM1ZXeGFjMXBJWkZSTlZXdzBWVEZvYzFVeVJYbGhTRUpXWWxoTmVGa3dXbk5XVmtaMVdrVTFhVkp1UVhkV1JscFRVVEZhY2sxV1drNVdSa3BZ
-Vm0weGIyVnNXblJOVlZwc1ZteGFlbFl5ZUhkaFZtUkhVMWh3V0Zac1dtaFdha3BUVTBaYWNsZHRkRk5OTUVwVlYxZDBiMUV3TlVkWGJGWlVWMGRTVUZacVFuZFRWbFY1
-WkVjNVYySlZjRWxhVldSdlZqSktTRlZyT1ZWV2JIQjZWbXBHWVZkWFJrZGhSazVwVW01Qk1sWXhXbGRaVjBWNFZXNU9XRmRIZUc5VmExWjNWMFpTVjFkdVpHaFNiRmt5
...
```

Пропущена первая строка, а следующие 28 (двадцать восемь!) совпадают. В последующих файлах такой прекрасной картины не наблюдается, но первая строка так и остаётся пропущенной, а вторая — совпадающей. Значит флаг был закодирован в base64 ровно 23 раза.

> **Почему такое хорошее совпадение только одно?** У строки — неподвижной точки base64 общий префикс с каждой строкой base64 короче, чем общий префикс base64 у двух строк с собственно общим префиксом. Это видно, если всматриваться.

Берём эту самую первую строку, докидываем в файл с флагом в начало и декодируем:

```shell
$ Flag=$(<<<"Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSV01WbDNXa1JTVjAxV2JETlhhMUpUVmpBeFYySkVUbGhoTVVwVVZtcEJlRll5U2tWVWJHaG9UVlZ3VlZadGNFSmxSbGw1" cat - /tmp/meow)
$ for i in {22..0}; do
    Flag=$(base64 -d <<<"$Flag")
    printf '%d\t%s\n' $i "$(head -c 100 <<<"$Flag")"
done
22      Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSV01WbDNXa1JTVjAxV2JETlhhMUpUVmpBeFYySkVUbGhoTVVwVVZtcEJlRll5U2tW
21      Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSV01WbDNXa1JTVjAxV2JETlhhMUpUVmpBeFYySkVUbGhoTVVwVVZtcEJlRll5U2tW
20      Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSV01WbDNXa1JTVjAxV2JETlhhMUpUVmpBeFYySkVUbGhoTVVwVVZtcEJlRll5U2tW
19      Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSV01WbDNXa1JTVjAxV2JETlhhMUpUVmpBeFYySkVUbGhoTVVwVVZqQmFTMlJIVmtk
18      Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSV01WbDNXa1JTVjAxV2JETlhhMUpUVjBaS2RHVkdXbFpOYWtFeFZtcEJlRll5U2tW
17      Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSV01WbDNXa1JTV0ZKdGVGWlZNakExVmpBeFYySkVUbGhoTWsweFZtcEtTMUl5U2tW
16      Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSWFJteFZVMjA1VjAxV2JETlhhMk0xVmpKS1IySkVUbGhoTVhCUVZteFZlRll5VGts
15      Vm0wd2QyUXlVWGxWV0d4V1YwZDRXRmxVU205V01WbDNXa2M1VjJKR2JETlhhMXBQVmxVeFYyTkljRmhoTVhCUVdWZDRTMk14WkhG
14      Vm0wd2QyUXlVWGxWV0d4WFlUSm9WMVl3Wkc5V2JGbDNXa1pPVlUxV2NIcFhhMXBQWVd4S2MxZHFRbFZXYlUweFZtcEdTMk15U2tW
13      Vm0wd2QyUXlVWGxXYTJoV1YwZG9WbFl3WkZOVU1WcHpXa1pPYWxKc1dqQlVWbU0xVmpGS2MySkVUbGhoTVVwVVZtcEdTMk15U2tW
12      Vm0wd2QyUXlWa2hWV0doVlYwZFNUMVpzWkZOalJsWjBUVmM1VjFKc2JETlhhMUpUVmpGS2MySkVUbGhoTVVwVVZqQmFTMlJIVmts
11      Vm0wd2QyVkhVWGhVV0dST1ZsZFNjRlZ0TVc5V1JsbDNXa1JTVjFKc2JETlhhMUpUVjBaS2RHVkliRmhoTVhCUVdWZDRTMk14WkhG
10      Vm0wd2VHUXhUWGROVldScFVtMW9WRll3WkRSV1JsbDNXa1JTV0ZKdGVIbFhhMXBQWVd4S2MxZHFRbFZXYkhCUVZtMTRZV015U2tW
9       Vm0weGQxTXdNVWRpUm1oVFYwZDRWRll3WkRSWFJteHlXa1pPYWxKc1dqQlVWbHBQVm14YWMySkVUbGRpV0ZGM1ZqQmtTMUl4VG5O
8       Vm0xd1MwMUdiRmhTV0d4VFYwZDRXRmxyWkZOalJsWjBUVlpPVmxac2JETldiWFF3VjBkS1IxTnNXbFpOYm1oUVdWUkJlRmRIVmts
7       Vm1wS01GbFhSWGxTV0d4WFlrZFNjRlZ0TVZOVlZsbDNWbXQwV0dKR1NsWlZNbmhQWVRBeFdHVkliRmhoTVVwVVYxWmtTMVp0VGtW
6       VmpKMFlXRXlSWGxXYkdScFVtMVNVVll3Vmt0WGJGSlZVMnhPYTAxWGVIbFhhMUpUV1ZkS1ZtTkVRbFZOVmtwRVZqRlZkMlZHWkhG
5       VjJ0YWEyRXlWbGRpUm1SUVYwVktXbFJVU2xOa01XeHlXa1JTWVdKVmNEQlVNVkpEVjFVd2VGZHFXbGhpUm1zeFdWWmFjMWRXVW5S
4       V2taa2EyVldiRmRQV0VKWlRUSlNkMWxyWkRSYWJVcDBUMVJDV1UweFdqWlhiRmsxWVZac1dWUnRlRTloYkVwdFYxWm9UMXB0VG5S
3       WkZka2VWbFdPWEJZTTJSd1lrZDRabUp0T1RCWU0xWjZXbFk1YVZsWVRteE9hbEptV1ZoT1ptTnRSblZhUnpsMFdETk9kbVJZU21w
2       ZFdkeVlWOXBYM2RwYkd4ZmJtOTBYM1Z6WlY5aVlYTmxOalJmWVhOZmNtRnVaRzl0WDNOdmRYSmpaVjl1TXpabWVtNTZaemh5T1dF
1       dWdyYV9pX3dpbGxfbm90X3VzZV9iYXNlNjRfYXNfcmFuZG9tX3NvdXJjZV9uMzZmem56ZzhyOWE=
0       ugra_i_will_not_use_base64_as_random_source_n36fznzg8r9a
```

Теперь флаг полностью восстановлен.

Флаг: **ugra_i_will_not_use_base64_as_random_source_n36fznzg8r9a**

## Не постмортем

В первой версии задания поток планировалось резать по 100 байт, а не по 128 — в таком случае можно было просто загуглить первый пакет и попасть на [ту самую статью в блоге](https://purplesyringa.moe/blog/ru/base64-has-a-fixed-point), откуда можно было достать начало. Чтобы сделать задание чуточку поинтереснее для тех, кто про это знает, а также по случайному стечению обстоятельств от этого решения было решено отказаться.

Первый вариант `.pcapng`-файла весил чуть меньше трёх гигабайт, поскольку за 12 минут на устройстве, с которого записывался дамп, успело раздаться достаточно много торрентов, никак не связанных с [соседней задачей](../leeching). От этого файла wireshark слишком сильно страдал, и трафик пришлось перезаписывать.

Флаг отправлялся [простеньким скриптом на расте](./sender.rs) на роутер с OpenWRT, наблюдение за чем производилось через ssh. В захваченном дампе пришлось вырезать постоянный ssh-трафик на роутер, десяток мегабайт трафика телеграма и некоторые другие вещи, которые сильно раздували дамп без лишней необходимости. Трафик на `45.43.14.223`, кстати, является трафиком Matrix.

Анонимизатор, который рандомизирует адреса в локальной сети и заменяет MAC-адреса, можно посмотреть в файле [`anonymize.py`](./anonymize.py).

Файл [`template.pcapng`](./template.pcapng), в который подставляется корректный флаг участника, содержит какой-то флаг, сгенерированный локально в процессе тестирования. Так что здесь не обязательно запускать генератор, если задание хочется кому-то показать. Флаг для этого файла: *ugra_i_will_not_use_base64_as_random_source_d2y4ybq1sxo3*.
