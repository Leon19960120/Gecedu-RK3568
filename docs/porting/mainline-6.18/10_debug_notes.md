# GEC-RK3568 项目开发日志

> 本文件由 WorkBuddy（Wiz）持续维护，按日期记录项目进展、关键决策、验证结果与下一步。
> 配套文档：
> - `docs/porting/mainline-6.18/00_overview.md` — 技术主题全记录（按章节，已修订为"主线 6.18 内核移植"）
> - `logs/` — 原始串口启动日志归档（`.txt` 原始抓取 + `logs/README.md` 索引）
>
> 维护约定：每节固定结构 = 【进展】【关键决策】【验证结果】【下一步】【遗留/风险】。

---

## 2026-08-05 — 方向确定：Buildroot + 主线内核

- **进展**：梳理项目原有规划（原 `01_全记录.md` 写"向 Ubuntu/Debian 移植"）；与用户确认新目标。
- **关键决策**：
  - 新目标 = 移植到**基于 Linux 主线内核的 Buildroot**，用于学习 Linux 命令/系统构建。
  - 放弃 fnOS（NAS 系统，RK3568 引脚浪费，且闭源定制空间小）。
  - 放弃 Ubuntu/Debian 完整发行版路线（学习价值不如自搭 Buildroot）。
- **事实补充**：
  - Linux 7.0 内核真实存在（2026-04 发布，当前 stable 已到 7.1.x，7.0 末版 7.0.14 已 EOL）；实际建议用 **6.18 LTS** 或 7.1 stable。
  - 板子 = Rockchip 官方 **RK3568 EVB1 DDR4 V10**，mainline 内核自带 `rk3568-evb1-v10.dts`，起步难度低于"野板"。
- **下一步**：搭建 x86_64 Ubuntu 编译环境 → pull 主线内核 → 先让板子进串口 shell（最小系统）。

---

## 2026-08-06 — 内核编译 + FIT 打包攻坚

- **进展**：
  - 逆向出厂 `rk356x-demo`（Ghidra 12.1.2 + PyGhidra），产出 `docs/development/decompiled_rk356x-demo.c`、`reverse_index.md`、`reverse_functions.md`（555 函数伪 C，确认 LED/Buzzer/RTC/GSensor/光照 等脚位）。
  - 用户在 WSL2（hyl@HYL）clone 主线 `linux` tag `v6.18` → `~/linux-rk3568`（6.18.0 LTS）。
  - 交叉工具链 = `/opt/arm-toolchain/gcc-aarch64/bin/aarch64-none-linux-gnu-gcc`（15.2，ARM 官方）。
  - `make ARCH=arm64 defconfig` + 改 `console=ttyS2,1500000 root=PARTUUID=614e0000-0000 rootwait`（CMDLINE_FORCE）+ 编译 `Image dtbs` **成功**（基线内核到手，Image 40M / dtb 62K）。
  - 解析厂商 `boot.img` = FIT 格式；创建 `docs/porting/fit-image.its` 模板。
  - 发现板子 boot 分区实际 **32MiB**（出厂 4.19.232 boot.img=32MiB 吻合），39MiB 主线 Image 塞不下 → 必须 **gzip 压缩内核**。
  - 根因定位：Rockchip U-Boot `boot_fit` 调 `fit_is_ext_type()`，要求 FIT 头 `fdt_totalsize < 4KiB`；普通 `mkimage -f` 内嵌数据使头 ~14MiB → `FIT: No fit blob`。
  - **外置 FIT 打包成功**：`mkimage -f fit-image.its -E -p 0x800 boot.img`，totalsize `0x3c4`（远小于 4KiB），`mkimage -l` 结构正确。
- **关键决策**：
  - 用**外置 FIT**（`-E`）而非内嵌；`.its` 用**真实 RAM 地址**（kernel `0x04080000` / fdt `0x08300000`），不用厂商 `0xffffff01/0xffffff00` 占位符（占位符仅 SPL 阶段有效，手动 `boot_fit` 不换算）。
  - 内核 `compression="gzip"`（→ ~14MiB 适配 32MiB 分区）；保留自动 sha256、去 RSA 签名节点（Verified-boot:0 不强制验签）。
  - 保留厂商 U-Boot，**只烧 boot 分区**（RKDevTool），不动 Loader/parameter。
- **下一步**：拷回 Windows → RKDevTool 烧 boot → 串口 1500000 看启动。

---

## 2026-08-07（上）— 6.18 主线内核启动成功（🏁 里程碑）

