# 08 - CAN

> 状态：`[BSP-5.10 RUNTIME VERIFIED]` 到 CAN driver interface；SocketCAN 收发仍为 `[PENDING]`。

## 当前状态

最新 5.10.209 启动日志已经出现：

```text
CAN device driver interface
```

这说明 CAN core / driver interface 已经进入运行时路径，`CONFIG_CAN_RK3568` 方向有效。

DTS 中可能包含：

```dts
&can1 {
    pinctrl-names = "default";
    pinctrl-0 = <&can1m0_pins>;
    status = "okay";
};
```

但这仍不足以说明 CAN 物理收发已经完成。

## 验证要求

只有下面链路全部成立后，才能把 CAN 标记为已验证：

```text
kernel CAN config enabled
→ Rockchip CAN driver built / interface appears
→ ip link shows canX
→ SocketCAN configuration succeeds
→ runtime send/receive is verified
```

下一步板端检查：

```bash
ip link
```

若出现 `can0` / `can1`，再继续配置 bitrate 并做 loopback 或实线收发测试。
