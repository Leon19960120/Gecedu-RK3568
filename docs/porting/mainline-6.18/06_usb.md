# 06 - USB bring-up（USB2 Host + USB3 DWC3）

> 适用：主线 6.18 内核 + `rk3568-gec-v11.dts` + 外置 FIT 启动。
> 权威映射见 `03_device_tree.md` §2.2（committed DTS 为 current software state；原理图 / 实机为佐证）。
> 现象：6.18 启动后所有 USB 控制器 `deferred probe pending: wait for supplier /usb2phy@fe8a0000|fe8b0000/{otg,host}-port`，插 U 盘无反应；dwc3 额外报 `failed to initialize core`。
> 出厂 4.19.232 下 USB 正常 → 硬件没坏，纯 DTS 未启用 phy。

**进度状态（2026-08-08，build #11 验证）**：
- ✅ **USB2 Host 全链路已通**：`usb2phy0/1` 启用 → EHCI/OHCI 起来 → 板载 4 口 Hub 已枚举（`usb 6-1 ... hub 6-1:1.0: 4 ports detected`），插设备走 Mass Storage 正常。
- ✅ **DWC3 / USB3 Host 已通**：启用 `combphy0`（usb_host0_xhci @fcc00000 的 USB3 SS phy）/ `combphy1`（usb_host1_xhci @fd000000 的 USB3 SS phy）后 `failed to initialize core` 消失；`xhci-hcd` 稳定注册，bus 1–4 正常出现。
- ⏸️ **USB Gadget / Device（ADB/U 盘共享/以太网共享）：kernel 侧已验证，userspace ADB 未收口（PAUSED）**。实测 `/sys/class/udc/fcc00000.usb` 出现、`configfs` gadget 已建、`ffs.adb` 与 FunctionFS endpoints 就绪，内核 `CONFIG_USB_CONFIGFS=y` 等均已开启。**真正卡住的是旧 userspace 的 `adbd`**：`/usr/bin/adbd` 启动后尝试 `tcp:5037` 即退出，adbd 未完成基于 FunctionFS 的 userspace 启动流程。详细状态见 §6「ADB/Gadget 实测状态」；重启推进见 `08_adb_gadget.md`。

---

## 1. 当前 committed DTS 的 USB 状态（权威，勿自行改写）

`gecedu-rk3568-v6.18` 的 `rk3568-gec-v11.dts` 实测：

| 地址 | 节点 | 角色 | 已确认属性 |
|------|------|------|-----------|
| `fcc00000` | `usb_host0_xhci`（DWC3 DRD） | Type-C / OTG / ADB 侧 | `dr_mode="peripheral"` + `extcon=<&usb2phy0>` + `status="okay"` |
| `fd000000` | `usb_host1_xhci`（DWC3 Host） | 第二路 USB3 Host | `dr_mode="host"` + `status="okay"` |
| `fd800000` | `usb_host0_ehci` | USB2 Host EHCI | `status="okay"` |
| `fd840000` | `usb_host0_ohci` | USB2 Host OHCI | `status="okay"` |
| `fd880000` | `usb_host1_ehci` | 第二路 EHCI | `status="okay"` |
| `fd8c0000` | `usb_host1_ohci` | 第二路 OHCI | `status="okay"` |

- **USB3 SuperSpeed phy**：`usb_host0_xhci`(@fcc00000) 的 SS phy 由 **`combphy0`(@fe820000)** 提供；`usb_host1_xhci`(@fd000000) 的 SS phy 由 **`combphy1`(@fe830000)** 提供。`combphy0` 与 `combphy1` 在 committed DTS 均 `status="okay"`。
- **本内核树没有 `usbdp_phy` 节点**。任何"启用 `usbdp_phy`"的指引都是错的（见 §6 澄清）。

> ⚠️ **VBUS GPIO 冲突（NEEDS RE-VERIFICATION）**：committed DTS 里 `vcc5v0_usb_host` = gpio0 **PA6**、`vcc5v0_usb_otg` = gpio0 **PA5**；而 4.19 出厂映射方向相反（HOST=A5 / OTG=A6）。两来源并列、统一标 `NEEDS RE-VERIFICATION`，详见 `03_device_tree.md` §2.2。本文件不修改 VBUS 分配。

---

## 2. 原理：USB 为什么全 `deferred probe`

Linux 驱动模型用 **supplier/consumer** 关系。USB 控制器（consumer）在 DTS 里声明它依赖的 phy：

```
&usb_host0_ehci { phys = <&u2phy0_host PHY_TYPE_USB2>; ... }
&usb_host0_xhci { phys = <&u2phy0_otg ...>, <&combphy0 ...>; }  // host0: USB2(u2phy0_otg) + USB3 SS(combphy0)
&usb_host1_xhci { phys = <&combphy1 ...>; }                    // host1: USB3 SS phy 由 combphy1 提供
```

phy 的"供应者"是 `usb2phy@fe8a0000 / fe8b0000` 的**子节点**（`otg-port` / `host-port`），以及 `combphy0`（host0 的 USB3 SS phy）/ `combphy1`（host1 的 USB3 SS phy）。
mainline `rk3568.dtsi` 里 `&usb2phy0 / &usb2phy1` 默认 `status="disabled"`，`&combphy0/1` 也默认不启用：