- **进展**：外置 FIT（gzip + 真实 load 地址）+ RKDevTool 只烧 boot，U-Boot 自动 `boot_fit` 进入出厂 Buildroot 4.19.232 rootfs 的 shell。
- **验证结果**（串口日志）：
  - `## Booting FIT Image ... Uncompressing GZIP Kernel Image ... OK`
  - `[    0.000000] Linux version 6.18.0 ... #1 SMP PREEMPT`
  - `[    0.000000] Machine model: Rockchip RK3568 EVB1 DDR4 V10 Board`
  - `[    0.000000] Kernel command line: console=ttyS2,1500000 root=PARTUUID=614e0000-0000 rootwait`（来自 U-Boot default env）
  - `[    1.008170] VFS: Mounted root (ext4 filesystem) ... device 179:6` → `Run /sbin/init` → `[root@RK356X:/]#`
  - `uname -a` → `Linux RK356X 6.18.0 #1 SMP PREEMPT Thu Aug  6 20:23:48 CST 2026 aarch64 GNU/Linux`
  - gzip 解压 ~40.9MiB 未撞 `CONFIG_SYS_BOOTM_LEN`（厂商 U-Boot 解压上限够）。
- **关键决策**：4.19→6.18 移植的内核+DTB+外置FIT+启动链**全部打通**；学习用首要目标（进系统跑命令）达成。
- **遗留/风险（均非致命）**：
  1. 触摸(gt911)/WiFi(RTL8723DS) 模块版本错：厂家 `/system/lib/modules/*.ko` 针对 4.19.232 → `invalid module format`，需为 6.18 重编。
  2. MIPI-DSI 屏/帧缓冲未起：`cannot open framebuffer device`（VOP/DSI/HDMI/GPU power-domain pending）。
  3. dwc3 USB3 初始化失败：`failed to initialize core`（EHCI USB2 正常）。
  4. configfs 未挂载（usb_gadget 不可用）；oem/userdata 挂载失败（fstab 当 ext2 实际非）；logo 预留内存失败——均无害。
- **下一步**：T1 先玩系统（验证基础外围），暂不动内核/外设驱动。

---

## 2026-08-07（下）— T1 系统验证 + 接管项目日志

- **进展**：
  - 修订 `docs/porting/mainline-6.18/00_overview.md`：前言更正为"主线 Linux 6.18 内核移植"，新增第四章（4.1 已达成 / 4.2 遗留 / 4.3 T1 验证清单 批次1-4）。
  - **T1 批次1 系统自检**（6.18 shell 实测）：`uname -a`(6.18.0 aarch64)、`free -h`(≈1.95GiB)、`/sys/firmware/devicetree/base/model`(RK3568 EVB1 DDR4 V10)、`/proc/partitions`(mmcblk1 p1~p9, p6=rootfs 6GiB)、`mount`(rootfs=/dev/mmcblk1p6 ext4 rw)。
    - **纠正**：之前预判"rootfs 只有 4.19.232 模块"是错的——`ls /lib/modules` → **No such file**；厂家 out-of-tree 模块在 `/system/lib/modules/`（goodix.ko / 8723ds.ko，4.19.232 编）。结论：该 Buildroot **不装 in-tree /lib/modules**，6.18 关键驱动(eMMC/ext4/mmc/serial/网络PHY/USB2/I2C)全内置，故无 /lib/modules 也能完整启动。
  - **T1 批次2 网络排查**：`eth0` **整个不存在**——`ip link` 只有 `lo`；网口两 LED 均未亮；U-Boot 期也 `Net: No ethernet found`。`/system/lib/modules/` 只有 3 个 4.19.232 ko，无任何 6.18 模块。
    - 主因待定：① 主线 `rk3568-evb1-v10.dts` 未启用 gmac / PHY 接线(复位GPIO、RGMII 延时)与粤嵌改版板不匹配；② 或 defconfig 未编入 stmmac。
  - 用户授权"**整个项目的日志由你来写**" → 新建本文件（`docs/porting/mainline-6.18/10_debug_notes.md`），由 Wiz 持续维护，并把 8/5–8/7 关键进展补作起点。
- **遗留/风险**：
  - eth0 缺失不阻塞批次3(IIO)/批次4(GPIO) 本地外设验证；网络修复属后续 T 阶段 DTS/驱动工作。
  - MIPI-DSI 屏、dwc3 USB3 仍待修。
  - **文档待修正**：`README.md` 写"LVDS 屏"，实际为 **MIPI-DSI**（8/6 确认），属错误表述。
- **下一步**：
  - T1 批次3 = IIO 传感器（光照 bh1750 / 六轴 mpu6050 / SARADC）
  - T1 批次4 = I2C·GPIO·LED
  - 之后视情况进入 T 阶段：重编 6.18 模块恢复触摸+WiFi → MIPI-DSI 屏驱动(T2 大任务) → dwc3 USB3 修复。

