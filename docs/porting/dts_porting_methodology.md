# DTS 移植方法论（跨路线）

> 本文提炼 GEC RK3568 板级 DTS 移植中反复验证有效的方法，横跨 **4.19（参考）→ 6.1（尝试）→ 5.10（成功）→ 6.6（未来）** 四条路线。
> 它是「怎么改、怎么判断对错」的 playbook；「改了什么」的具体落盘见 `rockchip-6.1/01_dts_override.md` 与 `rockchip-5.10/02_device_tree.md`。
> 本文不重复列节点，只沉淀方法。

## 1. 核心思想：override 层，不改 Rockchip 原文件

- 永不修改 Rockchip 官方文件（`rk3568-evb1-*.dtsi`、`rk3568.dtsi`、`rk3568-linux.dtsi` 等）。
- 只新增**一个板级 override 文件**（`rk3568-gec*.dtsi`）+ 一个薄入口 `.dts`（`#include` 官方文件 + override 文件）。
- 好处：Rockchip 升级 SDK 时，板级差异干净地独立出来，diff 一目了然，回滚/审计都简单。

**三类 override 动作**：

1. **覆盖值**（override）——改官方默认值，如 `gmac1` `clock_in_out` output→input。
2. **禁用错误继承**（disable wrong default）——如 `&sdmmc2 { status="disabled" }`（GEC WiFi 在 SDMMC1，不是官方 EVB1 的 SDMMC2）。
3. **补回独有节点**（re-add）——如 i2c2 的 BH1750/EEPROM/MPU6050。

## 2. 三层快照区分（最容易被忽略的坑）

移植时脑子里必须同时分清三个「快照」，它们**不是同一件事**：

| 快照 | 含义 | 来源 |
|------|------|------|
| **GEC 硬件** | 板子真实接线是什么 | 原理图 + factory DTS 反编译 |
| **目标 BSP 的 EVB1** | Rockchip 这一版的官方默认是什么 | 目标内核树 `rk3568-evb1-*.dtsi` |
| **factory 4.19** | 出厂那版是什么 | 反编译 factory boot.img 的 DTB |

**关键教训**：`4.19 EVB1 ≠ 6.1 EVB1`（GMAC delay 0x41/0x1e→0x4f/0x26、WiFi sdmmc1→sdmmc2、i2c2 传感器被删、NPU 节点从 rk3568.dtsi 挪到 rk356x.dtsi……）。所以 **GEC 的 override 必须描述「GEC 硬件 vs 目标 BSP 的 EVB1」，绝不能盲抄 4.19 的 GEC DT**。

## 3. 系统性 diff + 三类分类

从 factory DTB 提取板级差异，不要靠肉眼逐行看，用脚本做 full-path 对比：

```
反编译 factory DTB → full-path diff（vs 目标 BSP EVB1 的 DTB）
→ phandle 经 __symbols__ 解析成 LABEL（稳定词汇，避免误判）
→ 每个 diff 分三类
```

| 分类 | 含义 | 处置 |
|------|------|------|
| **BOARD_DELTA** | 板级真实差异（GEC 独有） | ✅ 落盘到 override 层 |
| **BSP_DRIFT** | BSP 版本演进（如 serial@* compatible 扩展、usb3 phy 补丁） | ❌ 不落盘（版本差异，非板级） |
| **ARTIFACT** | phandle 重编号等噪声 | ❌ 忽略 |

实例：`backlight pwms period 1000000ns` = BOARD_DELTA（落盘）；`pcie@fe26*` compatible 扩展 = BSP_DRIFT（不落盘）；`wireless-wlan WIFI,host_wake_irq` phandle 0xb4 vs 0xb3 = ARTIFACT（忽略）。

## 4. 参考纪律：factory DTS 是「参考」，不是「真理」

factory 4.19 DTS 是**唯一反映 GEC 真实接线**的权威参考，但它**不可盲信**：

1. **已证实的 factory 错误**：
   - `vcc5v0_otg` 漏了 `enable-active-high`（与硬件 SY6280 高有效 + fixed-regulator 语义矛盾）。
   - GT911 `irq-gpios` 极性（factory 的 flag 是 open-drain 位，不是极性位，曾被误读）。
2. **规则：与原理图/硬件冲突时，信硬件，不信 factory DTS**。
3. **版本坑**：本地 4.19 树是 **4.19.219**，但真正能跑的 factory 是 **4.19.232**——本地树不是可信 baseline，不能拿它对比 6.1/5.10 的 NPU 行为。
4. **改没改先看 git**：判断 SDK 里的 dtsi 是否被改，用 `git status`/`git diff HEAD` 看**实际编译的那份**，别分析用户说「没用」的 backup 拷贝。

