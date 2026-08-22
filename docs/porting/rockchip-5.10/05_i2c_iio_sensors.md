# 05 - I2C 与 IIO 传感器

> 状态：SARADC、MPU6050、BH1750 均为 `[BSP-5.10 RUNTIME VERIFIED]`。

## 已验证设备

| 设备 | 总线 / 地址 | 子系统 | 证据 |
|------|-------------|--------|------|
| RK3568 SARADC | SoC 内部 | IIO | `iio:device0`，name 为 `fe720000.saradc`，导出 `in_voltage*_raw`、`in_voltage_scale` |
| MPU6050 | I2C2 `0x69` | IIO | `inv-mpu6050-i2c 2-0069` probe，accel / gyro / temp raw values、scale、mount matrix、calibration bias |
| BH1750 | I2C2 `0x23` | IIO | `bh1750 2-0023` probe，IIO `iio:device2`，导出 `in_illuminance_raw`、`in_illuminance_scale`、`in_illuminance_integration_time` |

## 调试案例：设备存在但驱动未绑定

MPU6050 / BH1750 的 bring-up 是本项目很典型的参考案例：

```text
DTS creates I2C clients 2-0023 and 2-0069
compatible strings are correct
but no IIO device appears
```

根因是内核配置未启用：

```text
# CONFIG_INV_MPU6050_I2C is not set
# CONFIG_BH1750 is not set
```

修复位置为 `arch/arm64/configs/rockchip_linux_defconfig`：

```text
CONFIG_INV_MPU6050_I2C=y
CONFIG_BH1750=y
```

执行 `olddefconfig` 后，有效配置包含：

```text
CONFIG_INV_MPU6050_IIO=y
CONFIG_INV_MPU6050_I2C=y
CONFIG_BH1750=y
```

运行时结果：

```text
iio:device1: mpu6050
iio:device2: bh1750
```

BH1750 实测读数（`in_illuminance_raw` × `in_illuminance_scale` = lux，scale = `0.833333`）：

```text
raw=88   → 73.3 lux   （正常环境光）
raw=18   → 15  lux    （手遮传感器）
raw=117  → 97.5 lux   （恢复光照）
```

raw 随手遮挡/光照明显变化，确认 BH1750 采集真实照度，功能正常。
