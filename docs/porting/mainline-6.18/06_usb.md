# 修复 RK3568（6.18 主线）USB：usb2phy / usbdp_phy 启用

> 适用：主线 6.18 内核 + `rk3568-gec-v11.dts` + 外置 FIT 启动。
> 现象：6.18 启动后所有 USB 控制器 `deferred probe pending: wait for supplier /usb2phy@fe8a0000|fe8b0000/{otg,host}-port`，插 U 盘无反应；dwc3 额外报 `failed to initialize core`。
> 出厂 4.19.232 下 USB 正常 → 硬件没坏，纯 DTS 未启用 phy。

**进度状态（2026-08-08，build #11 验证）**：
- ✅ **USB2 Host 全链路已通**：`usb2phy0/1` 启用 → EHCI/OHCI 起来 → 板载 4 口 Hub 已枚举（`usb 6-1 ... hub 6-1:1.0: 4 ports detected`），插设备走 Mass Storage 正常。
- ✅ **DWC3 / USB3 Host 已通**：启用 `usbdp_phy` 后 `failed to initialize core` 消失；再在 `&usb_host0_xhci` 加 `dr_mode = "host";`（并去掉 `extcon`）根治了 **xhci 注册→移除死循环**。当前 `xhci-hcd.6/7.auto` 各只注册一次，bus 1–4 稳定出现，无循环。
- ⏭️ **USB Gadget / Device（ADB/U盘共享/以太网共享）待做**：rootfs 的 `S50usbdevice` 仍在找 `/sys/kernel/config/usb_gadget/rockchip`（configfs 未挂载 + 内核未开 `CONFIG_USB_CONFIGFS`/`FUNCTIONFS`），全部 `No such file or directory`。这是独立于 Host 的另一半，需要再做；当前锁 `dr_mode="host"` 下不相关。

---

## 1. 原理：USB 为什么全 `deferred probe`

Linux 驱动模型用 **supplier/consumer（供应者/消费者）** 关系。USB 控制器（consumer）在 DTS 里声明它依赖的 phy：

```
&usb_host0_ehci { phys = <&u2phy0_host PHY_TYPE_USB2>; ... }   // EHCI 等 usb2phy0 的 host 子口
&usb_host0_xhci { phys = <&u2phy0_otg ...>, <&usbdp_phy ...>; } // dwc3 的 USB2 + USB3 两路
```

phy 的"供应者"是 `usb2phy@fe8a0000 / fe8b0000` 的**子节点**（`otg-port` / `host-port`）。
mainline `rk3568.dtsi` 里 `&usb2phy0 / &usb2phy1` 默认 `status="disabled"`：

- 父节点不 probe → 子节点不会注册成 phy 设备；
- 于是所有 consumer 一直 `deferred probe pending: wait for supplier ...` → USB 全挂。
- dwc3 额外 `failed to init core`：它的 **USB3 SuperSpeed** 还需要 combo PHY（RK3568 上是 `usbdp_phy`，默认也 disabled），缺了就拿不到 SS phy，core 初始化失败。USB2 那一路也仍要等 `u2phy0_otg`。

**根因 = gec-v11.dts 没启用 usb2phy 与 usbdp_phy**，不是硬件问题。

---

## 2. 板端诊断（只看不改，确认根因）

在 6.18 板端 shell 跑：

```bash
# usb2phy 自己有没有 probe、报什么错
dmesg | grep -iE 'usb2phy|rockchip.*usb|usbdp'

# 当前有没有任何 phy 设备被注册
ls /sys/class/phy/ 2>/dev/null

# DTB 里 usb2phy 节点是不是 disabled
for n in fe8a0000 fe8b0000; do \
  echo "== usb2phy@$n =="; \
  cat /sys/firmware/devicetree/base/usb2phy@$n/status 2>/dev/null | tr -d '\0'; echo; \
done

# USB 控制器 / 控制器列表
ls /sys/class/udc/ 2>/dev/null; lsusb 2>/dev/null
```

