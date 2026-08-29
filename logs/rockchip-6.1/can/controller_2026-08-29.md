# BSP 6.1 RK3568 CAN1 控制器原始证据摘要（2026-08-29）

## 源码环境

```text
SDK: /home/hyl/lubancat-linux-sdk
Kernel: /home/hyl/lubancat-linux-sdk/kernel-6.1
Kernel release: 6.1.99
Board: Rockchip RK3568 GEC DDR4 V11 Board
SoC node: can1 / can@fe580000
Runtime netdev: can0
```

## 初始失败证据

```text
[    2.429813] CAN device driver interface
[    3.226504] can: controller area network core
[    3.226616] NET: Registered PF_CAN protocol family
[    3.226653] can: raw protocol
[    3.226687] can: broadcast manager protocol
[    3.226727] can: netlink gateway - max_hops=1
```

同期 `ip link show` 只有 `lo`、`eth0` 和 `wlan0`，没有 CAN 网络接口。

判定：CAN 协议栈存在，但硬件控制器未注册。

## 配置根因

初始 `.config`：

```text
CONFIG_CAN_DEV=y
CONFIG_CAN_CALC_BITTIMING=y
# CONFIG_CAN_ROCKCHIP is not set
# CONFIG_CANFD_ROCKCHIP is not set
```

源码匹配：

```text
rk356x.dtsi compatible: rockchip,rk3568-can-2.0
rockchip_canfd.c match: rockchip,rk3568-can-2.0
Makefile: obj-$(CONFIG_CANFD_ROCKCHIP) += rockchip_canfd.o
```

## 最终 defconfig 与 .config

维护 defconfig：

```text
CONFIG_CAN=y
CONFIG_CANFD_ROCKCHIP=y
```

最终 `.config`：

```text
CONFIG_CAN=y
CONFIG_CAN_RAW=y
CONFIG_CAN_BCM=y
CONFIG_CAN_GW=y
CONFIG_CAN_DEV=y
CONFIG_CAN_NETLINK=y
CONFIG_CAN_CALC_BITTIMING=y
CONFIG_CANFD_ROCKCHIP=y
```

## 最终 GEC DTS

```dts
&can1 {
    compatible = "rockchip,rk3568-can-2.0";
    assigned-clocks = <&cru CLK_CAN1>;
    assigned-clock-rates = <200000000>;
    pinctrl-names = "default";
    pinctrl-0 = <&can1m0_pins>;
    status = "okay";
};
```

Pinmux：

```text
can1m0 RX = GPIO1_A0, function 3
can1m0 TX = GPIO1_A1, function 3
```

## 板端成功证据

```text
2: can0: <NOARP,ECHO> mtu 16 qdisc noop state DOWN mode DEFAULT group default qlen 10
    link/can
```

配置后：

```text
2: can0: <NOARP,UP,LOWER_UP,ECHO> mtu 16 qdisc pfifo_fast state UP mode DEFAULT group default qlen 10
    link/can
    can state ERROR-ACTIVE (berr-counter tx 0 rx 0) restart-ms 1
          bitrate 500000 sample-point 0.875
          tq 50 prop-seg 17 phase-seg1 17 phase-seg2 5 sjw 1
          rockchip_canfd: tseg1 1..128 tseg2 1..128 sjw 1..128 brp 1..256 brp-inc 2
          clock 200000000
```

## 判定

```text
[CAN CONTROLLER RUNTIME VERIFIED]
[CAN PHYSICAL BUS PENDING]
```

已验证控制器驱动、SocketCAN 注册、200 MHz 时钟和 500 kbit/s 位时序。尚无 `candump/cansend` 内部回环或双节点物理收发证据。

## LVGL CAN Test 报错证据

应用源码：

```c
system("ip link set can0 down");
system("ip link set can0 type can bitrate 500000 dbitrate 500000 fd on");
system("ip link set can0 up");
```

板端输出：

```text
RTNETLINK answers: Operation not supported
btn index: 14, text: CAN Test
```

驱动映射：

```text
rockchip,rk3568-can-2.0 -> ROCKCHIP_RK3568_CAN_MODE
```

该 mode 的 `ctrlmode_supported`：

```text
CAN_CTRLMODE_BERR_REPORTING
CAN_CTRLMODE_LISTENONLY
CAN_CTRLMODE_LOOPBACK
CAN_CTRLMODE_3_SAMPLES
```

其中没有 `CAN_CTRLMODE_FD`。判定：应用请求 `fd on` 时驱动返回 `-EOPNOTSUPP`；`dbitrate` 也是 CAN-FD 数据段参数，应一并删除。经典 CAN 的 `bitrate 500000` 已由板端单独验证。

## LVGL CAN filter 证据

原代码：

```c
rfilter[0].can_id = -1;
rfilter[0].can_mask = CAN_SFF_MASK;
```

`-1` 会置位 `CAN_INV_FILTER`。Linux 6.1 将该项登记到 `RX_INV`，匹配条件为：

```text
(received_can_id & mask) != filtered_can_id
```

所以它实际排除低 11 位为 `0x7FF` 的帧，不是“全部帧”，也不是注释中的 `0x22`。接收全部应使用 `{ can_id=0, can_mask=0 }`；只收标准数据帧 `0x22` 应使用 ID `0x22`，mask 为 `CAN_SFF_MASK | CAN_EFF_FLAG | CAN_RTR_FLAG`。

## 应用修复状态

```text
[LVGL CAN ROOT CAUSE VERIFIED]
[LVGL CAN APP FIX PENDING]
```

当前仓库仅在 `docs/development/strings rk356x-demo_good_board_backup.md` 找到命令字符串，没有对应可编辑 C 源文件，因此本轮没有修改或重新编译 LVGL 应用。

## 经典 CAN 重配成功证据

接口为 `UP` 时直接修改 bit timing：

```text
ip link set can0 type can bitrate 500000
RTNETLINK answers: Device or resource busy
```

正确顺序：

```bash
ip link set can0 down
ip link set can0 type can bitrate 500000
ip link set can0 up
ip -details -statistics link show can0
```

结果：

```text
2: can0: <NOARP,UP,LOWER_UP,ECHO> mtu 16 qdisc pfifo_fast state UP
can state ERROR-ACTIVE (berr-counter tx 0 rx 0) restart-ms 1
bitrate 500000 sample-point 0.875
tq 50 prop-seg 17 phase-seg1 17 phase-seg2 5 sjw 1
rockchip_canfd: tseg1 1..128 tseg2 1..128 sjw 1..128 brp 1..256 brp-inc 2
clock 200000000
re-started 0 bus-errors 0 arbit-lost 0 error-warn 1 error-pass 1 bus-off 0
RX bytes 4449240 packets 556155 errors 0 dropped 0 overrun 0
TX bytes 0 packets 0 errors 0 dropped 1 carrier 0
```

判定：`[CLASSIC CAN RECONFIG VERIFIED]`。累计 error-state 事件和 RX 计数保留为待解释证据；没有 CAN ID/DLC/payload，物理帧收发状态仍为 `[PENDING]`。

板端 `ip` 同时打印了不合理的 `promiscuity` 和 queue 数值，后续使用 `/sys/class/net/can0/statistics/` 与 `candump` 交叉验证，不采信这些异常扩展字段。