---

## 2026-08-07（续1）— T1 批次3：IIO 传感器排查（saradc / bh1750 / mpu6050）

- **进展**：
  - T1 批次3 预判三颗传感器在 6.18 下可能"坏"。实测 `ls /sys/bus/iio/devices/` **全空**（连 saradc 都没有，IIO 零设备），预判落空。
  - 实测 I2C 设备（`ls /sys/bus/i2c/devices/`）：`0-001c`=tcs4525（稳压）、`0-0020`=rk809（PMIC）、`1-0014`=gt1151（Goodix 触摸，主线 EVB1 DTS 自带节点 → 证明 I2C+DTS+驱动绑定链路本身健康）。**无 bh1750(0x23) / mpu6050(0x69) 的 I2C 设备 → DTS 确无这两颗节点**。
  - **config 铁证**（`zcat /proc/config.gz`）：`CONFIG_IIO=y`（核心内置）；`CONFIG_ROCKCHIP_SARADC=m`（saradc 是**模块**→无 `/lib/modules` 加载不了）；`# CONFIG_INV_MPU6050_I2C is not set`（mpu6050 驱动**根本没编**）；`# CONFIG_BH1750 is not set`（bh1750 驱动**根本没编**）。
- **关键决策**：传感器上线必须 **config(=y) + DTS 节点 双修**。三颗死法各异：saradc=仅缺驱动(=m)；bh1750/mpu6050=驱动未编 + 缺 DTS 节点。
- **验证结果**：早期"更可能是缺 DTS 节点而非缺驱动"判断，对 bh1750/mpu6050 是"两者皆缺"，对 saradc 是"仅缺驱动"。
- **下一步（A 路径）**：① defconfig 翻 `STMMAC_ETH/STMMAC_PLATFORM/DWMAC_ROCKCHIP/REALTEK_PHY/ROCKCHIP_SARADC/BH1750/INV_MPU6050_I2C/IIO_TRIGGERED_BUFFER` 全 `=y`；② 从出厂 `hardware/Device Tree/rk3568.dts`(4.19) 抽 bh1750/mpu6050 节点的 i2c 总线+reg 地址，补进 6.18 板级 DTS；③ 重编内核→重打外置 FIT→RKDevTool 只烧 boot。属 T 阶段内核配置+DTS 实战，不在"先玩系统"范围。

---

## 2026-08-07（续2）— 网络修复实战：gmac0 reset + 板级 DTS gec-v11

- **进展**：
  - 新内核（STMMAC 已 =y 内置）烧入后，板端 `ip link` 出现 **eth0 + eth1 双口**（旧内核 0 个 eth）→ 证明重编+重打外置 FIT+只烧 boot 成功。但双口均 `state DOWN`、无载波。
  - 用户找"现成适配 DTS"：`arch/arm64/boot/dts/rockchip/` 全是 mainline 公版板，`rk3568-evb1-v10.dts` 不含粤嵌传感器，列表内无 `rk3568-gec-*` → **无现成，需自改**。
  - 用户新建独立板级 DTS `rk3568-gec-v11.dts`（比直接改 evb1-v10 干净，不污染上游），编译 `rk3568-gec-v11.dtb` 成功。
  - **FIT 指向修正**：本智能体已改仓库 `docs/porting/fit-image.its`，fdt 段 incbin 由 `rk3568-evb1-v10.dtb` → `rk3568-gec-v11.dtb`（第59行），kernel 段仍 incbin `Image.gz`。
- **关键决策 / 根因纠正**：出厂 `hardware/Device Tree/rk3568.dts` 逐字节核对证明，板载千兆 PHY(RTL8211F) 实际接在 **`ethernet@fe010000` = 主线 `&gmac0`**（fe2a0000=主线 gmac1 在出厂 DTS 里 `status="disabled"`，板上没接 PHY，是"幽灵口"）。出厂 BSP 把 fe010000 标成 "gmac1" 只是厂内命名癖，**判断依据必须是 reg 地址不是标签名**。
  - reset 规格：`snps,reset-gpios = <&gpio3 RK_PB5 GPIO_ACTIVE_LOW>; snps,reset-delays-us = <0 20000 100000>;` 必须加到 **`&gmac0`(fe010000) 的 MAC 节点**，不是 PHY 子节点（stmmac_mdio_reset 在 MDIO 扫描前 assert/deassert）；pinctrl 用 `gmac0_*`（非 `gmac1m1_*`）。`&gmac1` 设 disabled 去掉 phantom eth。
