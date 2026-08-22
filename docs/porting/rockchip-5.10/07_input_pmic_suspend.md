# 07 - Input、PMIC 与 Suspend

## RK809 PowerKey

状态：`[BSP-5.10 RUNTIME VERIFIED]`。

Linux input 名称：

```text
rk805 pwrkey
```

虽然 input 设备名显示 `rk805`，但在本板上它对应的是 RK809 PMIC 的电源键功能。该名称属于驱动历史兼容命名，不表示硬件识别成了 RK805。

已验证事件：

```text
EV_KEY KEY_POWER value 1
EV_KEY KEY_POWER value 0
```

已验证用户态脚本路径：

```text
/etc/power-key.sh press
/etc/power-key.sh release
```

已验证电源键链路：

```text
PMIC PowerKey
→ Linux input
→ KEY_POWER
→ userspace power script
→ PM: suspend entry (deep)
```

在 wakeup 也完成测试之前，不要写成完整 suspend / resume 已验证。

## RK817 Battery / Charger Warning

已知 warning：

```text
rk817-battery: Failed to locate of_node
rk817-battery: Failed to find matching dt id
rk817-charger: Failed to locate of_node
rk817-charger: Failed to find matching dt id
```

这不代表 RK809 PMIC 整体不可用。RTC、regulators 和 PowerKey 可以正常工作，同时 battery / charger 子驱动因为板级 DT 或硬件装配差异而无法匹配。

待决配置：

```text
CONFIG_BATTERY_RK817
CONFIG_CHARGER_RK817
```

只有确认板子没有需要这些驱动的电池 / 充电电路后，才建议关闭它们。
