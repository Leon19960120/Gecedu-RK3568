# 03 - 按键 / 电源键 / ADC 旋钮测试

> 状态：混合证据。本页记录当前项目理解，并避免把 `eventX` 写死，因为 input probe 顺序变化时编号会跟着变。

## 板载输入概览

按硬件手册口径，GEC RK3568 板上一共有六个物理按键：

| 控件 | Linux 视角 | 状态 |
|------|------------|------|
| GPIO Key UP | `gpio_keys_polled`，`KEY_UP` | `[FACTORY-4.19]` / BSP 5.10 需复核 |
| GPIO Key DOWN | `gpio_keys_polled`，`KEY_DOWN` | `[FACTORY-4.19]` / BSP 5.10 需复核 |
| ADC key 1 | `adc-keys`，通常映射为音量键 | `[FACTORY-4.19]` / BSP 5.10 需复核 |
| ADC key 2 | `adc-keys`，通常映射为音量键 | `[FACTORY-4.19]` / BSP 5.10 需复核 |
| POWER ON | RK809 PMIC input，Linux name 为 `rk805 pwrkey`，`KEY_POWER` | `[BSP-5.10 RUNTIME VERIFIED]` |
| RESET | 硬件复位 | 不是 Linux input event |

模拟旋钮是单独的模拟量输入，不属于上面六个按键。它从 SARADC channel 6 读取：

```bash
cat /sys/bus/iio/devices/iio:device0/in_voltage6_raw
```

除非后续原理图或运行证据证明，否则不要把板子描述成“四个 ADC key”。当前证据显示：用户按键由两个 GPIO key 加两个 ADC key 组成。

## 检查 input 设备

先查看 input 设备列表：

```bash
cat /proc/bus/input/devices
ls /dev/input
```

再按设备名称选择 `evtest` 目标，不要写死 event 编号：

```bash
evtest /dev/input/event0
```

GPIO key 输出示例：

```text
Input device name: "gpio_keys_polled"
Event code 103 (KEY_UP)
Event code 108 (KEY_DOWN)
```

RK809 power key 输出示例：

```text
Input device name: "rk805 pwrkey"
Event code 116 (KEY_POWER)
```

虽然 Linux input name 显示 `rk805`，但本板上它对应的是 RK809 PMIC PowerKey 功能。

## BSP 5.10 PowerKey 路径

BSP 5.10 已验证链路：

```text
PMIC PowerKey
→ Linux input KEY_POWER
→ /etc/power-key.sh press/release
→ PM: suspend entry (deep)
```

完整 suspend / resume 只有在 wakeup 也经过测试后，才能标记为已验证。
