# 06 - RTC 与 EEPROM

## RTC

| 设备 | 状态 | 证据 |
|------|------|------|
| RK809 internal RTC | `[BSP-5.10 RUNTIME VERIFIED]` | `rtc0`，name 为 `rk808-rtc`，可通过 `hwclock` 读取 |
| PCF8563 external RTC | `[BSP-5.10 RUNTIME VERIFIED]`，但有 warning | I2C0 `0x51`，compatible 为 `nxp,pcf8563`，注册为 `rtc1` |

PCF8563 warning：

```text
invalid alarm value
```

这是 alarm 相关 warning，不等于驱动 probe 失败。在 alarm 行为弄清楚之前，继续把该 warning 作为 `[PENDING]` 跟踪。

## 24C02 EEPROM

当前状态：`[BSP-5.10 RUNTIME VERIFIED]`。

已观察路径：

```text
I2C2 address 0x50
compatible = "atmel,24c02"
client = 2-0050
```

早期证据显示 I2C client 存在，但没有 driver symlink 或 EEPROM sysfs 文件；最新迁移盘点中 EEPROM 已确认正常。归档时建议补充对应板端命令输出，例如 driver symlink、`eeprom` sysfs 文件或实际读写记录。

相关内核配置：

```text
CONFIG_EEPROM_AT24
```

后续如果要把证据写实，可补充：

```bash
ls -l /sys/bus/i2c/devices/2-0050/driver
find /sys/bus/i2c/devices/2-0050 -maxdepth 1 -type f -name 'eeprom'
hexdump -C /sys/bus/i2c/devices/2-0050/eeprom | head
```