**预期（USB2 阶段）**：`ls /sys/class/phy/` 只有 u2phy 系列；`usb2phy@fe8a0000/status` 是 `disabled` → 坐实根因。
**DWC3 阶段追加诊断**：`cat /sys/firmware/devicetree/base/usbdp_phy@fcc00000/status`（应为 `disabled`）+ `dmesg|grep -iE 'usbdp|dwc3'` + `ls /sys/class/phy/`（应无 usb3 设备）→ 坐实 dwc3 缺 SS phy。

---

## 3. DTS 补丁（加到 `rk3568-gec-v11.dts` 末尾）

基于 mainline `rk3568-evb1-v10.dts` 的 USB 段（gec-v11 是其粤嵌派生版），**只启用、不动电气参数**：

```dts
/* ===== USB2 PHY（清除 deferred probe 的关键）===== */
&usb2phy0 {
	status = "okay";
};

&usb2phy0_host {
	status = "okay";
};

&usb2phy0_otg {
	status = "okay";
};

&usb2phy1 {
	status = "okay";
};

&usb2phy1_host {
	status = "okay";
};

/* ===== USB 控制器 ===== */
&usb_host0_ehci { status = "okay"; };   /* fd800000 */
&usb_host0_ohci { status = "okay"; };   /* fd840000 */
&usb_host0_xhci { status = "okay"; };   /* fd000000 = dwc3(OTG/Type-C) */
&usb_host1_ehci { status = "okay"; };   /* fc800000 */
&usb_host1_ohci { status = "okay"; };   /* fc840000 */

/* ===== USB3 SuperSpeed combo PHY（修 dwc3 "failed to init core"）===== */
&usbdp_phy {
	status = "okay";
	rockchip,u3otg0-port = <&u2phy0_otg>;
};
```

> 📌 **关键：mainline 下 `fcc00000` 不是第二个 dwc3。** 出厂 4.19 DTS 里 `fcc00000` 是 `usbdrd`（OTG dwc3），但 6.18 主线把它**重组为 `usbdp_phy`（USB3-DP combo PHY）**——它不再是控制器，而是 dwc3（`fd000000`）的 **USB3 SuperSpeed phy 供应者**。因此 mainline 的修法是「启用 `usbdp_phy`」，**不是**「再加一个 dwc3@fcc00000」。dwc3 拿不到这个 SS phy，core 初始化就失败。

> ⚠️ 应用前确认：
> 1. **未加 `phy-supply = <&vcc5v0_host>`**。evb1 里 host 口靠这个 GPIO 稳压器给 VBUS 供电；若 gec-v11.dts **没有**定义该稳压器，加了会 phandle 解析失败。先这样启用，烧后若插 U 盘没反应（控制器起了但口没电），再补 VBUS 稳压器。
> 2. `usbdp_phy` 标签与 `rockchip,u3otg0-port` 属性名以你 WSL 的 dtsi 为准，先核再改：
>    ```bash
>    grep -n 'usbdp_phy:' arch/arm64/boot/dts/rockchip/rk3568.dtsi
>    grep -n 'rockchip,u3otg' arch/arm64/boot/dts/rockchip/rk3568.dtsi
>    ```
>    若 dtsi 里没 `rockchip,u3otg0-port` 这个属性（更老写法），就只写 `status = "okay";` 即可。
> 3. **若你只要 USB2 OTG**（板子 Type-C 没接 SS 差分线，或暂时不想折腾 USB3），可在 dwc3 节点加 `snps,usb2-only;` 强制 USB2，连 `usbdp_phy` 都不用启用。但 4.19 出厂是开了 USB3 的，建议优先启用 `usbdp_phy` 拿满速。

---

## 4. 重编 dtb → 重打包 FIT → 只烧 boot

在 WSL 内核根目录（`fit-image.its` 已按移植记录复制到内核根，其 fdt 段 incbin 指向 `rk3568-gec-v11.dtb`）：

