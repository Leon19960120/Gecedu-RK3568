### 蜂鸣器

已确定蜂鸣器为以gpio111
首先手动导出

```bash
echo 111 > /sys/class/gpio/export
```

- 向内核的 GPIO 导出文件写入数字 `111`，表示将 **GPIO 111** 的控制权从内核空间导出到用户空间。

- 执行成功后，系统会在 `/sys/class/gpio/` 目录下创建 `gpio111/` 子目录，其中包含 `direction`、`value` 等文件，允许用户通过读写这些文件来操作该 GPIO。

 ```bash
  echo out > /sys/class/gpio/gpio111/direction
 ```

将 GPIO 111 的方向设置为 **输出模式** (`out`)。

只有设置为输出模式后，才能向 `value` 文件写入 0 或 1 来控制电平。

```bash
# 蜂鸣器常响（假设高电平有效）
echo 1 > /sys/class/gpio/gpio111/value
```

向 GPIO 120 的 value 文件写入 1，即把该引脚输出高电平（通常为 3.3V 或 1.8V）。

按照注释“蜂鸣器常响（假设高电平有效）”，这里本意是让蜂鸣器开始响。

```bash
sleep 1
# 蜂鸣器不响（假设高电平有效）
echo 0 > /sys/class/gpio/gpio111/value
```

## LED测试

```bash
echo 120 > /sys/class/gpio/export
echo 121 > /sys/class/gpio/export
echo 123 > /sys/class/gpio/export
echo 124 > /sys/class/gpio/export
```

```shell
# 以 gpio120 为例
echo out > /sys/class/gpio/gpio120/direction
# 点亮（假设高电平有效）
echo 1 > /sys/class/gpio/gpio120/value
sleep 1
echo 0 > /sys/class/gpio/gpio120/value
```



## 🖥️ 背光设备（屏幕）

你之前还看到 `/sys/class/backlight/backlight/brightness`，它可以控制屏幕背光或某个可调光 LED：

```bash
# 查看最大亮度
cat /sys/class/backlight/backlight/max_brightness
# 设置亮度（例如 255）
echo 255 > /sys/class/backlight/backlight/brightness
# 熄灭
echo 0 > /sys/class/backlight/backlight/brightness
```

观察板子上是否有变化（可能是 LCD 背光）。




```bash
[root@RK356X:/sys/class/gpio]# cat /sys/kernel/debug/gpio
gpiochip0: GPIOs 0-31, parent: platform/fdd60000.gpio, gpio0:
 gpio-6   (                    |vcc5v0_otg          ) out lo
 gpio-23  (                    |vcc3v3_lcd0_n       ) out hi
 gpio-29  (                    |vcc3v3_vga          ) out hi

gpiochip1: GPIOs 32-63, parent: platform/fe740000.gpio, gpio1:
 gpio-40  (                    |GPIO Key UP         ) in  hi
 gpio-42  (                    |GPIO Key DOWN       ) in  hi

gpiochip2: GPIOs 64-95, parent: platform/fe750000.gpio, gpio2:
 gpio-73  (                    |bt_default_rts      ) in  hi
 gpio-79  (                    |bt_default_reset    ) out lo
 gpio-80  (                    |bt_default_wake_host) in  hi
 gpio-82  (                    |bt_default_wake     ) in  lo
 gpio-84  (                    |reset               ) out hi
 gpio-94  (                    |reset               ) out lo

gpiochip3: GPIOs 96-127, parent: platform/fe760000.gpio, gpio3:
 gpio-98  (                    |spk-ctl             ) out lo
 gpio-100 (                    |vcc3v3_pcie         ) out hi
 gpio-103 (                    |reset               ) out hi
 gpio-109 (                    |mdio-reset          ) out hi
 gpio-111 (                    |sysfs               ) out lo
 gpio-114 (                    |Headphone detection ) in  lo

gpiochip4: GPIOs 128-159, parent: platform/fe770000.gpio, gpio4:
```

 粤嵌RK3568 开发板上有配备 6个按键。其中 4 个按键是用 ADC0 模拟，按键按下去 ADC0 有不同的电压变化。  

在开发板串口终端下运行以下命令进行测试，然后输入数字“7”，因为按键事件为 event7。如需要停止测试按 Ctrl + c。 请按下开发板上的以上四个键，请不要按到其他键，如复位键 REST等。



```
~ # evtest
No device specified, trying to scan all of /dev/input/event*
Available devices:
/dev/input/event0:      gpio_keys_polled
/dev/input/event1:      fe6f0030.pwm
/dev/input/event2:      rk805 pwrkey
/dev/input/event3:      adc-keys
/dev/input/event4:      rockchip,rk809-codec Headphones
/dev/input/event5:      rockchip,hdmi rockchip,hdmi
/dev/input/event6:      Goodix Capacitive TouchScreen
Select the device event number [0-6]: 
```



运行结果如下所示，可以看到按对应的按键就会打印对应的按键类型和按下时值为 1，松开即为

```bash
[root@RK356X:/sys/class/gpio]# ls /dev/input
by-path  event0  event1  event2  event3  event4  event5

```



## 按键测试

```bash
[root@RK356X:/sys/class/gpio]#  evtest /dev/input/event0
Input driver version is 1.0.1
Input device ID: bus 0x19 vendor 0x1 product 0x1 version 0x100
Input device name: "gpio_keys_polled"
Supported events:
  Event type 0 (EV_SYN)
  Event type 1 (EV_KEY)
    Event code 103 (KEY_UP)
    Event code 108 (KEY_DOWN)
Key repeat handling:
  Repeat type 20 (EV_REP)
    Repeat code 0 (REP_DELAY)
      Value    250
    Repeat code 1 (REP_PERIOD)
      Value     33
Properties:
Testing ... (interrupt to exit)
Event: time 1777906431.204591, type 1 (EV_KEY), code 108 (KEY_DOWN), value 1
Event: time 1777906431.204591, -------------- SYN_REPORT ------------
Event: time 1777906431.411026, type 1 (EV_KEY), code 108 (KEY_DOWN), value 0
Event: time 1777906431.411026, -------------- SYN_REPORT ------------
Event: time 1777906432.341233, type 1 (EV_KEY), code 103 (KEY_UP), value 1
Event: time 1777906432.341233, -------------- SYN_REPORT ------------
Event: time 1777906432.547670, type 1 (EV_KEY), code 103 (KEY_UP), value 0
Event: time 1777906432.547670, -------------- SYN_REPORT ------------
```