- **验证结果（逻辑闭环）**：用户板端之前 `gpiochip3 空` + `MDIO device at address 0 is missing` + eth 都 DOWN，正因 reset 没在 MDIO 扫描前执行（错放在 PHY 子节点/错 MAC）。改 `&gmac0` 的 `snps,reset-gpios` 后，PHY 应被识别为 RTL8211F。
- **下一步**：烧入 gec-v11 + gmac0 reset 修复后，验证 `cat /sys/kernel/debug/gpio` 见 gpio-13(snps,reset) out hi；`dmesg|grep -iE 'gmac|mdio|phy|rtl'` 应见 `PHY [stmmac-0:00] driver [RTL8211F ...]`。

---

## 2026-08-07（续3）— 出厂基线对照 + 6.18+gec-v11 网络彻底通 🏁

- **进展**：
  - 用户贴出厂 4.19.232 完整启动日志作**基线对照**：eth0(fe010000/RTL8211F) 1Gbps Link Up；显示 fb 1024x600 launcher 起、MIPI-DSI 先 -517 defer 后 bound；rtl8723ds 加载、wlan0/p2p0 建但 NO-CARRIER；RTC(pcf8563)/EEPROM(24c02)/saradc/PMIC 正常。**关键点**：① 出厂**只使能单 GMAC(eth0) 无 eth1** → 印证 gmac0 才是真口；② 出厂 **Goodix-TS 1-005d 三次 i2c 探测失败(-6)** → **两内核都认不到触摸**，是屏/触摸硬件或地址问题，非 6.18 独有；③ 出厂 OTG Type-C gadget 实际 CONFIGURED（dwc3 虽报 clk 错但 device 模式可用）→ 6.18 的 `failed to init core` 更可能是 DTS/时钟/combphy 缺失而非硬件废。
  - 用户贴 6.18 + gec-v11 新启动日志：`Linux version 6.18.0-dirty ... #6 ... Machine model: Rockchip RK3568 GEC V1.1 Board` → 证明 **gec-v11.dtb 已生效** 且用户在 gmac0 纠正后重编重烧。
- **验证结果（🏁 网络里程碑）**：`rk_gmac-dwmac fe010000.ethernet eth0: PHY [stmmac-0:00] driver [RTL8211F Gigabit Ethernet]` + `eth0: Link is Up - 1Gbps/Full - flow control rx/tx`。**单 eth0、无 eth1（phantom 口消除）**，证实 gmac0 reset 修复 + STMMAC=y 完全生效；rootfs 正常挂载（mmcblk1p6 ext4 r/w）。
  - 注：bootargs 这次 PARTUUID 是完整 GUID 形式（4.19 那次是短 `614e0000-0000`），照样解析到 p6，无需担心（U-Boot env 可能被动过）。
- **遗留/风险（均预期内）**：
  1. **显示**：`cannot open framebuffer device` → 无 /dev/fb0；VOP/DSI/HDMI/GPU `sync_state() pending`（依赖显示链路未满足）→ gec-v11.dts 大概率缺 panel 节点（T2 大任务）。
  2. **触摸 / WiFi**：`goodix.ko`/`8723ds.ko` 仍 `invalid module format`（4.19 编 vs 6.18）→ 暂不可用（已知 out-of-tree 版本错，需为 6.18 重编）。
  3. **USB**：ehci/ohci/xhci + dwc3(fcc00000/fd000000) 全 `deferred probe pending: wait for supplier /usb2phy@fe8a0000|fe8b0000` → usb2phy 子节点未就绪，USB 全挂。需查 gec-v11.dts 里 usb2phy 节点是否 enabled 及依赖(vbus/otg/extcon/reset)齐。
  4. **cpufreq-dt** deferred probe pending（次要）。
- **下一步**：可选 (a) 重编 6.18 的 goodix+8723ds 模块恢复触摸+WiFi；(b) 修 USB（usb2phy DTS）；(c) T2 MIPI-DSI 显示（大任务）；(d) 验证 gec-v11 是否已含 bh1750/mpu6050/saradc 节点（`ls /sys/bus/iio/devices`）。

---

## 2026-08-07（续4）— 外围盘点：CAN / USART 现状（基于出厂 DTS）

