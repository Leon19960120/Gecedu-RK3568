# 排障 - I2C / IIO 传感器

> **适用范围：Mainline 6.18。** 本页保留 Mainline 专题排障，不代表 BSP 5.10 或 BSP 6.1 的当前状态。
> BSP 5.10 与 BSP 6.1 同等维护；5.10 IIO 传感器状态见 `../porting/rockchip-5.10/05_i2c_iio_sensors.md`，6.1 状态按其总览和长期验证日志判断。
> 6.18 特有结论（如 I2C 频率 NACK、DTS 节点缺失）不要直接套用到 5.10。

> 对应 6.18 bring-up 文档：`../porting/mainline-6.18/07_i2c_sensors.md`

---

## 1. `i2cdetect` 看不到 0x23 / 0x69

**现象**：`i2cdetect -y 2` 扫描 i2c2 看不到 BH1750(0x23) / MPU6050(0x69)。

**原因 / 处理**：
- `i2c2` 没 enable → 确认 `&i2c2 { status = "okay"; }`（本板 pinctrl 为 `i2c2m1_xfer`，SDA `GPIO4_B4` / SCL `GPIO4_B5`，无需额外 pinctrl）。
- pinctrl 冲突（罕见）。

```bash
cat /sys/firmware/devicetree/base/i2c@fe5b0000/status 2>/dev/null | tr -d '\0'   # 期望 okay
i2cdetect -y 2
```

---

## 2. `ls /sys/bus/iio/devices/` 全空（含 saradc 都没有）

**现象**：IIO 零设备，连原生 saradc 都没有。

**原因**：驱动未编入内核。实测 config 铁证：
- `CONFIG_IIO=y`（核心内置）
- `CONFIG_ROCKCHIP_SARADC=m`（saradc 是**模块** → 无 `/lib/modules` 加载不了）
- `CONFIG_INV_MPU6050_I2C` 未设置
- `CONFIG_BH1750` 未设置

**处理**：整套内核 + 模块同源重编，或直接把驱动 `=y` 内置（避开模块版本 mismatch）：

```bash
./scripts/config --enable CONFIG_ROCKCHIP_SARADC
./scripts/config --enable CONFIG_BH1750
./scripts/config --enable CONFIG_INV_MPU6050_I2C
./scripts/config --enable CONFIG_IIO_TRIGGERED_BUFFER
make ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- olddefconfig
```

> 结论：**传感器上线 = config(=y) + DTS 节点 双修**。saradc 仅缺驱动(=m)；bh1750/mpu6050 是驱动未编 + 缺 DTS 节点。

---

## 3. MPU6050 `in_accel_*` 全 0 / 轴向不对

**现象**：`in_accel_z_raw` 接近 0 而某水平轴接近 g。

**处理**：
- **committed 6.18 DTS 的 MPU6050 没有 `interrupts` 属性 → 当前是 polling 模式**（这是正常状态，不是 bug）。原理图有 `MPU6050 INT → GPIO3_C7`（`RK_PC7`，SCHEMATIC 背书），但 committed DTS 未建模该中断。
- 若你**自行加回** `interrupts = <RK_PC7 IRQ_TYPE_EDGE_RISING>;` 想用中断模式：先确认 GPIO 配错（应是 `GPIO3_C7`）→ 仍能 "去掉中断属性试轮询" 回到 committed DTS 的 polling 态。
- `mount-matrix` 轴向不符 → 回退为不填 `mount-matrix`（驱动默认单位矩阵）；如需修正，可据出厂 4.19 DTB 的轴向矩阵补回（FACTORY-4.19 证据，6.18 下未验证）。

```bash
# 平放时 in_accel_z_raw 应接近 +g（约 16384，±2g 量程），晃动时三轴变化
cat /sys/bus/iio/devices/iio:device*/in_accel_z_raw
```

---

## 4. BH1750 读数不随光照变化

**现象**：`in_illuminance_raw` 不变或异常。

**处理**：
- 确认驱动绑定：`for d in /sys/bus/iio/devices/iio:device*; do cat $d/name; done` 应见 `bh1750`。
- 确认时钟频率：本板 I2C2 推荐 `clock-frequency = <100000>`（见下条频率说明）。
- 真实读数验证：

```bash
# 先按 name 定位（iio:deviceN 编号不固定）
LIGHT=$(for d in /sys/bus/iio/devices/iio:device*; do [ "$(cat $d/name)" = bh1750 ] && echo $d; done)
cat "$LIGHT"/in_illuminance_raw   # 用手电/遮挡应明显变化
```

---

## 5. 关于 I2C 频率的严谨说明

> **不要简单写"BH1750 根因就是 400k"。** 历史测试中**既存在 400 kHz 下 NACK，也存在 100 kHz 下 NACK**。

当前推荐：`clock-frequency = <100000>;`（100 kHz 是本板较稳妥的配置）。
但 100 kHz 曾出现 NACK 的历史说明：**不能把全部异常唯一归因于 I2C 时钟频率**——
更可能是早期 DTS 节点缺失/驱动未编导致设备根本没绑上。400 kHz NACK 与 100 kHz NACK 都发生过，
频率只是可能因素之一，需结合 `i2cdetect` + IIO 设备 presence 综合判断。

---

## 6. 读取传感器值的用户态技巧

`/sys/class/` 是内核动态目录树，不允许直接建子目录（即使 root）。想给光传感器建快捷访问：

```bash
# 临时
LIGHT=$(for d in /sys/bus/iio/devices/iio:device*; do [ "$(cat $d/name)" = bh1750 ] && echo $d; done)
ln -s "$LIGHT"/in_illuminance_raw /tmp/light
cat /tmp/light
# 或别名（~/.bashrc）
alias light='cat "$LIGHT"/in_illuminance_raw'
```

> 出厂 `rk356x-demo`（4.19 固件）读取路径作对照：`/sys/devices/iio:device2/in_illuminance_raw`（光照）、
> `iio:device1/in_accel_*`、`iio:device0/in_voltage6_raw`（ADC 按键）。**该编号是出厂固件下的，主线编号不固定，请勿照搬**。

---

## 7. 错误假设保留（调试过程价值）

早期曾假设「BH1750 是硬件损坏」，后被实验推翻：
- **初始假设**：BH1750 硬件损坏（读数异常）。
- **结果**：被 4.19 正常通信实验 + 6.18 IIO 成功读出 `in_illuminance_raw`（值随光照变化）推翻。
- **当前结论**：BH1750 硬件正常，问题在 6.18 的 DTS 节点缺失 + 驱动未编（已修复）。

保留这个推理过程，比直接写"已修复"更有价值——它体现了真实调试路径。