- 父节点不 probe → 子节点不会注册成 phy 设备；
- 于是所有 consumer 一直 `deferred probe pending: wait for supplier ...` → USB 全挂。
- dwc3 额外 `failed to init core`：它的 **USB3 SuperSpeed** 还需要 combo phy（`usb_host0_xhci`→`combphy0`@fe820000，`usb_host1_xhci`→`combphy1`@fe830000，均默认 disabled），缺了就拿不到 SS phy，core 初始化失败。USB2 那一路也仍要等 `u2phy0_otg`。

**根因 = gec-v11.dts 没启用 usb2phy 与 combphy0/combphy1**，不是硬件问题。

---

## 3. 板端诊断（只看不改，确认根因）

在 6.18 板端 shell 跑：

```bash
# usb2phy 自己有没有 probe、报什么错
dmesg | grep -iE 'usb2phy|rockchip.*usb|combphy'

# 当前有没有任何 phy 设备被注册
ls /sys/class/phy/ 2>/dev/null

# DTB 里 usb2phy / combphy 节点是不是 disabled
for n in fe8a0000 fe8b0000; do \
  echo "== usb2phy@$n =="; \
  cat /sys/firmware/devicetree/base/usb2phy@$n/status 2>/dev/null | tr -d '\0'; echo; \
done
cat /sys/firmware/devicetree/base/combphy@fe820000/status 2>/dev/null | tr -d '\0'   # combphy0 (usb_host0_xhci 的 SS phy)
cat /sys/firmware/devicetree/base/combphy@fe830000/status 2>/dev/null | tr -d '\0'   # combphy1 (usb_host1_xhci 的 SS phy)

# USB 控制器 / 控制器列表
ls /sys/class/udc/ 2>/dev/null; lsusb 2>/dev/null
```

**预期（USB2 阶段）**：`ls /sys/class/phy/` 只有 u2phy 系列；`usb2phy@fe8a0000/status` 是 `disabled` → 坐实根因。
**DWC3 阶段追加诊断**：`cat /sys/firmware/devicetree/base/combphy@fe820000/status`（combphy0，应为 `disabled`）+ `cat .../combphy@fe830000/status`（combphy1，应为 `disabled`）+ `dmesg|grep -iE 'combphy|dwc3'` + `ls /sys/class/phy/`（应无 usb3 设备）→ 坐实 dwc3 缺 SS phy。

---

## 4. DTS 补丁（加到 `rk3568-gec-v11.dts` 末尾，对齐 committed DTS）

基于 mainline `rk3568-evb1-v10.dts` 的 USB 段（gec-v11 是其粤嵌派生版），**只启用、不动电气参数**：

```dts
/* ===== USB2 PHY（清除 deferred probe 的关键）===== */
&usb2phy0 { status = "okay"; };
&usb2phy0_host { status = "okay"; };
&usb2phy0_otg { status = "okay"; };
&usb2phy1 { status = "okay"; };
&usb2phy1_host { status = "okay"; };

/* ===== USB3 SuperSpeed combo PHY（修 dwc3 "failed to initialize core"）===== */
&combphy0 { status = "okay"; };
&combphy1 { status = "okay"; };

/* ===== USB 控制器（committed DTS 已 okay，此处显式列出仅作核对参考）===== */
&usb_host0_ehci { status = "okay"; };   /* fd800000 */
&usb_host0_ohci { status = "okay"; };   /* fd840000 */
&usb_host1_ehci { status = "okay"; };   /* fd880000 */
&usb_host1_ohci { status = "okay"; };   /* fd8c0000 */
/* usb_host0_xhci (fcc00000) / usb_host1_xhci (fd000000) 在 committed DTS 已 okay：
   dr_mode / extcon 以 committed DTS 为准（host0 = peripheral + extcon=<&usb2phy0>；
   host1 = host），不要自行改成 dr_mode="host"。 */
```

> 📌 **关键澄清：本树没有 `usbdp_phy`。** 出厂 4.19 DTS 里 `fcc00000` 是 `usbdrd`（OTG dwc3）；6.18 主线把该地址归给 `usb_host0_xhci`（DWC3 DRD），其 USB3 SS phy 由 `combphy0`（host0）/ `combphy1`（host1）提供，**不是**某个名为 `usbdp_phy` 的节点。因此 mainline 的正确修法是「启用 `combphy0`/`combphy1` 提供 SS phy」，**不是**「启用 `usbdp_phy`」——后者在本内核树根本不存在，是早期文档的错误结论（已推翻）。
>
> ⚠️ **VBUS 稳压器**：committed DTS 通过 `vcc5v0_usb_host` / `vcc5v0_usb_otg`（`phy-supply` 挂在 `usb2phy0_host` / `usb2phy0_otg`）供 VBUS。若你的 DTS 副本缺这两个稳压器定义，先启用上述 phy 节点即可；烧后若插 U 盘没反应（控制器起了但口没电），再补 VBUS 稳压器（见 §7 遗留）。