- **进展（出厂 4.19 DTS 逆向，硬件事实）**：
  - **CAN**：3 个控制器 `can@fe570000/fe580000/fe590000`，compatible `rockchip,rk3568-can-2.0`，但**三节点全部 `status="disabled"`**；pinctrl `can0m1/can1m0` 已定义。即厂内 BSP 也没默认使能 CAN。
  - **USART**：出厂 `aliases` 把 `serial1~9` 映射到 `fe650000~fe6d0000`（uart1~9）+ `serial0=fdd50000`(uart0，通常 ATF/secure)。其中 `status="okay"` 的用户串口 = **uart1(fe650000) / uart3(fe670000) / uart4(fe680000) / uart8(fe6c0000)** 共 4 个；uart2(fe660000) 是出厂 FIQ 控制台（节点 disabled，由 ttyFIQ0 直占）；uart5/6/7/9 均 disabled。用户问的"三个 usart"即板子实际引出的 3 路（4 个里挑）。
- **6.18 现状（关键）**：mainline `rk3568.dtsi` 默认**禁用所有 uart/can**；gec-v11.dts 目前只确认使能 gmac0（网络）。**故 CAN 与那 3 个用户 USART 在 6.18 下大概率尚未出现**（与早前网络/IIO 同一根因：需板级 DTS 显式 `status="okay"` + 对应驱动编入）。6.18 当前控制台 `ttyS2`=uart2 是我们自己打开的，非厂内 FIQ 路径。
- **验证命令（板端，只看不改）**：
  - `ls /dev/ttyS*` — 看哪些 UART 成了设备
  - `dmesg | grep -iE 'ttyS|uart|serial' | head` — 看内核实际 probe 了哪些
  - `ls /sys/firmware/devicetree/base/ | grep -iE 'serial|can|uart'` — 看 DTS 现含哪些节点
  - `zcat /proc/config.gz | grep -i CAN` — 看 CAN 驱动是否编入
  - `ip link | grep -i can` — 看 CAN 接口是否生成
- **修复方向（待用户决定再动手）**：
  - USART（低风险）：gec-v11.dts 加 `&uart1/&uart3/&uart4/&uart8 { status="okay"; };`（mainline dtsi 已带默认 pinctrl，通常无需另写）。
  - CAN（有坑）：gec-v11.dts 加 `&can0 { status="okay"; pinctrl-0=<&can0m1_pins>; };`，注意 **mainline 用 `rockchip,rk3568-canfd` 兼容（非厂内 `can-2.0`）**，靠 dtsi 自带 compatible；config 需 `CONFIG_CAN=y` + Rockchip CANFD 控制器驱动（menuconfig 在 CAN bus subsystem 下）。
- **遗留/风险**：CAN 兼容字符串差异（厂内 `can-2.0` vs mainline `canfd`）是主要坑；USART 风险低。

---

## 2026-08-08（续5）— USB 选 A 路线 + 新建 `docs/porting/02_usb_fix.md`

- **进展**：用户拍板走 A（修 USB）。已沉淀整套 USB 修复文档到 `docs/porting/02_usb_fix.md`（原理 / 板端诊断 / DTS 补丁 / 重编重打包 / 烧后验证 / 遗留 六节）。
- **关键决策 / 根因**：Linux deferred-probe 的 supplier/consumer 模型——mainline `rk3568.dtsi` 里 `&usb2phy0/1` 默认 `disabled`，父不 probe → 子节点(otg/host-port)不注册成 phy → 所有 USB 控制器一直 `deferred probe pending: wait for supplier /usb2phy@fe8a0000|fe8b0000/...`；dwc3 额外 `failed to init core` 因缺 USB3 SuperSpeed phy（`usbdp_phy` 默认 disabled）。**非硬件废**（出厂 4.19 USB 正常）。
- **协作约束**：本智能体侧 `wsl` 命令被安全策略禁用（`SYSTEM TOOL DISABLED`），无法访问 WSL 内核树里的 `rk3568-gec-v11.dts`；**DTS 改动须由用户在 WSL 自行应用**。据此调整为「我出补丁+流程文档，用户跑命令贴输出」。
- **DTS 补丁要点**：启用 `usb2phy0/0_host/0_otg/1/1_host` + `usb_host0_ehci/ohci/xhci` + `usb_host1_ehci/ohci`；**故意未加 `phy-supply=<&vcc5v0_host>`**，以免 gec-v11.dts 无该稳压器时 phandle 解析失败（插 U 盘无反应再补）。
- **下一步**：用户跑板端诊断（`dmesg|grep usb2phy` / `ls /sys/class/phy/` / live dtree status）贴输出 → 核对 `usbdp_phy` 标签与有无 VBUS 稳压器 → 应用 DTS 补丁 → 重编 dtb → `mkimage -E -p 0x800` → `truncate 32M` → RKDevTool 只烧 boot → 烧后验证。

---

## 2026-08-08（续6）— USB2 Host 全链路通 ✅ / DWC3 仍待修

