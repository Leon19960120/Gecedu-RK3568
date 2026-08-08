 粤嵌RK3568 开发板上有配备 6个按键。其中 4 个按键是用 ADC0 模拟，按键按下去 ADC0 有不同的电压变化。  

在开发板串口终端下运行以下命令进行测试，然后输入数字“7”，因为按键事件为 event7。如需要停止测试按 Ctrl + c。 请按下开发板上的以上四个键，请不要按到其他键，如复位键 REST等。



```
evtest
```



运行结果如下所示，可以看到按对应的按键就会打印对应的按键类型和按下时值为 1，松开即为

```bash
[root@RK356X:/sys/class/gpio]# ls /dev/input
by-path  event0  event1  event2  event3  event4  event5

```

```bash
 evtest /dev/input/event0
```

//读取ADC按键

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

