# Настоящая крипта: Write-up

Дана ссылка на blockchain explorer на адрес какого-то контракта. С ним ничего не происходило, никаких транзакций, а категория reverse намекает, что его нужно реверсить.

## Способ 1

Закидываем байткод контракта в декомпилятор [panoramix](https://github.com/palkeo/panoramix). Он выдаёт примерно следующее:
```python
# Palkeoramix decompiler. 

def _fallback(?) payable: # default function
  require not (Mask(16, 192, _param1) >> 16 or Mask(16, 160, _param1) << 32 or Mask(16, 144, _param1) >> 48 or Mask(16, 128, _param1) << 80 or Mask(16, 112, _param1) >> 80 or _param1 or Mask(16, 80, _param1) << 64 or Mask(16, 64, _param1) << 16 or Mask(16, 48, _param1) >> 32 or Mask(16, 32, _param1) << 208 or Mask(16, 16, _param1) << 144 or uint16(_param1) << 224 xor 0xd087f450a472071dad29898d9a036e7a755f80efa5f7146e1785f509e0741ecd) - 0xa2f59729c51c6842df50ece3e3731b1d073eed8ad1984b0d67f1865683017dbf
  revert
```

Другой [декомпилятор](https://ethervm.io/decompile) — с ethervm.io — выдаёт такое:
```js
contract Contract {
    function main() {
        var var0 = 0xd087f450a472071dad29898d9a036e7a755f80efa5f7146e1785f509e0741ecd;
        var var1 = 0xa2f59729c51c6842df50ece3e3731b1d073eed8ad1984b0d67f1865683017dbf;
        var var2 = var0;
        var var3 = 0x004d;
        var var4 = msg.data[0x44:0x64];
        var3 = func_0098(var4);
        var temp0 = var0;
        var0 = var3 ~ var2;
        var2 = temp0;
        var3 = 0x005a;
        var4 = msg.data[0x64:0x84];
        var3 = func_0098(var4);
        var temp1 = var0;
        var0 = var3 ~ var2;
    
        if (temp1 - var1) {
            // Unhandled termination
        } else if (0xb4f6853bd41a687adf50f1f9fc7331141a2bf28ed4804b0d67f18c568d1d66bd - var0) {
            // Unhandled termination
        } else {
            var0 = 0x01;
            // Unhandled termination
        }
    }
    
    function func_0098(var arg0) returns (var r0) {
        var temp0 = arg0;
        var temp1 = temp0 >> 0x70;
        return (temp1 & (0xffff << 0x80)) | // ((temp0 >> 0x70) & (0xffff << 0x80))
		       (temp1 & (0xffff << 0x70)) | // ((temp0 >> 0x70) & (0xffff << 0x70))
		       ((temp0 >> 0x90) & 0xffff0000000000000000) |
		       ((temp0 >> 0x10) & (0xffff << 0xb0)) |
		       ((temp0 >> 0x80) & 0xffff000000000000) |
		       ((temp0 << 0x20) & (0xffff << 0xc0)) |
		       ((temp0 >> 0x30) & 0xffff000000000000000000000000) |
		       ((temp0 << 0x50) & (0xffff << 0xd0)) |
		       ((temp0 >> 0x50) & 0xffff00000000) |
		       ((temp0 >> 0x60) & 0xffff) |
		       ((temp0 << 0x40) & (0xffff << 0x90)) |
		       ((temp0 << 0x10) & 0xffff00000000000000000000) |
		       ((temp0 >> 0x20) & 0xffff0000) |
		       ((temp0 << 0xd0) & (0xffff << 0xf0)) |
		       ((temp0 << 0x90) & (0xffff << 0xa0)) |
		       ((temp0 << 0xe0) & (0xffff << 0xe0));
    }
}
```

Оба они декомпилируют достаточно криво (например, ethervm не смог декомпилировать завершение работы контракта и почему-то записал XOR как `~` вместо привычного `^`, а panoramix полностью проигнорировал существование второго блока), но видно, что байты переданной в параметрах строки сначала перемешиваются парами по 2 байта, потом происходит XOR с константой и сравнение. Причём происходит это для двух «блоков» по 32 байта.

Преобразуем всё обратно:

```python
XORED_CT1 = bytes.fromhex('a2f59729c51c6842df50ece3e3731b1d073eed8ad1984b0d67f1865683017dbf')
XORED_CT2 = bytes.fromhex('b4f6853bd41a687adf50f1f9fc7331141a2bf28ed4804b0d67f18c568d1d66bd')
KEY = bytes.fromhex('d087f450a472071dad29898d9a036e7a755f80efa5f7146e1785f509e0741ecd')

def unshuffle_block(ct):
    cti = int.from_bytes(ct)

    ans = 0
    ans |= (cti & (0xffff << 0x80)) << 0x70
    ans |= (cti & (0xffff << 0x70)) << 0x70
    ans |= (cti & 0xffff0000000000000000) << 0x90
    ans |= (cti & (0xffff << 0xb0)) << 0x10
    ans |= (cti & 0xffff000000000000) << 0x80
    ans |= (cti & (0xffff << 0xc0)) >> 0x20
    ans |= (cti & 0xffff000000000000000000000000) << 0x30
    ans |= (cti & (0xffff << 0xd0)) >> 0x50
    ans |= (cti & 0xffff00000000) << 0x50
    ans |= (cti & 0xffff) << 0x60
    ans |= (cti & (0xffff << 0x90)) >> 0x40
    ans |= (cti & 0xffff00000000000000000000) >> 0x10
    ans |= (cti & 0xffff0000) << 0x20
    ans |= (cti & (0xffff << 0xf0)) >> 0xd0
    ans |= (cti & (0xffff << 0xa0)) >> 0x90
    ans |= (cti & (0xffff << 0xe0)) >> 0xe0
    
    return int.to_bytes(ans, 32).decode()

CT1 = bytes([k ^ c for k, c in zip(KEY, XORED_CT1)])
CT2 = bytes([k ^ c for k, c in zip(KEY, XORED_CT2)])

print(unshuffle_block(CT1) + unshuffle_block(CT2))
```

Получаем флаг.

## Способ 2

Находим аналог анализатора [angr](https://angr.io) для EVM — [greed](https://github.com/ucsb-seclab/greed). Установливается он не очень приятно, поэтому для простоты запустим контейнер `docker run -it python:bullseye` (важно, что именно `bullseye`: для некоторых зависимостей нужна библиотека `libffi7`, которой нет на последнем Debian).

Устанавливаем greed:

```bash
pip install virtualenvwrapper
source /usr/local/bin/virtualenvwrapper.sh 

mkvirtualenv greed
workon greed
git clone https://github.com/ucsb-seclab/greed
cd greed

# первая часть зависимостей greed
apt update
apt install cmake gperf mkisofs bison build-essential clang cmake doxygen flex mcpp libboost-all-dev time # да, time тоже нужен :)

# ещё одна зависимость greed
wget https://souffle-lang.github.io/ppa/souffle-key.public -O /usr/share/keyrings/souffle-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/souffle-archive-keyring.gpg] https://souffle-lang.github.io/ppa/ubuntu/ stable main" | tee /etc/apt/sources.list.d/souffle.list
apt update
apt install souffle

# запускаем установку
# ждать придётся очень долго
./setup.sh
```

Запускаем анализ байткода (ждать очень долго придётся ещё раз):

```bash
mkdir /task && cd /task
echo <bytecode> > contract.hex
analyze_hex.sh --file contract.hex
```

Открываем `contract.tac`, видим в конце основной функции три блока, которые как-то завершают выполнение контракта:
```
    Begin block 0x88
    prev=[0x62], succ=[]
    =================================
    0x88: v88(0x1) = CONST 
    0x8a: v8a(0x0) = CONST 
    0x8b: MSTORE v8a(0x0), v88(0x1)
    0x8c: v8c(0x20) = CONST 
    0x8e: v8e(0x0) = CONST 
    0x8f: RETURN v8e(0x0), v8c(0x20)

    Begin block 0x90
    prev=[0x62], succ=[]
    =================================
    0x91: v91(0x0) = CONST 
    0x93: REVERT v91(0x0), v91(0x0)

    Begin block 0x94
    prev=[0x5a], succ=[]
    =================================
    0x95: v95(0x0) = CONST 
    0x97: REVERT v95(0x0), v95(0x0)
```
Первый блок корректно завершает выполнение контракта и возвращает 1, а два других просто прерывают выполнение. Мы хотим, чтобы контракт завершился корректно, поэтому ищем через `greed` calldata, с которой выполнение доходит до этой инструкции:

```bash
# greed . --find 0x8f
INFO | greed | Found State 1 at 0x8f
INFO | greed | CALLDATA: 7272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272756772615f63727970746f5f6d65616e735f63727970746f63757272656e63795f6e6f745f63727970746f6772617068795f7870667071776d6964717874716b72727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272727272
```

Среди мусорных 0x72 находим байтовую строку `756772615f63727970746f5f6d65616e735f63727970746f63757272656e63795f6e6f745f63727970746f6772617068795f7870667071776d6964717874716b`, декодируем, получаем флаг.

Флаг: **ugra_crypto_means_cryptocurrency_not_cryptography_xpfpqwmidqxtqk**

Можно почитать [оригинальный контракт](Ugra.yul) (он написан на Yul, а не на Solidity с целью сделать таску не гробом).