- **进展**：用户应用 usb2phy0/1 + EHCI/OHCI + host 控制器启用后，**USB2 Host 全链路 ✅**：EHCI/OHCI 起来、板载 4 口 Hub 已枚举（`hub 1-1: 4 ports detected`），`deferred probe pending` 消失，插 U 盘走 Mass Storage 正常。
- **关键澄清（fcc00000 坑，易踩）**：出厂 4.19 DTS 里 `fcc00000` 是 `usbdrd`（OTG dwc3，reg=0xfcc00000）；但 6.18 主线把该地址**重组为 `usbdp_phy`（USB3-DP combo PHY）**，不再是独立 dwc3。故 mainline 修法是「启用 `usbdp_phy`」，**不是**「再加 dwc3@fcc00000」。已查 `hardware/Device Tree/rk3568.dts` 确认 4.19 双 dwc3 结构（usbdrd@fcc00000 OTG + usbhost@fd000000 Host，phys=<usb2>+<usb3>）。
- **验证结果**：DWC3（`fd000000` = mainline `usb_host0_xhci`）仍 `failed to initialize core`——根因是 dwc3 需 usb2-phy(u2phy0_otg，已✅) + usb3-phy（来自 `usbdp_phy`@fcc00000，仍 disabled），拿不到 SS phy。
- **DWC3 修法（待用户应用）**：gec-v11.dts 加 `&usbdp_phy { status="okay"; rockchip,u3otg0-port=<&u2phy0_otg>; };`；标签/属性名先 `grep -n 'usbdp_phy:' / 'rockchip,u3otg' arch/arm64/boot/dts/rockchip/rk3568.dtsi` 核对（更老 dtsi 无该属性就只写 `status="okay"`）。**备选**：若只要 USB2 OTG，dwc3 节点加 `snps,usb2-only;` 即可不依赖 usbdp_phy。
- **遗留/风险**：USB Gadget/Device 模式（`/sys/kernel/config/usb_gadget/rockchip` 报错）是独立于 Host 的另一半，待 DWC3 修好后再做（configfs + extcon + UDC）。`02_usb_fix.md` 已增订：顶部进度状态（USB2✅/DWC3⏳）、第2节加 usbdp_phy 诊断、第3节补 📌fcc00000 澄清 + 应用前 3 项核对。

---

## 2026-08-08（续7）— 移植资料沉淀 + T2 显示驱动骨架准备

- **进展**：沉淀三份移植资料到 `docs/porting/`，把早期逆向结论固化为可复用文档：
  1. `mainline-7.x-porting.md` — 完整移植评估：T0–T3 难度分级、屏原理图↔DTS 交叉核对（PyMuPDF 提 PDF 文本）、9 项已知坑清单、分区/烧写布局、`parameter.txt`、WiFi RTL8723DS 专项方案（§11）。
  2. `panel-himax-evb1.c` — 屏面板 `drm_panel` 驱动骨架：`compatible="gec,rk3568-evb1-dsi-panel"`，`prepare()` 完整重放 **20 条 init 命令**（字节级从 DTS `panel-init-sequence` 机器生成，杜绝手抄错），复位/使能 GPIO、regulator、背光按 DTS 接线。
  3. `rk3568-evb1-v10-panel.dts` — 屏 DTS 片段：把 panel 节点接到 `&dsi0`，含 `pwm5` 背光修正提示。
- **关键发现（T2 硬骨头根因）**：
  - 屏 IC 是**定制 Himax**，SETEXTC 解锁密码 `B9 F1 12 83` 与所有主线 himax 驱动（hx8394=FF 83 94 / hx83102=83 10 21 / hx83112a=83 11 2a / hx8279）**均不匹配** → 无现成驱动可"改 compatible 即用"，必须自写驱动。
  - 厂商能"只改 DTS 点屏"是因为 Rockchip BSP 给 `panel-simple` 打了补丁解析私有属性 `panel-init-sequence`；**主线 `panel-simple` 忽略该属性** → 不能用厂商 DTS 段直接喂主线。
  - **背光 PWM 索引坑**：原理图丝印 "PWM4"，但 DTS 实测 `fe6e0010` = 内核 `pwm5`；主线 `rk3568-evb1-v10.dts` 用 `&pwm4` → 移植时该索引要 **+1** 对齐（或沿用厂商 pwm5 值）。
