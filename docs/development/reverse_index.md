# 反编译索引：rk356x-demo_good_board_backup

总函数数：**555**，已全部反编译为伪 C（见 `decompiled_rk356x-demo.c`）

## main 函数（程序入口 / 总调度）

- **FUN_00105f70 @ 00105f70**
- 该函数内直接调用的子函数（FUN_ 形式，标注已知测试项）：

  - `FUN_00105520`
  - `FUN_00105e78`
  - `FUN_00105f70`
  - `FUN_00106a50`

## 测试项 -> 函数 映射表

| 测试项 | 函数名 | 地址 |
|---|---|---|
| RTC Test | `FUN_00105f70` | 00105f70 |
| IO Test | `FUN_00105f70` | 00105f70 |
| BT Test | `FUN_00105f70` | 00105f70 |
| ping | `FUN_0010731c` | 0010731c |
| ping | `FUN_00107320` | 00107320 |
| ping | `FUN_0010baa0` | 0010baa0 |
| ping | `FUN_0010c0e0` | 0010c0e0 |
| SIM Test | `FUN_0010c3a4` | 0010c3a4 |
| SIM Test | `FUN_0010c3a8` | 0010c3a8 |
| ping | `FUN_0010c770` | 0010c770 |
| ping | `FUN_0010cccc` | 0010cccc |
| ping | `FUN_0010ccd0` | 0010ccd0 |

## 含可读字符串的业务函数（已排除纯 libc/liblvgl 跳板）

共 **107** 个，这些是业务逻辑所在。