---

## 5. 重编 dtb → 重打包 FIT → 只烧 boot

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

## 6. 已知坑：xhci 注册→移除死循环（dr_mode 抖动）

**现象**：启用 USB3 phy 后 `failed to initialize core` 消失，但 `xhci-hcd.N.auto`（`io mem 0xfcc00000`）每 ~200ms 反复 `xHCI Host Controller` → `hub found` → `USB disconnect` → `USB bus deregistered` → 再注册，死循环。

**根因**：不是硬件问题，是软件反复 bind/unbind。两种主因：
1. **rootfs 的 USB Gadget/device 模式服务**（如 `/etc/init.d/S50usbdevice`、`usbdevice`、`functionfs`、`UDC` 报错那条链路）反复试图把 dwc3 切到 device 模式建 gadget，建失败退回 host → host 侧 xhci 不断 register/remove。
2. **`dr_mode="otg"` + `extcon` 的 ID/VBUS 检测抖动**导致角色反复切换。

> ⚠️ **SUPERSEDED DIAGNOSTIC WORKAROUND（历史有效临时手段，非最终结论）**：早期为快速停循环，曾把 `&usb_host0_xhci` 强制 `dr_mode = "host";` 并去掉 `extcon`，循环即止。这**当时是有效的诊断手段**，但**不是 committed DTS 的最终状态**——已提交 DTS 的 `usb_host0_xhci` 是 `dr_mode="peripheral"` + `extcon=<&usb2phy0>`（OTG/ADB 侧）。若你在新内核上再遇到该死循环，这条 `dr_mode="host"` 临时改法**仍可用来定位**（确认是角色抖动后再决定是修 rootfs gadget 服务还是用 extcon 正确切角色），但**不要把它当成"正确 DTS"写死**；生产状态以 committed DTS（peripheral + extcon）为准。

**验证（诊断用）**：
```bash
dmesg | grep -iE 'dwc3|role|extcon|otg|usb_gadget|UDC|soft_connect'
ps aux 2>/dev/null | grep -iE 'usb|gadget|adb|usbd'
ls /etc/init.d/ | grep -i usb
ls /sys/class/udc/ 2>/dev/null
```

**Gadget/Device 模式（当前状态 PAUSED：kernel 侧已验证，只差 userspace ADB）**：

实测已验证的链路（**不要再回头查内核 config**，这一层已经通了）：

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

- **Kernel gadget plumbing: VERIFIED** —— `CONFIG_USB_GADGET=y` / `CONFIG_USB_LIBCOMPOSITE=y` / `CONFIG_USB_F_FS=y` / `CONFIG_USB_CONFIGFS=y` / `CONFIG_USB_CONFIGFS_F_FS=y` / `CONFIG_CONFIGFS_FS=y` 全部开启。
- **ConfigFS / FunctionFS: VERIFIED** —— `ffs.adb` 与 endpoints 就绪。
- **ADB userspace: INCOMPLETE** —— 观察 `/usr/bin/adbd` 启动后尝试 `tcp:5037` 即退出，adbd 未完成预期的基于 FunctionFS 的 userspace 启动流程。**Root cause: NOT FULLY RESOLVED**。
- **Factory/userspace 集成脚本差异**：本 Buildroot rootfs 的 `/etc/init.d/S50usbdevice`（若存在）引用的是旧 `/sys/kernel/config/usb_gadget/rockchip` 路径，与 mainline configfs 布局不一致——这只算 **userspace 集成差异**，**不得**作为「内核 `CONFIG_USB_CONFIGFS` 未启用 / configfs 不存在」的证据（那一层已实测为 VERIFIED）。
- 重启推进见 `08_adb_gadget.md`。保留 `dr_mode="peripheral"` + `extcon`，勿让出厂脚本乱切角色。

---

## 7. 烧后验证

```bash
dmesg | grep -iE 'usb|dwc3|xhci|ehci|phy|combphy'
ls /sys/class/phy/          # 应出现 u2phy0_otg / u2phy0_host / u2phy1_host 等 + combphy
lsusb                       # 应能看到 ehci/xhci 控制器
# 插 U 盘看 sda 枚举；Type-C 口插设备看 dwc3 是否还报 init core
```

**成功标志**：`deferred probe pending` 消失；`ls /sys/class/phy/` 有设备；插 U 盘能 `mount`。

**遗留 / 后续**：
- 若 host 口控制器起了但无 VBUS 供电 → 在 DTS 补 `vcc5v0_usb_host` 类 GPIO 稳压器并加到 `phy-supply`（gpio 分配见 `03_device_tree.md` §2.2，NEEDS RE-VERIFICATION）。
- dwc3 Type-C 角色切换（host/device）靠 `extcon = <&usb2phy0_otg>`，committed DTS 已含；做 Gadget 时确认 configfs 与 `CONFIG_USB_CONFIGFS`/`FUNCTIONFS` 已开。
- 此修复与「触摸/WiFi 模块重编」「MIPI-DSI 显示」相互独立，可并行推进。
