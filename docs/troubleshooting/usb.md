# 排障 - USB

> ⚠️ **历史路线（mainline-6.18）**：本页记录 mainline-6.18 阶段的排障，非当前现役路线。
> 现役路线是 Rockchip BSP 5.10（USB2/USB3 已验证，见 `../porting/rockchip-5.10/00_overview.md`）。
> 6.18 特有结论（如 `usbdp_phy` 不存在、`combphy` 启用、`dr_mode` 抖动）不要直接套用到 5.10。

> 对应 6.18 bring-up 文档：`../porting/mainline-6.18/06_usb.md`（含完整 DTS 补丁与原理）。
> 权威 USB 映射见 `../porting/mainline-6.18/03_device_tree.md` §2.2（committed DTS = current software state）。

---

## 1. 所有 USB 控制器 `deferred probe pending`

**现象**：启动后插 U 盘无反应；dmesg 满屏
`deferred probe pending: wait for supplier /usb2phy@fe8a0000|fe8b0000/{otg,host}-port`。

**根因**：mainline `rk3568.dtsi` 里 `&usb2phy0/1` 默认 `disabled` → 父不 probe → 子节点(otg/host-port)
不注册成 phy → 所有 consumer（EHCI/OHCI/xhci/dwc3）一直等 supplier。**非硬件废**（4.19 USB 正常）。

**修复**（加到 `rk3568-gec-v11.dts`）：

```dts
&usb2phy0 { status = "okay"; };
&usb2phy0_host { status = "okay"; };
&usb2phy0_otg { status = "okay"; };
&usb2phy1 { status = "okay"; };
&usb2phy1_host { status = "okay"; };
&combphy0 { status = "okay"; };   /* USB3 SS phy for usb_host0_xhci (fcc00000) */
&combphy1 { status = "okay"; };
&usb_host0_ehci { status = "okay"; };   /* fd800000 */
&usb_host0_ohci { status = "okay"; };   /* fd840000 */
&usb_host1_ehci { status = "okay"; };   /* fd880000 */
&usb_host1_ohci { status = "okay"; };   /* fd8c0000 */
```

> 本树**没有 `usbdp_phy`**。USB3 SS phy 由 `combphy0`（usb_host0_xhci @fcc00000）/ `combphy1`（usb_host1_xhci @fd000000）提供，启用 `combphy0` 与 `combphy1` 即可；不要去加 `usbdp_phy` 节点。
> `usb_host0_xhci`(fcc00000) / `usb_host1_xhci`(fd000000) 在 committed DTS 已 `okay`，
> `dr_mode`/extcon 以 committed DTS 为准（host0 = `peripheral`+`extcon=<&usb2phy0>`；host1 = `host`）。
> 烧后若插 U 盘仍没反应（控制器起了但口没电），再补 VBUS 稳压器（gpio 分配见 `03_device_tree.md` §2.2，NEEDS RE-VERIFICATION）。

---

## 2. dwc3 `failed to initialize core`（USB3 不通）

**现象**：`platform fd000000.usb: deferred probe pending: dwc3: failed to initialize core`（或 `fcc00000`）。

**根因**：dwc3 的 USB3 SuperSpeed 还需 combo PHY（`usb_host0_xhci`→`combphy0`@fe820000，`usb_host1_xhci`→`combphy1`@fe830000，mainline 默认 disabled），缺了拿不到 SS phy。

**修复**：启用 `combphy0`（与 `combphy1`）：
```dts
&combphy0 { status = "okay"; };
&combphy1 { status = "okay"; };
```

> ⚠️ **不存在 `usbdp_phy`**：4.19 里 `fcc00000` 是 `usbdrd`（OTG dwc3），6.18 主线把该地址归给 `usb_host0_xhci`，
> 其 USB3 SS phy 由 `combphy0`（host0）/ `combphy1`（host1）提供。任何「启用 `usbdp_phy`」的指引在本内核树无效（节点不存在，已推翻）。

---

## 3. xhci 注册→移除死循环（dr_mode 抖动）

**现象**：启用 USB3 phy 后 `failed to init core` 消失，但 `xhci-hcd.N.auto` 每 ~200ms 反复
register → `hub found` → `USB disconnect` → `USB bus deregistered` → 再注册。

