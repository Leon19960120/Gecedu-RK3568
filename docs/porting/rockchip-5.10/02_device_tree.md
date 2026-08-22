# 02 - Device Tree 笔记

> 状态：混合状态。每个节点都要分别判断 DTS、bind、subsystem 和 runtime evidence。

## 当前 DTS

当前目标文件：

```text
kernel/arch/arm64/boot/dts/rockchip/rk3568-gec-v11-linux.dts
```

根据当前项目笔记，已知 include 链如下：

```text
rk3568-gec-v11-linux.dts
├── rk3568-gec-v11.dtsi          ← 板级 override 层（&route_dsi0、sdmmc1、can 等在这里）
│   ├── rk3568.dtsi
│   └── rk3568-evb-gec.dtsi      ← 基础外设（&route_hdmi 等在这里）
├── rk3568-linux.dtsi
└── <dt-bindings/display/rockchip_vop.h>
```

实际修改前仍应回到 SDK 工作树确认 include 关系，避免改到了非运行路径。

## 证据层级

每个外设都按下面的链路判断：

```text
source DTS node
→ built DTB contains node
→ running DTB contains node
→ bus device/client exists
→ driver bound
→ subsystem registered
→ runtime function verified
```

不要因为 DTS 中出现 `status = "okay"` 就直接把功能写成已验证。`okay` 只说明设备树意图，不等于内核已绑定驱动，也不等于用户态功能可用。

## 已知 DTB 陷阱

项目曾经启动到 `Rockchip RK3568 EVB1 DDR4 V10 Board`，这通常表示 DTB 路径错误或 boot image 过期。

当前目标运行时 model 应为：

```text
Rockchip RK3568 GEC DDR4 V10 Board
```

## VOP Route 分层覆盖

当前板级 DTS 使用 override 分层，不是所有显示 route 都写在同一个文件里：

```text
rk3568-gec-v11.dtsi
└── &route_dsi0 {
        status = "okay";
        connect = <&vp0_out_dsi0>;
    };

rk3568-evb-gec.dtsi
└── &route_hdmi {
        status = "okay";
        connect = <&vp1_out_hdmi>;
    };
```

已验证的正确分配：

```text
DSI0  -> VP0
HDMI  -> VP1
```

如果 `route_dsi0` 被写成 `vp1_out_dsi0`，会与 `route_hdmi` 抢 VP1，导致 U-Boot 阶段不走正确 DSI logo 路径。当前修复是让 DSI0 回到 `vp0_out_dsi0`，HDMI 保持 `vp1_out_hdmi`；HDMI 未接时显示 disconnected，不影响 DSI。