| 函数 | 地址 | 关键字符串（节选） |
|---|---|---|
| `FUN_001050c0` | 001050c0 | LV_HOR_RES_MAX=%d, LV_VER_RES_MAX=%d\n |
| `FUN_00105684` | 00105684 | %dx%d, %dbpp\n / /dev/fb0 / Error reading fixed information / Error reading variable information / Error: cannot open framebuffer device / Error: failed to map framebuffer device to memory |
| `fbdev_init` | 00105688 | %dx%d, %dbpp\n / /dev/fb0 / Error reading fixed information / Error reading variable information / Error: cannot open framebuffer device / Error: failed to map framebuffer device to memory |
| `FUN_00105abc` | 00105abc | /dev/input/event6 / unable open evdev interface: |
| `evdev_init` | 00105ac0 | /dev/input/event6 / unable open evdev interface: |
| `evdev_set_file` | 00105b20 | unable open evdev interface: |
| `FUN_00105e74` | 00105e74 | btn index: %d, text: %s\n |
| `FUN_00105e78` | 00105e78 | btn index: %d, text: %s\n |
| `FUN_00105f70` | 00105f70 | BT Test / IO Test / RTC Test / rk356x demo |
| `FUN_00106904` | 00106904 | hwclock -w |
| `FUN_00106908` | 00106908 | hwclock -w |
| `FUN_001069ac` | 001069ac | hwclock -w |
| `FUN_001069b0` | 001069b0 | hwclock -w |
| `FUN_00106a4c` | 00106a4c | 01\n02\n03\n04\n05\n06\n07\n08\n09\n10\n11\n12 / Adjust Date / Adjust Time / Minute / Month / Second |
| `FUN_00106a50` | 00106a50 | 01\n02\n03\n04\n05\n06\n07\n08\n09\n10\n11\n12 / Adjust Date / Adjust Time / Minute / Month / Second |
| `FUN_0010731c` | 0010731c | /dev/input/event0 / obj->index: %d, act=%d\n / ping 8.8.8.8 -c 1 |
| `FUN_00107320` | 00107320 | /dev/input/event0 / obj->index: %d, act=%d\n / ping 8.8.8.8 -c 1 |
| `FUN_00107414` | 00107414 | /sys/class/gpio/export / /sys/class/gpio/gpio120/direction / /sys/class/gpio/gpio121/direction / /sys/class/gpio/gpio123/direction / /sys/class/gpio/gpio124/direction / LED %d |
| `FUN_00107418` | 00107418 | /sys/class/gpio/export / /sys/class/gpio/gpio120/direction / /sys/class/gpio/gpio121/direction / /sys/class/gpio/gpio123/direction / /sys/class/gpio/gpio124/direction / LED %d |
| `FUN_001077bc` | 001077bc | /sys/class/gpio/gpio111/value |
| `FUN_001077c0` | 001077c0 | /sys/class/gpio/gpio111/value |
| `FUN_00107818` | 00107818 | /sys/class/gpio/gpio111/value |
| `FUN_00107870` | 00107870 | /sys/class/gpio/export / /sys/class/gpio/gpio111/direction / /sys/class/gpio/gpio111/value / Beep . . . |
| `FUN_00107ae4` | 00107ae4 | slider value: %d\n |
| `FUN_00107ae8` | 00107ae8 | slider value: %d\n |
| `FUN_00107bd4` | 00107bd4 | /sys/class/backlight/backlight/brightness / brightness: %s\n |
| `FUN_00107bd8` | 00107bd8 | /sys/class/backlight/backlight/brightness / brightness: %s\n |
| `FUN_00107e10` | 00107e10 | /dev/input/event0 / /dev/input/event3 / ADC Key: version: %d.%d.%d, name: %s\n / IO Key: version: %d.%d.%d, name: %s\n |
| `FUN_001083e4` | 001083e4 | /sys/bus/iio/devices/iio:device2/in_illuminance_raw |
| `FUN_001083e8` | 001083e8 | /sys/bus/iio/devices/iio:device2/in_illuminance_raw |
| `FUN_00108744` | 00108744 | /sys/bus/iio/devices/iio:device0/in_voltage6_raw |
| `FUN_00108748` | 00108748 | /sys/bus/iio/devices/iio:device0/in_voltage6_raw |
| `FUN_00108c10` | 00108c10 | Acceleration: / Angular: / X-raw: / Y-raw: / Z-raw: |
| `FUN_001090c4` | 001090c4 | %d |
| `FUN_001090c8` | 001090c8 | %d |
| `FUN_001091a4` | 001091a4 | /tmp/demo.wav / amixer cset numid=3 0 / amixer cset numid=3 1 / arecord -d 10 -f cd -r 44100 -c 2 -t wav %s |
| `FUN_001091a8` | 001091a8 | /tmp/demo.wav / amixer cset numid=3 0 / amixer cset numid=3 1 / arecord -d 10 -f cd -r 44100 -c 2 -t wav %s |
| `FUN_001091fc` | 001091fc | play %s |
| `FUN_00109200` | 00109200 | play %s |
| `FUN_00109238` | 00109238 | /oem/piano2-CoolEdit.mp3 / /tmp/demo.wav / obj->index: %d\n |
| `FUN_001094e4` | 001094e4 | /dev/input/event6 / Event: / unable open evdev interface: |
| `FUN_001094e8` | 001094e8 | /dev/input/event6 / Event: / unable open evdev interface: |
| `FUN_001099a8` | 001099a8 | %.2fG / %.2fK / %.2fM / %ld / %s/%s / );

      if ((iVar2 == 0) || (iVar2 = strcmp(pcVar4, |
| `FUN_00109c44` | 00109c44 | obj->index: %d\n |
| `FUN_00109c48` | 00109c48 | obj->index: %d\n |
| `FUN_00109db4` | 00109db4 | Explorer: [/udisk] / Refresh |
| `FUN_00109db8` | 00109db8 | Explorer: [/udisk] / Refresh |
| `FUN_0010a170` | 0010a170 | %.2fG / %.2fK / %.2fM / %ld / %s/%s / );

      if ((iVar2 == 0) || (iVar2 = strcmp(pcVar4, |
| `FUN_0010a40c` | 0010a40c | obj->index: %d\n |
| `FUN_0010a410` | 0010a410 | obj->index: %d\n |
| `FUN_0010a57c` | 0010a57c | Explorer: [/sdcard] / Refresh |
| `FUN_0010a580` | 0010a580 | Explorer: [/sdcard] / Refresh |
| `FUN_0010a94c` | 0010a94c | Can not open %s!\n / Receive fail. / Write to comm_port fail. / cfsetispeed fail / cfsetospeed fail |
| `FUN_0010a950` | 0010a950 | Can not open %s!\n / Receive fail. / Write to comm_port fail. / cfsetispeed fail / cfsetospeed fail |
| `FUN_0010ab58` | 0010ab58 | obj->index: %d\n |
| `FUN_0010ab88` | 0010ab88 | /dev/ttyS0\n/dev/ttyS1\n/dev/ttyS3\n/dev/ttyS4 / 1234567890\nabcdefghij / Device: / Receive: / Send & Receive / Send: |
| `FUN_0010b050` | 0010b050 | Send Error frame\n! / obj->index: %d\n |
| `FUN_0010b138` | 0010b138 | %02X  |
| `FUN_0010b1c8` | 0010b1c8 | %02X  / ID: 0x%X, DLC: %d\n / ID=0x%X DLC=%d data: \n |
| `FUN_0010b2e0` | 0010b2e0 | );

  system( / 01 02 03 04 05 06 07 08 / Device: / Generate / Receive: / Send: |
| `FUN_0010b9cc` | 0010b9cc | );

  __stream = popen( / );

  system( / \nWait connect . . . \n\n / obj->index: %d\n |
| `FUN_0010b9d0` | 0010b9d0 | );

  __stream = popen( / );

  system( / \nWait connect . . . \n\n / obj->index: %d\n |
| `FUN_0010baa0` | 0010baa0 | bytes from / ping %s -c 1 |
| `FUN_0010bb5c` | 0010bb5c | Start |
| `FUN_0010bb60` | 0010bb60 | Start |
| `FUN_0010bdd8` | 0010bdd8 | ifconfig eth0 down |
| `FUN_0010be10` | 0010be10 |  dev /  metric / \nIP: %s\nGATE: %s\n\n / default via  / gate: len=%d, gate=%s\n / ip route show |
| `FUN_0010c004` | 0010c004 | );

  sleep(4);

  __stream = popen( / );

  system( / \nWait connect . . . \n\n / obj->index: %d\n |
| `FUN_0010c008` | 0010c008 | );

  sleep(4);

  __stream = popen( / );

  system( / \nWait connect . . . \n\n / obj->index: %d\n |
| `FUN_0010c0e0` | 0010c0e0 | bytes from |
| `FUN_0010c19c` | 0010c19c | /dev/ttyUSB2 / AT+CIMI\r / Can not open %s!\n / OK / Write to comm_port fail. / cfsetispeed fail |
| `FUN_0010c1a0` | 0010c1a0 | /dev/ttyUSB2 / AT+CIMI\r / Can not open %s!\n / OK / Write to comm_port fail. / cfsetispeed fail |
| `FUN_0010c3a4` | 0010c3a4 | SIM Test / Start / ifconfig eth0 down / ifconfig wlan0 down |
| `FUN_0010c3a8` | 0010c3a8 | SIM Test / Start / ifconfig eth0 down / ifconfig wlan0 down |
| `FUN_0010c738` | 0010c738 | killall pppd |
| `FUN_0010c770` | 0010c770 | %31s dev %*s proto kernel scope link src %31s / Test ping \'8.8.8.8\'\n / \nIP: %s\nGATE: %s\n\n / ip route show / proto kernel scope link src |
| `FUN_0010c8c8` | 0010c8c8 | %31s %*s %31s %255s %31[^\n]s / );

  printf( / ifconfig wlan0 down / ifconfig wlan0 up / killall wpa_supplicant / obj->index: %d\n |
| `FUN_0010ca7c` | 0010ca7c | obj->index: %d\n / wifi_start.sh \'%s\' \'%s\' |
| `FUN_0010ca80` | 0010ca80 | obj->index: %d\n / wifi_start.sh \'%s\' \'%s\' |
| `FUN_0010cccc` | 0010cccc | bytes from / ping %s -c 1 |
| `FUN_0010ccd0` | 0010ccd0 | bytes from / ping %s -c 1 |
| `FUN_0010cd8c` | 0010cd8c | Connect / ifconfig eth0 down / password: / signal / ssid: |
| `FUN_0010cd90` | 0010cd90 | Connect / ifconfig eth0 down / password: / signal / ssid: |
| `FUN_0010d444` | 0010d444 | ifconfig wlan0 down / killall wpa_supplicant |
| `FUN_0010d448` | 0010d448 | ifconfig wlan0 down / killall wpa_supplicant |
| `FUN_0010d48c` | 0010d48c |  dev /  metric / \nIP: %s\nGATE: %s\n\n / default via  / gate: len=%d, gate=%s\n / ip route show |
| `FUN_0010d490` | 0010d490 |  dev /  metric / \nIP: %s\nGATE: %s\n\n / default via  / gate: len=%d, gate=%s\n / ip route show |
| `FUN_0010d684` | 0010d684 | /usr/libexec/bluetooth/bluetoothd --compat -n  & / \nBT Audio ready.\n / bluealsa --profile=a2dp-sink & / bluealsa-aplay --profile-a2dp 00:00:00:00:00:00 & / echo 0 > /sys/class/rfkill/rfkill0/state / echo 1 > /sys/class/rfkill/rfkill0/state |
| `FUN_0010d688` | 0010d688 | /usr/libexec/bluetooth/bluetoothd --compat -n  & / \nBT Audio ready.\n / bluealsa --profile=a2dp-sink & / bluealsa-aplay --profile-a2dp 00:00:00:00:00:00 & / echo 0 > /sys/class/rfkill/rfkill0/state / echo 1 > /sys/class/rfkill/rfkill0/state |
| `FUN_0010d7e8` | 0010d7e8 | Enable BT Audio |
| `FUN_0010daa0` | 0010daa0 | %02X  / );

  __fd = open( |
| `FUN_0010db50` | 0010db50 | %02X  |
| `FUN_0010dbe8` | 0010dbe8 | /sys/devices/platform/fe5b0000.i2c/i2c-2/2-0050/eeprom / obj->index: %d\n |
| `FUN_0010dc50` | 0010dc50 | %02X  / Generate / Read: / Write / Write: |
| `FUN_0010e2b8` | 0010e2b8 | %s/%s / );

  tcflush(iVar2,2);

  sVar7 = write(iVar2, / ,7);

  if (sVar7 < 7) {

    puts( / /dev/serial/by-id / Can not open %s!\n / Receive fail. |
| `FUN_0010e53c` | 0010e53c | );

  FUN_0010e2b8();

  iVar1 = printf( |
| `FUN_0010e540` | 0010e540 | );

  FUN_0010e2b8();

  iVar1 = printf( |
| `FUN_0010e584` | 0010e584 | Test |
| `FUN_0010e588` | 0010e588 | Test |
| `FUN_0010e7ec` | 0010e7ec | ifconfig eth0 down |
| `FUN_0010e7f0` | 0010e7f0 | ifconfig eth0 down |
| `FUN_0010e8d4` | 0010e8d4 | killall gst-launch-1.0 |
| `FUN_0010e8d8` | 0010e8d8 | killall gst-launch-1.0 |
| `FUN_0010e910` | 0010e910 | /sys/class/gpio/gpio%d/value / echo 0 > /sys/class/gpio/gpio%d/value / echo 1 > /sys/class/gpio/gpio%d/value / echo in > /sys/class/gpio/gpio%d/direction / echo out > /sys/class/gpio/gpio%d/direction |
| `FUN_0010ebe8` | 0010ebe8 | /sys/bus/iio/devices/iio:device0/in_voltage2_raw / /sys/bus/iio/devices/iio:device0/in_voltage3_raw / IO TEST / SARADC_VIN / SARADC_VIN2 / SARADC_VIN3 |
| `FUN_0010f0ec` | 0010f0ec | echo %d > /sys/class/gpio/unexport |
| `FUN_0010f0f0` | 0010f0f0 | echo %d > /sys/class/gpio/unexport |