**根因**：出厂 rootfs 的 USB gadget/device 服务反复把 dwc3 切到 device 模式建 gadget、失败退回 host，
或 `dr_mode="otg"` + `extcon` 的 ID/VBUS 检测抖动导致角色横跳。本质是 dwc3 在 host/device 间横跳。

> ⚠️ **SUPERSEDED DIAGNOSTIC WORKAROUND（历史有效临时手段，非最终结论）**：早期为快速停循环，曾把
> `&usb_host0_xhci` 强制 `dr_mode = "host";` 并去掉 `extcon`，循环即止。**这当时是有效的诊断手段**，
> 但**不是 committed DTS 的最终状态**——已提交 DTS 的 `usb_host0_xhci` 是 `dr_mode="peripheral"` + `extcon=<&usb2phy0>`。
> 若在新内核上再遇该死循环，这条 `dr_mode="host"` 临时改法**仍可用于定位**（确认是角色抖动后，再决定修 rootfs gadget 服务
> 还是用 extcon 正确切角色），但**不要写死成"正确 DTS"**；生产状态以 committed DTS（peripheral + extcon）为准。

**成功标志**：`dmesg` 只剩**一次** xhci 注册；`lsusb -t` 看到稳定 USB3 bus；`ls /sys/class/udc/` 为空（host 模式无 UDC）。

---

## 4. Gadget / Device 模式（ADB 等）未收口 —— kernel 已验证，只差 userspace ADB

USB Gadget（ADB / U 盘共享 / 以太网共享）是独立于 Host 的另一半。**Kernel gadget plumbing 已验证**：
实测 `/sys/class/udc/fcc00000.usb` 出现、`configfs` gadget 已建、`ffs.adb` 与 FunctionFS endpoints 就绪，
内核 `CONFIG_USB_CONFIGFS=y` 等均已开启。**真正卡住的是旧 userspace 的 `adbd`**：`/usr/bin/adbd` 启动后尝试 `tcp:5037` 即退出，adbd 未完成基于 FunctionFS 的 userspace 启动流程。详细状态表如下（**不要再回头查内核 config**）：

| 层级 | 当前状态 |
|------|----------|
| `fcc00000` peripheral role（`dr_mode="peripheral"`+`extcon`） | ✅ configured |
| UDC `fcc00000.usb` | ✅ verified |
| ConfigFS（`/sys/kernel/config/usb_gadget`） | ✅ verified |
| FunctionFS `ffs.adb` | ✅ verified |
| FunctionFS endpoints | ✅ verified |
| `adbd` userspace 启动 | ⚠️ incomplete |
| PC 端最终 `adb devices` | ❌ not completed |
| 当前工作状态 | ⏸ paused |

- **Kernel gadget plumbing: VERIFIED**（`CONFIG_USB_GADGET=y` / `CONFIG_USB_LIBCOMPOSITE=y` / `CONFIG_USB_F_FS=y` / `CONFIG_USB_CONFIGFS=y` / `CONFIG_USB_CONFIGFS_F_FS=y` / `CONFIG_CONFIGFS_FS=y`）。
- **ConfigFS / FunctionFS: VERIFIED**（`ffs.adb` 与 endpoints 就绪）。
- **ADB userspace: INCOMPLETE** —— 观察 `/usr/bin/adbd` 启动后尝试 `tcp:5037` 即退出。**Root cause: NOT FULLY RESOLVED**。
- **Factory/userspace 集成脚本差异**：若 rootfs 的 `/etc/init.d/S50usbdevice` 引用旧 `/sys/kernel/config/usb_gadget/rockchip` 路径，这只算 **userspace 集成差异**，**不得**作为「内核 `CONFIG_USB_CONFIGFS` 未启用 / configfs 不存在」的证据（那一层已实测为 VERIFIED）。
- 需另做：换一个能正确走 USB FunctionFS 启动路径的 `adbd` / gadget 用户态，用 `extcon` 正确切角色。见 `../porting/mainline-6.18/08_adb_gadget.md`。

---

## 5. 板端诊断命令（只看不改）

```bash
dmesg | grep -iE 'usb|dwc3|xhci|ehci|phy|combphy'
ls /sys/class/phy/            # USB2 阶段应有 u2phy0_otg/host 等；DWC3 阶段应再有 combphy
ls /sys/class/udc/ 2>/dev/null
lsusb
```
