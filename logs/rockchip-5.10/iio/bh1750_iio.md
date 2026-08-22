# BSP 5.10 BH1750 光照传感器证据

状态：`[BSP-5.10 RUNTIME VERIFIED]`

## 结论

BH1750 在 I2C2 `0x23` 正常 probe，IIO 注册为 `iio:device2`，读数随手遮挡/光照明显变化，功能正常。此前一度误判为「设备消失」，实际是只看 grep 过滤过的 boot log 所致，设备一直存在。

## DTS 节点

```dts
// rk3568-gec-v11.dtsi
&i2c2 {
    status = "okay";
    pinctrl-0 = <&i2c2m1_xfer>;

    bh1750@23 {
        compatible = "rohm,bh1750";
        reg = <0x23>;
        status = "okay";
    };
};
```

## 板端证据

`i2cdetect -y 2`（0x23 = `UU`，表示设备存在且被驱动占用）：

```text
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- UU -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: UU -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- UU -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

sysfs：

```text
cat /sys/bus/i2c/devices/2-0023/name
→ bh1750

ls /sys/bus/iio/devices/iio:device2/
→ dev  in_illuminance_integration_time  in_illuminance_raw
  in_illuminance_scale  integration_time_available  name  of_node  power
  subsystem  uevent
```

## 实测读数（raw × scale = lux）

`in_illuminance_scale` = `0.833333`：

```text
raw=88   → 73.3 lux   （正常环境光）
raw=18   → 15  lux    （手遮传感器）
raw=117  → 97.5 lux   （恢复光照）
```

raw 随手遮挡/光照明显变化（18 → 117），确认真实采集照度。

## 规则

1. 判断「设备是否 probe」以板端实况为准（`i2cdetect` + `/sys/bus/i2c/devices/`），不要只看 grep 过滤过的 boot log——日志可能被截断，某条 probe 行没显示 ≠ 设备消失。
2. IIO 属性名以驱动源码为准：BH1750 是 `in_illuminance_raw`（不是 `in_illuminance_input`），读值前先 `ls` 确认。
