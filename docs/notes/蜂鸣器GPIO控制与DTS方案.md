# 蜂鸣器 GPIO 控制与 DTS 方案

> Status: `[SCHEMATIC]` + `[FACTORY-4.19]`；BSP 5.10 下仍需实机复核。  
> 目的：记录 GPIO 控制蜂鸣器的电路理解、DTS 建模建议和验证方法。

## 结论

蜂鸣器是一个典型的 **GPIO 控制开关量负载**。通常不需要单独写一个蜂鸣器专用内核驱动。

推荐在板级 DTS 中用通用 `gpio-leds` 建模，把蜂鸣器暴露到 `/sys/class/leds/buzzer/brightness`，由用户态写 `0/1` 控制。

## 电路理解

根据电路图，控制链路是：

```text
RK3568 GPIO3_B7
→ N-MOS gate
→ MOS 导通/截止
→ 蜂鸣器下端接地/断开
→ 蜂鸣器响/停
```

逻辑：

| GPIO 电平 | MOS 状态 | 蜂鸣器 |
|-----------|----------|--------|
| 高电平 `1` | 导通 | 响 |
| 低电平 `0` | 截止 | 停 |

因此它按 **GPIO_ACTIVE_HIGH** 处理。

## GPIO 编号校正

Rockchip 传统 sysfs GPIO 编号通常按：

```text
bank * 32 + group * 8 + pin
```

其中 A/B/C/D 分别是 0/1/2/3。

所以：

```text
GPIO3_B7 = 3 * 32 + 1 * 8 + 7 = 111
```

这与历史 FACTORY-4.19 / demo 测试中使用的 `gpio111` 对得上。

## 推荐 DTS：gpio-leds

在 BSP 5.10 板级 DTS 中可建模为：

```dts
/ {
    buzzer_ctrl: buzzer-ctrl {
        compatible = "gpio-leds";

        buzzer {
            label = "buzzer";
            gpios = <&gpio3 RK_PB7 GPIO_ACTIVE_HIGH>;
            linux,default-trigger = "none";
            default-state = "off";
        };
    };
};
```

如果需要显式 pinctrl，可加：

```dts
&pinctrl {
    buzzer {
        buzzer_pin: buzzer-pin {
            rockchip,pins = <3 RK_PB7 RK_FUNC_GPIO &pcfg_pull_none>;
        };
    };
};
```

并把节点改成：

```dts
buzzer_ctrl: buzzer-ctrl {
    compatible = "gpio-leds";
    pinctrl-names = "default";
    pinctrl-0 = <&buzzer_pin>;

    buzzer {
        label = "buzzer";
        gpios = <&gpio3 RK_PB7 GPIO_ACTIVE_HIGH>;
        linux,default-trigger = "none";
        default-state = "off";
    };
};
```

注意先 grep 当前 DTS，确认 `GPIO3_B7` 没被 UART/I2C/PWM/音频等其他 pinctrl 占用。

## 用户态验证

烧录新 DTB 后检查：

```bash
ls /sys/class/leds/
```

期望看到：

```text
buzzer
```

控制：

```bash
echo 1 > /sys/class/leds/buzzer/brightness
sleep 1
echo 0 > /sys/class/leds/buzzer/brightness
```

如果没有 `buzzer`，继续查：

```bash
dmesg | grep -iE 'gpio-led|buzzer|leds|gpio3'
cat /sys/kernel/debug/gpio | grep -iE 'buzzer|gpio-111|gpio111'
```

## 临时验证：sysfs GPIO

在尚未修改 DTS 前，可以先用旧 sysfs GPIO 接口直接验证电路是否能响。

```bash
# 1. 导出 GPIO 111
echo 111 > /sys/class/gpio/export

# 2. 设置为输出模式
echo out > /sys/class/gpio/gpio111/direction

# 3. 输出高电平 -> MOS 管导通 -> 蜂鸣器响
echo 1 > /sys/class/gpio/gpio111/value

# 4. 输出低电平 -> MOS 管截止 -> 蜂鸣器停
echo 0 > /sys/class/gpio/gpio111/value

# 5. 测试完后释放
echo 111 > /sys/class/gpio/unexport
```

如果 `echo 111 > /sys/class/gpio/export` 报 busy，通常说明这个 GPIO 已被内核里的其他驱动占用。此时先看：

```bash
cat /sys/kernel/debug/gpio | grep -iE 'gpio-111|spk|buzzer'
```

## 与旧 sysfs GPIO 方法的关系

历史测试中直接操作：

```bash
echo 111 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio111/direction
echo 1 > /sys/class/gpio/gpio111/value
echo 0 > /sys/class/gpio/gpio111/value
```

这是可用于早期验证的方式，但 sysfs GPIO 在新内核中属于旧接口。正式板级建模更推荐 `gpio-leds` 或 `libgpiod`。

## 暂不使用 pwm-beeper

当前电路看起来是普通 GPIO 驱动 MOS 管开关，不是 PWM 输出到无源蜂鸣器。因此不要优先使用 `pwm-beeper`。只有确认蜂鸣器是无源器件且引脚实际复用为 PWM 时，才考虑 `pwm-beeper`。
