# AGU_micropython
A股 股票时刻关注
基于micropython esp32s2 st7789 显示日期 天气 及股票信息

## 基础
上传所有文件到你的esp32s2 即可（esp32s2的micropython版本不低于1.19）

## 硬件 接线
ST7789接线
|ST7789|ESP32s2|
|-|-|
|sda|10|
|sck|8|
|cs|2|
|dc|4|
|res|6|
|bl|1|

## 软件 创造
上传项目中的所有文件到你的ESP32S2（请先刷号mpy固件），修改main.py中的心知天气的API和需要显示城市的拼音

```
#心知天气API私钥请自行申请,城市拼音请自行设置
KEY="SFBgZ_NMzMaWbjrXW"
CITY="shanghai"
```

OK 大功告成，请按照LCD显示的信息操作即可。