```bash
# 1) 只重编 dtb（kernel Image 没动，无需重编内核）
make ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- rockchip/rk3568-gec-v11.dtb

# 2) 确保内核根有最新 .its，再重打外置 FIT
cp docs/porting/fit-image.its ./fit-image.its
mkimage -f fit-image.its -E -p 0x800 boot.img

# 3) 自检 FIT 头 totalsize < 0x1000（外置 FIT 必须，否则 Rockchip U-Boot 拒载）
xxd -s 4 -l 4 boot.img     # 第 2 个 32 位 = totalsize，须 < 00001000

# 4) 安全截断 32M：先 stat 确认 <32M 再 truncate；超过说明 dtb 异常，勿截
stat -c%s boot.img
truncate -s 32M boot.img
```

然后 **RKDevTool 只烧 `boot` 一行**（勿动 Loader / parameter）。

---

## 5. 烧后验证

```bash
dmesg | grep -iE 'usb|dwc3|xhci|ehci|phy'
ls /sys/class/phy/          # 应出现 u2phy0_otg / u2phy0_host / u2phy1_host 等
lsusb                       # 应能看到 ehci/xhci 控制器
# 插 U 盘看 sda 枚举；Type-C 口插设备看 dwc3 是否还报 init core
```

**成功标志**：`deferred probe pending` 消失；`ls /sys/class/phy/` 有设备；插 U 盘能 `mount`。

---

## 6. 遗留 / 后续

- 若 host 口控制器起了但无 VBUS 供电 → 在 gec-v11.dts 补 `vcc5v0_host` 类 GPIO 稳压器并加到 `phy-supply`。
- dwc3 Type-C 角色切换（host/device）还需 `extcon = <&usb2phy0_otg>`，如需要再加。
- 此修复与「触摸/WiFi 模块重编」「MIPI-DSI 显示」相互独立，可并行推进。

---

## 7. 已知坑：DWC3 xhci 注册/移除死循环（dr_mode/OTG）

**现象**：启用 `usbdp_phy` 后 `failed to initialize core` 消失，但 `xhci-hcd.N.auto`（`io mem 0xfcc00000`）每 ~200ms 反复 `xHCI Host Controller` → `hub found` → `USB disconnect` → `USB bus deregistered` → 再注册，死循环。

**根因**：不是硬件问题，是软件反复 bind/unbind。两种主因：
1. **rootfs 的 USB Gadget/device 模式服务**（如 `/etc/init.d/S50usbdevice`、`usbdevice`、`functionfs`、`UDC` 报错那条链路）反复试图把 dwc3 切到 device 模式建 gadget，建失败退回 host → host 侧 xhci 不断 register/remove。
2. **`dr_mode="otg"` + `extcon` 的 ID/VBUS 检测抖动**导致角色反复切换。

本质是 dwc3 被当成 OTG 在 host/device 之间横跳。

**验证**：
```bash
dmesg | grep -iE 'dwc3|role|extcon|otg|usb_gadget|UDC|soft_connect'
ps aux 2>/dev/null | grep -iE 'usb|gadget|adb|usbd'
ls /etc/init.d/ | grep -i usb
ls /sys/class/udc/ 2>/dev/null
```

**修复（推荐，一行 DTS 根治）**：当前只要 USB Host，强制 dwc3 仅 host 模式，循环即停：
```dts
&usb_host0_xhci {
    dr_mode = "host";
    /* 暂时拿掉 extcon，避免 OTG 角色抖动；以后做 gadget 再加回 */
};
```
若 dts 里 `&usb_host0_xhci` 自带 `extcon = <&usb2phy0_otg>`，注释掉或整段改成只留 `dr_mode = "host";`。重编 dtb → 重打 FIT → 只烧 boot。

**备选（临时，改 rootfs）**：`/etc/init.d/S50usbdevice stop` 或改名禁用 gadget 服务；但重烧/重启可能复发，DTS 强制 host 才是根治。

**成功标志**：`dmesg` 只剩**一次** xhci 注册；`lsusb -t` 看到稳定 USB3 bus（bus 7/8）；`ls /sys/class/udc/` 为空（host 模式无 UDC）。

**Gadget/Device 模式**：等要做 ADB/U 盘共享/以太网共享时再做对——保留 `dr_mode="otg"` + `extcon`，用 configfs 正确建 gadget，别让出厂脚本乱切。
