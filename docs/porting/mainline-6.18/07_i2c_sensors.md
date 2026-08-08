# 03 - I2C 传感器：BH1750 光照 + MPU6050 六轴

> 板子（RK3568 EVB1 V10 / GEC V1.1）出厂 4.19 下已验证存在两个 I2C 传感器，
> 但主线 `rk3568-evb1-v10.dts` 未声明，需补进 `rk3568-gec-v11.dts` 并打开内核驱动。
> 本步骤不涉及 Buildroot / ADB，纯内核 + DTS 改动。

## 1. 接线来源（出厂 DTB 反编译核对）

`hardware/Device Tree/rk3568.dts` 中：

- `i2c@fe5b0000`（即 `i2c2`，alias `i2c2 = "/i2c@fe5b0000"`）
  - `bh1750@23`：`compatible = "rohm,bh1750"; reg = <0x23>;`
  - `mpu6050@69`：`compatible = "invensense,mpu6050"; reg = <0x69>;`
    - `interrupt-parent = <&gpio3>; interrupts = <RK_PC7 IRQ_TYPE_EDGE_RISING>;`
    - `mount-matrix = "-0.9848 0 -0.1736 0 -1 0 -0.1736 0 0.9848";`（出厂值，轴向修正）

> 中断 GPIO：出厂 DTS 里 `phandle 0x41` = `gpio3`，`interrupts <0x17 0x01>` = 引脚 23 = `GPIO3_C7`，
> flags `0x01` = `IRQ_TYPE_EDGE_RISING`。已转写为标准宏。

## 2. DTS 补丁（加到 `rk3568-gec-v11.dts`）

```dts
/* I2C2：BH1750 光照 + MPU6050 六轴（出厂默认 okay，保险起见再显式开） */
&i2c2 {
    status = "okay";

    /* 光照传感器 ROHM BH1750，挂 i2c2 0x23 */
    bh1750: light-sensor@23 {
        compatible = "rohm,bh1750";
        reg = <0x23>;
        status = "okay";
    };

    /* 六轴加速度/陀螺仪 Invensense MPU6050，挂 i2c2 0x69 */
    mpu6050: imu@69 {
        compatible = "invensense,mpu6050";
        reg = <0x69>;
        interrupt-parent = <&gpio3>;
        interrupts = <RK_PC7 IRQ_TYPE_EDGE_RISING>;
        /* 轴向修正矩阵（来自出厂 DTB） */
        mount-matrix = "-0.984807753012208 0 -0.173648177666930",
                       "0 -1 0",
                       "-0.173648177666930 0 0.984807753012208";
        status = "okay";
    };
};
```

> 注意：`i2c2` 的 pinctrl 为 `i2c2m1_xfer`（SDA `GPIO4_B4` / SCL `GPIO4_B5`，已与提交 DTS 核对），
> 无需额外 `pinctrl-0`；中断沿用 `gpio3` 标准控制器。
> 本板 I2C2 推荐 `clock-frequency = <100000>`（100 kHz）。**不要把 BH1750 的历史 NACK 唯一归因于 400 kHz**——
> 实测中 100 kHz 也曾 NACK，更可能是早期 DTS 节点缺失/驱动未编导致设备未绑上（详见 `../../../docs/troubleshooting/i2c.md` §5）。

## 3. 内核配置（符号务必打开，建议 =y 内置，避开模块版本 mismatch）

```bash
# 在 6.18 内核源码树里
scripts/config --module BH1750          # 也可 --enable 内置
scripts/config --module INV_MPU6050_I2C
# 依赖会自选中：INV_MPU6050_IIO、IIO
make olddefconfig

# 确认
grep -E 'CONFIG_BH1750|CONFIG_INV_MPU6050' .config
# 期望：CONFIG_BH1750=m  (或 =y)   CONFIG_INV_MPU6050_I2C=m
```

> 之前 goodix / 8723ds 报 `invalid module format`，是因为 4.19 旧 .ko 被塞进 6.18。
> 只要本次 **整套内核 + 模块同源重编** 就不会再 mismatch；本步骤更推荐直接 `=y` 内置，
> 不依赖 `modules_install` / 外置 .ko。

## 4. 重编 + 重打包 FIT（沿用 02_usb_fix 流程）

```bash
make -j$(nproc) Image.gz rockchip/rk3568-gec-v11.dtb   # 若用 =m 则追加 modules
mkimage -f fit-image.its -E -p 0x800 boot-6.18.img
truncate -s 32M boot-6.18.img
# RKDevTool 只烧 boot 分区，U-Boot / rootfs 不动
```

## 5. 板端验证（启动后进串口 / SSH）

### 5.1 I2C 总线先探活（无需驱动也能看）

```bash
i2cdetect -y 2        # i2c2 → 应看到 0x23 和 0x69
#       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 20: -- -- -- 23 -- -- -- -- -- -- -- -- -- -- -- --
# 60: -- -- -- -- -- -- -- -- 69 -- -- -- -- -- -- --
```

### 5.2 驱动绑定后看 IIO 设备

```bash
for d in /sys/bus/iio/devices/iio:device*; do
    echo "=== $d ==="; cat "$d/name" 2>/dev/null
done
# 期望出现：fe720000.saradc（原生）、bh1750、mpu6050
```

