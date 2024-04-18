# Подсистема мониторинга уровня жидкости

Для определения наличия воды у основания бутылки, установленной на кулер, используется бесконтактный датчик уровня жидкости, подключённый к микроконтроллеру. Микроконтроллер реализует алгоритм считывания данных с датчика и отправки данных в серверную часть для последующей обработки и анализа.

## Бесконтактные датчики уровня жидкости

<details>
<summary>Принцип действия емкостных бесконтактных датчиков</summary>

Принцип действия ёмкостных бесконтактных датчиков основан на изменении электрической ёмкости конденсатора, в зону которого попадает объект. При подаче питания перед активной зоной датчика, представляющую собой поверхность «развёрнутого» конденсатора, возникает электрическое поле, которое является зоной чувствительности датчика. При попадании в эту зону какого-либо материала с диэлектрической проницаемостью больше единицы ёмкость конденсатора изменяется, и, соответственно, изменяется состояние выхода датчика.

<img src=".github\vb1_princzip_dejstviya.svg" alt="Принцип действия емкостных бесконтактных датчиков" width="500">

</details>

### Датчик `XKC-Y25-V`

Модель `XKC-Y25-V` (V: выходной интерфейс высокого и низкого уровня; [документация](http://pdf.sz-xkc.cn/?pdf-id=80&type=en)). Штатная длина кабеля 50 см, на конце кабеля находится разъём `XH2.54mm-4p`.

<details>
<summary>Описание и схема подключения датчика</summary>
<img src=".github\XKC-Y25-V_01.jpg" alt="Изображение датчика XKC-Y25-V" width="500">

<img src=".github\XKC-Y25-V_02.jpg" alt="Схема подключения датчика XKC-Y25-V" width="500">

#### Режимы работы

Выбор режима работы:
1. Когда черный провод не подключен (не заземлён, висит в воздухе), это положительный выход:
    - если жидкость обнаружена, транзистор отключается и выдает высокий уровень;
    - если жидкость не обнаружена, транзистор включается и выдает низкий уровень.
2. Когда черный провод заземлен (подключен к отрицательному полюсу источника питания 0 В), это обратный выход:
    - если жидкость обнаружена, транзистор включается и выдает низкий уровень;
    - если жидкость не обнаружена, транзистор отключается и выдает высокий уровень.

#### Примеры использования

- https://www.youtube.com/watch?v=9XhXjy4BPrs
- https://mysku.club/blog/aliexpress/56013.html ([исходный код](https://github.com/Gelezako/XKC-Y25-V/blob/master/water-sensor.ino))

</details>

### Датчик `XKC-Y21-NPN`

Модель `XKC-Y21-NPN` (NPN: активный уровень на выходе датчика – низкий (0В); [документация](http://pdf.sz-xkc.cn/?pdf-id=192&type=en)). Штатная длина кабеля 30 см, на конце кабеля находится разъём `XH2.54mm-3p`.

<details>
<summary>Описание и схема подключения датчика</summary>
<img src=".github\XKC-Y21-NPN_01.jpg" alt="Изображение датчика XKC-Y21-NPN" width="500">

<img src=".github\XKC-Y21-NPN_02.jpg" alt="Схема подключения датчика XKC-Y21-NPN" width="500">

Судя по схеме подключения (NPN: если жидкость обнаружена, то на выходе низкий уровень, если не обнаружена - выход не скоммутирован), необходимо использовать дополнительный резистор подтяжки к питанию.

<details>
  <summary>Выбор резистора подтяжки</summary>
  Резистор подтяжки нужен для того, чтобы вход не висел в воздухе и не наловил шумов. Подтягивают к земле или к питанию, чтобы потенциал всегда был определен, даже при отсутствии входного сигнала. Номинал подтягивающего резистора должен быть достаточно большим, обычно используются 5-10 кОм (см. [правила выбора номинала](https://kotyara12.ru/iot/i2c/). ESP32 работает с 3.3В, поэтому можно использовать 4.7 кОм. Судя по [документации](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html?highlight=pullup#pinmode) производителя микроконтроллера, у ESP32 часть GPIO уже имеет внутренние подтягивающие резисторы.
</details>
</details>

## Подготовка микроконтроллера

Датчик уровня жидкости подключается к отладочной плате `DOIT ESP32 DevKit V1` на базе микроконтроллера [ESP32-WROOM-32](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32_datasheet_en.pdf) (`ESP32-D0WDQ6, rev. v1.0`). Для разработки приложения для управления датчиком используется [MicroPython](https://www.micropython.org).

<details>
  <summary>Изображение и распиновка отладочной платы</summary>
  <img src="https://docs.espressif.com/projects/esp-idf/en/latest/esp32/_images/esp32-devkitc-functional-overview.jpg" alt="Изображение микроконтроллера" width="500">
  
  <img src=".github\DOIT_ESP32-WROOM-32_36pins_Pinout_01.jpg" alt="Распиновка микроконтроллера" width="500">
</details>

Подготовка микроконтроллера состоит из следующих этапов:
- подключение микроконтроллера к персональному компьютеру под управлением Windows 10;
- загрузка прошивки в микроконтроллер.

### Подключение микроконтроллера к персональному компьютеру

Для подключения микроконтроллера через USB порт и доступа к нему через виртуальный последовательный порт (`Virtual COM Port`, `VCP`) необходимо установить драйвер [USB to UART Bridge](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads) ([CP210x Windows Drivers](https://www.silabs.com/documents/public/software/CP210x_Windows_Drivers.zip)). Номер созданного VCP можно изменить  с помощью `Device Manager`, далее во всех примерах используется `COM1`.

<details>
  <summary>Скриншот окна Device Manager с выбранным VCP</summary>
  <img src="https://docs.espressif.com/projects/esp-idf/en/latest/esp32/_images/esp32-devkitc-in-device-manager.png" alt="Windows Device Manager" width="300">
</details>

### Загрузка прошивки в микроконтроллер

Загрузка прошивки в микроконтроллер выполняется с помощью утилиты [esptool.py](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/index.html). Эта утилита является приложением, разработанным на языке [Python](https://www.python.org/downloads/), поэтому сначала создадим [виртуальное окружение](https://docs.python.org/3/library/venv.html?highlight=venv#creating-virtual-environments), а затем установим в него приложение. В дальнешем это же виртуальное окружение использовать и для установки утилит MicroPython.

```PowerShell
> python -m venv .venv
> .\.venv\Scripts\Activate.ps1
```

```PowerShell
> python -m pip install esptool
```

Информацию о названии модели микроконтроллера, его аппаратных возможностях, MAC адресе и т.п. можно получить с помощью следующей команды.

```PowerShell
> esptool --port COM1 flash_id
```

По названию модели микроконтроллера на сайте [MicroPython](https://micropython.org/download) необходимо выбрать подходящую прошивку. Для `ESP32-WROOM-32` подходит прошивка [ESP32 / WROOM](https://micropython.org/download/ESP32_GENERIC), на момент написание этой инструкции последняя версия прошивки имеет номер [1.22.1](https://micropython.org/resources/firmware/ESP32_GENERIC-20240105-v1.22.1.bin).

Загрузка прошивки в контроллер выполняется с помощью приведённых далее команд. При выполнении второй команды необходимо перевести `ESP32-WROOM-32` в так называемый режим загрузки ([Firmware Download mode](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html#manual-bootloader)). Для этого необходимо нажать кнопку `Boot` и, удерживая её нажатой, нажать и отпустить кнопку `EN`, а затем отпустить и кнопку `Boot`.

```PowerShell
> esptool --chip esp32 --port COM1 erase_flash
> esptool --chip esp32 --port COM1 --baud 115200 write_flash -z 0x1000 ESP32_GENERIC-20240105-v1.22.1.bin
```

Тестирование загруженной прошивки можно выполнить с помощью следующих команд.

```PowerShell
> python -m serial.tools.list_ports
> python -m serial.tools.miniterm --raw COM1 115200
```

## Работа с микроконтроллером под управлением `MicroPython`

Основным инструментом для взаимодействия с `MicroPython` является `mpremote` - [MicroPython remote control](https://docs.micropython.org/en/latest/reference/mpremote.html). Установка `mpremote` выполняется следующим образом.

```PowerShell
> python -m pip install mpremote
```

Основные команды `mpremote` приведены ниже.

```PowerShell
> mpremote fs ls
> mpremote fs cp boot.py :
> mpremote fs cp boot.py main.py config.py :
> mpremote fs cat :boot.py
> mpremote run boot.py
> mpremote moint . repl
> mpremote soft-reset
```

Для команды `fs cp` действует следующее правило: двоеточие `:` указывает, что файл находится в файловой системе микроконтроллера.

Большой список инструментов для `MicroPython` приведён вот на сайте [Awesome MicroPython](https://awesome-micropython.com/).

## Особенности программирования микроконтроллера `ESP32-WROOM-32`/`DOIT ESP32 DevKit V1`

1. GPIO, у которых в названии есть префикс `ADC2`, нельзя использовать одновременно с Wi-Fi. Описание распиновки приведено в спецификации ([пример 1](https://dzen.ru/a/Y774Df-le2kG3b99), [пример 2](https://diytech.ru/projects/spravochnik-po-raspinovke-esp32-kakie-vyvody-gpio-sleduet-ispolzovat)).

## Примеры кода

### Работа с MQTT
https://www.donskytech.com/micropython-mqtt-esp32-esp8266/

### Работа с ёмкостными датчиками

#### Кнопка `TTP223`

https://github.com/mcauser/micropython-ttp223
https://kit.alexgyver.ru/tutorials/ttp223/