- **难度分级（资料级结论）**：T0 零改动（UART/eMMC/千兆网/USB/HDMI/I2C/SPI/PWM/VOP2/Mali Panfrost，主线 `rk356x-base.dtsi` 已覆盖）｜T1 半天级（GT911/BH1750/MPU6050/24C02/PCF8563/背光/按键）｜T1.5 WiFi（RTL8723DS 树外 `lwfinger/rtl8723ds`）｜T2 屏驱动（2~5 天）｜T3 放弃（NPU/rkvdec/rkisp/DMC/eDP/LVDS/fiq-debugger）。
- **验证结果（资料级，非板端）**：屏面板 IC datasheet 资料库里没有（仅有 Fn-Link/RTL8211F/BH1750/PCF8563/BL24C02），再次印证 T2 只能靠已提取 init 序列硬搬；驱动骨架字节级就绪，待合入主线编译验证。
- **下一步（T2 落地四步）**：① 把 `.c` 放进 `drivers/gpu/drm/panel/`，加 Makefile/Kconfig 项（文件头已注释）；② 把 `.dts` 片段合并进 `rk3568-evb1-v10.dts`，`&backlight` 的 `pwm4` 改 `pwm5`；③ 编 `CONFIG_DRM_PANEL_HIMAX_GEC_EVB1=y/m`；④ 烧写验证亮屏（图像偏移/色偏再调 `bus_flags` 与 reset 时序）。该任务可与 USB/T1 并行推进。

---

## 2026-08-08（续8）— 战略转向：弃主线 6.18，改投 Rockchip BSP 6.6 🔀

- **进展**：用户确认内核路线从「主线 6.18」转向 **Rockchip BSP 6.6**（`linux-rockchip` 的 `stable-6.6` 分支）。根因：用户需要 NPU，而**主线任意版本（6.6 / 6.18 / 7.x）均无 RK3568 NPU 官方驱动**——主线仅有的 "Rocket" NPU 驱动只支持 RK3588 及更新芯片。
- **关键决策 / 取舍**：
  - BSP 6.6 含 **in-tree `rknpu`**（`drivers/rknpu/`，DTS `npu@fde40000`），且 6.6 是 **LTS 长期支持版**（比早前提的 6.1 更优：更新 + LTS）。
  - **附带红利（直接砍掉最难的 T2）**：BSP 自带 `panel-simple` 补丁会解析 `panel-init-sequence` → MIPI-DSI 屏**靠改 DTS 即点亮**，原 `panel-himax-evb1.c` 自定义 drm_panel 驱动不再必需。
  - BSP 还带 `rkvdec` / `mpp` / `isp`（硬解 / 多媒体框架），学习/实用价值高于纯主线。
  - **6.18 阶段成果不浪费**：已跑通的网(1Gbps) / USB2 Host / 外置 FIT 打包 / DTS 调试，基底换成 BSP 6.6 后同理复用（gmac0 reset、usb2phy、FIT 流程全部可迁移）。
- **验证结果（事实级，非板端）**：社区 `rknpu-dkms` 即抽取自 Rockchip **6.6.y**，反向证明 BSP 6.6 的 rknpu 成熟可用；FriendlyELEC / Armbian BSP 6.1 亦 in-tree rknpu，6.6 更新且 LTS 更稳。
- **下一步**：
  1. **对齐文档**：本项目日志 + `docs/porting/` 内核版本统一改指 **BSP 6.6**；NPU 从「T3 放弃」改为「BSP 自带，可用 rknn-toolkit2 跑推理」。
  2. 拉取 BSP 6.6 源码（`rockchip-linux/linux` `stable-6.6`），以 `rk3568-evb1-v10.dts` 为基底重建粤嵌板级 DTS（复用 6.18 阶段的 gmac0 reset / usb2phy / usbdp_phy 等结论；NPU 节点 BSP 已含，启用即可）。
  3. 重编内核 + 外置 FIT + RKDevTool 只烧 boot，验证 BSP 6.6 启动、`rknpu.ko` 加载、`/dev/dri/renderD*` 出现。
- **遗留/风险**：① BSP 非纯主线，与上游有差异、部分上游补丁缺失，但 RK3568 资料最全最稳；② `rknn` 用户态库（`librknnrt`）需另行获取（Rockchip 闭源分发，`airockchip/rknn-toolkit2`）；③ 原 `panel-himax-evb1.c` / `rk3568-evb1-v10-panel.dts` 在 BSP 路线下降级为「备用参考」，屏改由厂内 panel-simple + DTS 点亮。

---

## 2026-08-08（续9）— 内核仓库首次 push 诊断（269 MB 根因）

