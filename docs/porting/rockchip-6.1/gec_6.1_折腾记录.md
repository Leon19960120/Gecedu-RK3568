# GEC RK3568 6.1 内核折腾记录

> 方向：LubanCat SDK + RK3568 GEC DDR4 V10 板，编译/启动 6.1 内核（kernel-6.1）
> 本文件只记录 6.1 方向的内容。早期 5.10 方向的折腾不在此文件，未删除。
>
> **现状提示**：文中 2026-08-24 的 `rk3568-gec-v11-*` 文件名是当日记录。当前 6.1 编译目标已经改为 `rk3568-evb1-gec-v11-linux.dtb`，并使用 `rk3568-evb1-gec-v11-linux.dts`、`rk3568-evb1-gec-v11.dtsi`、`rk3568-evb-gec.dtsi` 三个 GEC 派生层；旧的 `rk3568-gec-v11-linux.dts` / `.dtsi` 已清理。当前结构以 `01_dts_override.md` 为准。

---

## 2026-08-24 13:18 — 6.1 内核首次成功启动验证

### 编译链路
- SDK: `~/lubancat-linux-sdk`
- 板型配置: `device/rockchip/.chips/rk3566_rk3568/rockchip_rk3568_gec_defconfig`
- 切换内核版本：把 `kernel` 软链接指向 `kernel-6.1`
  ```bash
  cd ~/lubancat-linux-sdk && rm kernel && ln -s kernel-6.1 kernel
  ```
- `./build.sh defconfig` 选 20 (gec) 后显示 `Using current kernel version(6.1)`
- 工具链：aarch64 GCC 10.3.1（`prebuilts/gcc/linux-x86/aarch64/gcc-arm-10.3-2021.07-x86_64-aarch64-none-linux-gnu`）
- 最终生效的内核 defconfig：`rockchip_linux_defconfig`（gec config 未设 `RK_KERNEL_CFG`，落到 Kconfig 默认）
- dtb 生成走 `make rk3568-gec-v11-linux.img`（通配规则找 `.dts`），**不需要**在 `rockchip/Makefile` 加 dtb-y 条目

### dts 文件关系（6.1）
```
rk3568-gec-v11-linux.dts
  └─ #include "rk3568-gec-v11.dtsi"
        └─ #include "rk3568-evb-gec.dtsi"   ← 从 5.10 复制覆盖过来的
```
- `rk3568-evb-gec.dtsi` 由 5.10 版本（8/23 修改版）直接 cp 覆盖到 6.1（8/24 执行）
- 覆盖前 diff 显示 5.10 与 6.1 两份已分叉：5.10 用 `simple-audio-card`/`#sound-dai-cells=<0>`/`pwm11`/`vp1`；6.1 原版用 `multicodecs-card`+`hp-det-gpio`/`#sound-dai-cells=<1>`/`pwm7`/`vp0`
- 用户确认：直接覆盖（5.10 写法为准）

### 启动结果：成功 ✅
- `Linux version 6.1.99 ... #8 SMP Mon Aug 24 13:12:20 CST 2026`
- `Machine model: Rockchip RK3568 GEC DDR4 V10 Board`
- 4 核全起，根文件系统挂载，shell 可用

### 报错分类

#### 一、功能受影响（需修）
1. **MIPI DSI 屏不显示 / framebuffer 打不开**
   ```
   panel-simple-dsi fe060000.dsi.0: not found firmware desc data, using defaults
   panel-simple-dsi fe060000.dsi.0: Expected bpc in {6,8} but got: 0
   Starting launcher: Error: cannot open framebuffer device: No such file or directory
   ```
   面板 bpc=0，launcher 开不了 framebuffer。最可能是 5.10 的 panel 节点字段在 6.1 `panel-simple-dsi` 绑定下不匹配。待查。

2. **耳机检测丢失**
   ```
   rockchip_headset rk-headset: Can not read property hook_gpio
   rockchip_headset rk-headset: have not set adc chan
   ```
   因为覆盖了 6.1 原版的 `multicodecs-card`+`hp-det-gpio`+`hp_det` pinctrl，换成 5.10 的 `simple-audio-card`。音频本身可用（`#1: rockchip,rk809-codec`），但耳机插拔检测不可用。

3. **USB gadget 复合功能创建失败**
   ```
   mkdir: cannot create directory '.../functions/uac1.gs0': No such file or directory
   (uac2.gs0 / mtp.gs0 / rndis.gs0 / hid.usb0 同样)
   ```
   内核未编入对应 USB 功能（或模块未加载）。adb/mtp/rndis 等不可用。不需要可忽略。

#### 二、无害噪声（不影响启动，常见）
- `fiq_debugger ... IRQ fiq not found` — 未用 FIQ 调试
- `gpio-regulator ... active low - ignored`
- `rtc rtc1: invalid alarm value: 2026-08-24T33:42:00` — pcf8563 闹钟越界
- `Goodix-TS ... I2C communication failure: -6` — 触摸 IC 未应答
- `rk817-battery/charger: Failed to locate of_node` — dts 无电池节点
- `VOP ... failed to init opp info / no regulator (vop)` — 显示 DVFS 未配
- `RKNPU ... IRQ npu_irq not found` — NPU 中断未配
- `dw-mipi-dsi ... failed to find panel or bridge: -517` — deferred probe，后续绑定成功
- `cfg80211: failed to load regulatory.db` — 无 WiFi 国家码库
- `mali ... power_model DT node matching ...` — 未配 GPU 功耗模型
- `reserved logo memory should be aligned` — kernel logo 不显示
- `EXT4 ... Wrong fs type(ext2) for mmcblk0p7/p9` — fstab 类型写错
- `S36load_wifi_modules: can't create .../rfkill1/state` — WiFi 脚本路径问题

### 下一步待办
- [ ] 查 `panel-simple-dsi` bpc=0 / framebuffer 打不开（屏幕不亮，最高优先级）
- [ ] 视需要恢复 6.1 的 `multicodecs-card`+`hp-det-gpio` 耳机检测
- [ ] 视需要开启 USB gadget 功能（uac2/mtp/rndis）