## 5. GPIO 极性约定

DTS 里 GPIO 引用元组（如 `<&gpio3 RK_PC2 0x00>`）的**末位是 GPIO_ACTIVE_* flag**：

- `0` = `GPIO_ACTIVE_HIGH`
- `1` = `GPIO_ACTIVE_LOW`

（Linux `dt-bindings/gpio/gpio.h` 标准，`GPIO_ACTIVE_HIGH`/`GPIO_ACTIVE_LOW` 宏。）

**两条易混的坑**：

1. 这个 flag **不是 IRQ 触发类型**——IRQ 类型在 `interrupts` 属性里，不在 GPIO 元组末位。`0x04` 这类是 `GPIO_LINE_OPEN_DRAIN`（bit2），不是极性。
2. `fixed-regulator` 的 `enable-active-high` 属性是**另一个概念**，别和 GPIO flag 混（见 §4 的 VBUS 案例）。

> 曾在 4.19 DTB 审计时把这个搞反过（`0x01` 读成 HIGH），被纠正。审计极性时务必回查 `0=HIGH / 1=LOW`。

## 6. 证据链：DTS 写对 ≠ 功能完成

每层证据按「最弱成立」记录，不要跳级（详见 `rockchip-5.10/02_device_tree.md` 与 `11_debug_methodology.md`）：

```text
source DTS → built DTB → running DTB → bus device/client → driver bind
→ subsystem register → sysfs/dev node → runtime behavior
```

- `status = "okay"` 只说明意图，不代表驱动绑定、更不代表用户态可用。
- 判断「设备是否 probe」以 `/sys/bus/i2c/devices/`、`i2cdetect` 板端实况为准，别只看 grep 过的日志（BH1750「消失」误判的教训）。

## 7. 常见 gotcha 清单

| gotcha | 正确做法 |
|--------|---------|
| GMAC tx/rx_delay | GEC 保持 `0x41/0x1e`，**不要**采 6.1 EVB1 的 `0x4f/0x26` |
| GMAC 命名 | **BSP 5.10 里 `fe010000`=gmac1（真口）、`fe2a0000`=gmac0（空口），与主线相反**；判断一律以 reg 地址为准，别信 gmac0/gmac1 名字；BSP 用**单数 `reset-gpio`**（不是 `reset-gpios`） |
| WiFi SDMMC | GEC 在 `sdmmc1`（不是 EVB1 的 `sdmmc2`），要 disable sdmmc2 |
| NPU 节点位置 | 6.1 从 `rk3568.dtsi` 挪到 `rk356x.dtsi`；compatible `rockchip,rk3568-rknpu` 跨版本不变 |
| Touch 属性命名 | `goodix,gt911` 用 `irq-gpios`/`reset-gpios`；`goodix,gt1x` 用 `goodix,irq-gpio`/`goodix,rst-gpio` |
| GT911 中断 | 6.1 `goodix.c` 用 `client->irq`（来自 `interrupts`），**不**调用 `gpiod_to_irq`——节点必须带 `interrupt-parent`+`interrupts` |
| GT911 地址选择 | `reg=0x5d` 时 `irq-gpios` 必须 `GPIO_ACTIVE_HIGH`（address-select 逻辑反相） |
| 背光 PWM 索引 | 丝印 `pwm4` 可能对应 `pwm@fe6e0000` 的索引 +1，核对 `pinctrl` 再写 |
| WiFi 控电 | GEC 用单一 `sdio_pwrseq reset-gpios`；**不要**再加 `WIFI,poweren_gpio`（双重控电） |

（每条的具体落盘见 `rockchip-6.1/01_dts_override.md`。）

## 8. 工具

- **dtc 反编译**：`dtc -I dtb -O dts -o out.dts in.dtb`（uutils 的 dtc 用 `tail -n N`，不是 `-N`）。
- **DTB 对比脚本**（当时在 `tmp_boot_cmp/` 里写的，未入库，可考虑 formalize 到 `scripts/`）：`dtb2dts.py`、`dtb_cmp.py`、`dtb_cmp2.py`、`extract_cfg_dtb.py`。
- **板端只读快照**（已入库）：`scripts/check_bsp_5_10.sh`、`scripts/check_i2c_bindings.sh`。
- **交叉编译工具链**：全量构建用 `/opt` GCC 15.2（`aarch64-none-linux-gnu-`）；4.19-SDK GCC 6.3.1 只能做轻量任务（全量会被 `CONFIG_WERROR=y` 卡死）。