- **进展**：用户在 WSL `~/linux-rk3568`（torvalds/linux 的 **shallow clone**，`--depth=1 --branch v6.18`）上提交板级 DTS `ce6fcfba`（`arm64: dts: rockchip: add GecEdu RK3568 board`，仅 `Makefile` + `rk3568-gec-v11.dts`），并 push 到 `Leon19960120/linux`（fork）。
- **269 MB 根因（澄清）**：非 DTS 改动大。浅克隆本地只有 v6.18 那一个快照、无历史；而**目标仓库 `Leon19960120/linux` 当时是空的**（无共享历史）→ push 把浅克隆里唯一那棵 v6.18 源码树（96,586 objects / 268.97 MiB）整棵传上去。**空目标 + 浅克隆 = 必传整树**（不是"协商找不到共同历史"，是对面没历史可协商）。
- **验证命令**：`git rev-parse --is-shallow-repository`（预计 `true`）；`git count-objects -vH`（看实际占用）。
- **关键提醒**：① `ce6fcfba` 是**主线 6.18** DTS，本项目已弃 6.18 转 BSP 6.6 → 这笔提交现属"6.18 实验记录"，BSP 6.6 需另开分支另写（DTS 基底不同，gmac0 reset/usb2phy 等结论可复用）。② `fit-image.its` / `*.config` 仍 **untracked**，未进本次 push；`boot.img` 也未 commit → 产物未备份。
- **后续正确做法**：切 BSP 6.6 时 **fork `rockchip-linux/linux`（正经 fork，GitHub 服务端自带完整历史）**，再推 BSP 分支 → 服务器已有 base，只传 DTS diff（几 KB），不会再 269 MB。建议 `fit-image.its` 留元仓库 `docs/porting/`（可 commit）、defconfig 进内核 fork、`boot.img` 等生成物不进 git。

---

（日志持续更新中）

---

## 2026-08-08（续10）— 文档目录重组（按用户 spec 落地）

- **进展**：用户给了一份详细目录 spec + 写作口径（initial board support / 保留错误假设 / 统一英文文件名+中文内容），要求"先盘点迁移表、改动前告知"，并确认 5 项（USB3/6050/1750 已通、英文文件名、内核仓库 `gecedu-rk3568-v6.18`、configs 已从 WSL 复制到根、各设备相关说明.md 忽略、原文件都保留）。随后用户指令"全部开始写吧"。
- **执行（机械迁移 + 逐篇补写，未删任何原文件）**：
  1. 建目录树：`docs/hardware/`、`docs/porting/mainline-6.18/`、`docs/porting/rockchip-6.6/`、`docs/troubleshooting/`、`porting/mainline-6.18/{boot,configs/history}`、`logs/mainline-6.18/{boot,ethernet,usb,i2c}`。
  2. `mv` + `git add -A` 重定位 11 个文件（git 识别为 rename/add），原文件内容保留。
  3. **新写 / 补全** 15 篇：
     - mainline-6.18：`02_kernel_build` / `03_device_tree` / `04_rootfs_compat` / `05_ethernet` / `09_known_issues`（5 篇）
     - hardware：`01_board_overview`（1 篇）
     - troubleshooting：`boot` / `ethernet` / `usb` / `i2c`（4 篇）
     - rockchip-6.6：`01_bsp_setup` / `02_board_dts` / `03_rknpu_rknn`（3 篇，均标注"规划未实测"）
  4. **合并零散素材**：`01_boot_chain.md` 补"附录 A 出厂 boot.img 解包证据" + 修正 2 处迁移后失效内链；`07_i2c_sensors.md` 补"实测读值" + "BH1750 硬件损坏假设被推翻"错误假设保留。
  5. **刷新索引**：重写 `docs/porting/README.md`（含 hardware/troubleshooting/BSP 01-03），修正 `10_debug_notes.md` 头部失效文档引用。
  6. `README.md`（项目入口）早在重组前已重写，含确认状态表（USB3/6050/1750 ✅）+ 仓库分工 + 双路线导航。
- **保留未动**：`docs/development/` 下 `decompiled_rk356x-demo.c` / `reverse_*` / `strings*` / `解包boot.md` / `触摸屏获取不到真实光传感器的值.md`；`docs/notes/` 下两个 `✅` 开头杂记；`辅助文档/` / `hardware/Device Tree/` / `rockchip_test/`。这些按用户"原文件都不要删"保留。
- **关键口径落实**：① 全仓库只写 initial board support / mainline bring-up，不写 full support；② NPU 解释为"mainline 暂缓、转 BSP 6.6"，不单纯写失败；③ 错误假设（BH1750 硬件坏、400kHz 唯一归因）保留不删；④ BSP 三篇均标"规划未实测"。
- **下一步**：所有改动仍**未 commit**（用户此前要求先不提交）。待用户决定提交元仓库；内核仓库 `gecedu-rk3568-v6.18` 的 DTS 实际已在 WSL 验证（ce6fcfba），BSP 6.6 待 fork。