### 5.3 BH1750 读数（光照 lux）

```bash
cd /sys/bus/iio/devices/iio:device*/   # 进 bh1750 那个目录
cat in_illuminance_raw      # 原始值
cat in_illuminance_scale    # 换算系数（如 1.2）
# lux ≈ raw * scale ；用手电/遮挡验证数值变化
```

### 5.4 MPU6050 读数（加速度 + 角速度）

```bash
cd /sys/bus/iio/devices/iio:device*/   # 进 mpu6050 那个目录
cat in_accel_x_raw in_accel_y_raw in_accel_z_raw
cat in_anglvel_x_raw in_anglvel_y_raw in_anglvel_z_raw
cat in_temp_raw
# 平放时 in_accel_z_raw 应接近 +g（约 16384，±2g 量程），晃动时三轴变化
```

> 若 `in_accel_z_raw` 接近 0 而某水平轴接近 g，说明 `mount-matrix` 轴向不符，
> 可回退为不填 `mount-matrix`（驱动默认单位矩阵）。

## 6. 排错

| 现象 | 原因 / 处理 |
|------|------------|
| `i2cdetect` 看不到 0x23/0x69 | `i2c2` 没 enable → 确认 `&i2c2 { status="okay"; }`；或 pinctrl 冲突 |
| `name` 无 bh1750/mpu6050 | 驱动未编进内核 → 检查 `CONFIG_BH1750` / `CONFIG_INV_MPU6050_I2C` |
| MPU6050 `in_accel_*` 全 0 | 中断 GPIO 配错（PC7）或 `mount-matrix` 异常；可先去掉中断属性试轮询 |
| 模块 `invalid module format` | 旧 4.19 .ko 混入；用 `=y` 内置或整套重编 modules |

## 7. 进度

- [x] 出厂 DTB 挖出 BH1750 / MPU6050 总线与地址
- [x] DTS 补丁 + 内核配置 + 验证步骤就绪
- [x] 用户 WSL 侧应用 DTS、开驱动、重编 FIT
- [x] 板端 `i2cdetect` + IIO 读数确认（2026-08-08 实测 ✅）

---

## 8. 实测读值（验证已通 ✅）

板端实机验证，IIO 设备已正确绑定（注意：`iio:deviceN` 编号**不是固定 ABI**，每次启动/驱动加载顺序可能变化，**务必按 `name` 定位**）：

```bash
for d in /sys/bus/iio/devices/iio:device*; do echo "=== $d ==="; cat "$d/name"; done
# === /sys/bus/iio/devices/iio:device0 ===  fe720000.saradc   ← 原生 ADC（示例，编号不固定）
# === /sys/bus/iio/devices/iio:device1 ===  mpu6050           ← 六轴（示例）
# === /sys/bus/iio/devices/iio:device2 ===  bh1750            ← 光照（示例）
```

**按 name 定位设备**（避免硬编码 `iio:deviceN`）：

```bash
LIGHT=$(for d in /sys/bus/iio/devices/iio:device*; do [ "$(cat $d/name)" = bh1750 ] && echo $d; done)
IMU=$(for d in /sys/bus/iio/devices/iio:device*; do [ "$(cat $d/name)" = mpu6050 ] && echo $d; done)
```

BH1750 真实读值（随光照明显变化）：

```bash
cat "$LIGHT"/in_illuminance_raw
# 例: 478  （手电照射会升高，遮挡会下降）
```

MPU6050 加速度（平放时 z 轴接近 +g）：

```bash
cat "$IMU"/in_accel_z_raw   # 约 16384（±2g 量程）
```

> 出厂 `rk356x-demo` 用户态读取路径作对照（出厂 4.19 固件里的编号，与本主线不同，**仅作对照不照搬**）：
> `/sys/devices/iio:device2/in_illuminance_raw`（光照）、
> `iio:device1/in_accel_*`（六轴）、`iio:device0/in_voltage6_raw`（ADC 按键）。

用户态快捷访问（内核 `/sys/class/` 不允许建子目录，用软链接到可写目录）：

```bash
ln -s "$LIGHT"/in_illuminance_raw /tmp/light
cat /tmp/light
# 或 ~/.bashrc: alias light='cat "$LIGHT"/in_illuminance_raw'
```

---

## 9. 错误假设保留（调试过程价值）

早期曾假设「**BH1750 是硬件损坏**」（读数异常），后被实验推翻：

- **初始假设**：BH1750 硬件损坏。
- **结果**：被 4.19 正常通信实验 + 6.18 IIO 成功读出 `in_illuminance_raw`（值随光照变化）推翻。
- **当前结论**：BH1750 硬件正常；6.18 早期读不到是因 DTS 节点缺失 + 驱动未编（已修复）。

保留这条推理，比直接写"已修复"更有价值——它体现了真实调试路径，也避免后人重蹈"先怪硬件"的坑。

> 另：I2C 频率问题**不能唯一归因于 400kHz**——历史测试中 100kHz 也曾 NACK，详见 `../../../docs/troubleshooting/i2c.md` §5。
