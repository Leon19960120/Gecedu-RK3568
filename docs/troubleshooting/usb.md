# Troubleshooting - USB

> 对应 bring-up 文档：`../porting/mainline-6.18/06_usb.md`（含完整 DTS 补丁与原理）。

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
&usb_host0_ehci { status = "okay"; };   /* fd800000 */
&usb_host0_ohci { status = "okay"; };   /* fd840000 */
&usb_host0_xhci { status = "okay"; };   /* fd000000 = dwc3(OTG/Type-C) */
&usb_host1_ehci { status = "okay"; };   /* fc800000 */
&usb_host1_ohci { status = "okay"; };   /* fc840000 */
```

> 故意未加 `phy-supply = <&vcc5v0_host>`：若 gec-v11.dts 无该稳压器定义，加了会 phandle 解析失败。
> 烧后若插 U 盘仍没反应（控制器起了但口没电），再补 VBUS 稳压器。

---

## 2. dwc3 `failed to initialize core`（USB3 不通）

**现象**：`platform fd000000.usb: deferred probe pending: dwc3: failed to initialize core`。

**根因**：dwc3 的 USB3 SuperSpeed 还需 combo PHY（`usbdp_phy`，mainline 默认 disabled），缺了拿不到 SS phy。

**⚠️ 关键：mainline 下 `fcc00000` 不是第二个 dwc3。**
厂内 4.19 里 `fcc00000` 是 `usbdrd`（OTG dwc3）；但 6.18 主线把它**重组为 `usbdp_phy`（USB3-DP combo PHY）**，
是 `fd000000` dwc3 的 **USB3 SS phy 供应者**。修法是「启用 `usbdp_phy`」，**不是**「再加 dwc3@fcc00000」。

**修复**：

```dts
&usbdp_phy {
    status = "okay";
    rockchip,u3otg0-port = <&u2phy0_otg>;
};
```

> 应用前先核对 dtsi 标签/属性名：
> `grep -n 'usbdp_phy:' arch/arm64/boot/dts/rockchip/rk3568.dtsi`
> `grep -n 'rockchip,u3otg' arch/arm64/boot/dts/rockchip/rk3568.dtsi`
> 若 dtsi 无 `rockchip,u3otg0-port` 属性（更老写法），只写 `status = "okay";` 即可。
> 备选：若只要 USB2 OTG，dwc3 节点加 `snps,usb2-only;` 即可不依赖 usbdp_phy。

---

## 3. xhci 注册→移除死循环（dr_mode 抖动）

**现象**：启用 `usbdp_phy` 后 `failed to init core` 消失，但 `xhci-hcd.N.auto` 每 ~200ms 反复
register → `hub found` → `USB disconnect` → `USB bus deregistered` → 再注册。

**根因**：出厂 rootfs 的 USB gadget/device 服务反复把 dwc3 切到 device 模式建 gadget、失败退回 host，
或 `dr_mode="otg"` + `extcon` 的 ID/VBUS 检测抖动导致角色横跳。本质是 dwc3 在 host/device 间横跳。

**根治**（当前只要 Host，一行 DTS）：

```dts
&usb_host0_xhci {
    dr_mode = "host";
    /* 暂拿掉 extcon，避免 OTG 角色抖动；做 gadget 时再加回 */
};
```

**成功标志**：`dmesg` 只剩**一次** xhci 注册；`lsusb -t` 看到稳定 USB3 bus；`ls /sys/class/udc/` 为空（host 模式无 UDC）。

---

## 4. Gadget / Device 模式（ADB 等）待做

USB Gadget（ADB / U 盘共享 / 以太网共享）是独立于 Host 的另一半：rootfs 的 `S50usbdevice` 仍在找
`/sys/kernel/config/usb_gadget/rockchip`（configfs 未挂载 + 内核未开 `CONFIG_USB_CONFIGFS`/`FUNCTIONFS`）。
需另做：开 configfs、建 gadget、用 `extcon` 正确切角色。见 `../porting/mainline-6.18/08_adb_gadget.md`。

---

## 5. 板端诊断命令（只看不改）

```bash
dmesg | grep -iE 'usb|dwc3|xhci|ehci|phy'
ls /sys/class/phy/            # USB2 阶段应有 u2phy0_otg/host 等；DWC3 阶段应再有 usb3 设备
ls /sys/class/udc/ 2>/dev/null
lsusb
```
