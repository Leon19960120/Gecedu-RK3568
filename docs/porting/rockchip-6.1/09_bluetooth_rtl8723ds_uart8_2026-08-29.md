# 09 - RTL8723DS Bluetooth / UART8 验证（2026-08-29）

> 状态：`[BSP-6.1 HCI + FIRMWARE RUNTIME VERIFIED]`
>
> 已验证 Rockchip RFKill 上电、UART8 H5 同步、RTL8723DS 芯片识别、固件下载、串口切换到 1.5 Mbit/s，以及 UART HCI 设备 `hci0` 注册。现有输出中 `hci0` 仍为 `DOWN`，尚无扫描、配对或业务数据传输证据，因此本页不写成“蓝牙功能完全跑通”。

## 结论

GEC V11 的 RTL8723DS 是 Wi-Fi / Bluetooth 二合一芯片，但两部分使用不同链路：

```text
Wi-Fi:      RK3568 SDMMC1/SDIO -> rtw88 -> wlan0
Bluetooth:  RK3568 UART8/H5    -> rtk_hciattach -> hci0
```

Wi-Fi 固件握手成功不能代替 Bluetooth 验证。本次 Bluetooth 实验的关键成功证据：

```text
Realtek Bluetooth :IC: RTL8723DS
Realtek Bluetooth :Load FW /lib/firmware/rtlbt/rtl8723d_fw OK, size 54980
Realtek Bluetooth :FW version 0xaaa82df5, Patch num 3
Realtek Bluetooth :Final speed 1500000
Realtek Bluetooth :Device setup complete
```

随后系统出现：

```text
/sys/class/bluetooth/hci0
hci0: Type: Primary  Bus: UART
BD Address: 70:68:71:EC:10:67
RX errors: 0
TX errors: 0
```

因此可以标记 `[HCI + FIRMWARE RUNTIME VERIFIED]`。由于 `hciconfig -a` 明确显示 `DOWN`，还不能标记扫描、配对或完整蓝牙功能通过。

## 当前架构

当前没有在 UART8 下添加 `realtek,*-bt` serdev 子节点，而是沿用 Rockchip BSP 的传统组合：

```text
wireless_bluetooth / bluetooth-platdata
        -> rfkill_rk 控制 reset、wake 和 host-wake
        -> 用户空间打开 /dev/ttyS8
        -> rtk_hciattach 执行 H5 握手和 Realtek 固件下载
        -> 内核 HCI UART line discipline 注册 hci0
```

这条路线已经取得板端成功证据，不应在没有明确收益和回归测试的情况下切换成另一套 serdev DTS 架构。

## DTS

### UART8

当前 `rk3568-evb1-gec-v11.dtsi`：

```dts
&uart8 {
    status = "okay";
    pinctrl-names = "default";
    pinctrl-0 = <&uart8m0_xfer &uart8m0_ctsn>;
};
```

板端节点：

```text
/dev/ttyS8
dw-apb-uart fe6c0000.serial
```

### Bluetooth 电源与唤醒

```dts
&wireless_bluetooth {
    compatible = "bluetooth-platdata";
    clocks = <&rk809 1>;
    clock-names = "ext_clock";
    uart_rts_gpios = <&gpio2 RK_PB1 GPIO_ACTIVE_LOW>;
    pinctrl-names = "default", "rts_gpio";
    pinctrl-0 = <&uart8m0_rtsn>;
    pinctrl-1 = <&uart8_gpios>;
    BT,reset_gpio    = <&gpio2 RK_PB7 GPIO_ACTIVE_HIGH>;
    BT,wake_gpio     = <&gpio2 RK_PC2 GPIO_ACTIVE_HIGH>;
    BT,wake_host_irq = <&gpio2 RK_PC0 GPIO_ACTIVE_HIGH>;
    status = "okay";
};
```

启动日志解析出的 GPIO 编号与 DTS 一致：

```text
uart_rts_gpios = 73
BT,reset_gpio = 79
BT,wake_gpio = 82
BT,wake_host_irq = 80
```

## 内核配置

当前 GEC 专用 defconfig 保留：

```text
CONFIG_BT=y
CONFIG_BT_RFCOMM=y
CONFIG_BT_HIDP=y
CONFIG_BT_HCIUART=y
CONFIG_BT_HCIUART_RTL=y
CONFIG_RFKILL=y
CONFIG_RFKILL_RK=y
```

最终 `.config` 展开出的关键依赖：

```text
CONFIG_BT_HCIUART=y
CONFIG_BT_HCIUART_SERDEV=y
CONFIG_BT_HCIUART_H4=y
CONFIG_BT_HCIUART_3WIRE=y
CONFIG_BT_HCIUART_RTL=y
CONFIG_RFKILL=y
CONFIG_RFKILL_RK=y
```

当前实际运行依赖 H5/Three-wire、HCI UART、RFKill RK 和 RTL8723DS 用户空间 attach。`CONFIG_BT_HCIUART_ATH3K`、`CONFIG_BT_HCIBTUSB`、`CONFIG_BT_HCIBFUSB`、`CONFIG_BT_HCIVHCI`、`CONFIG_BT_MRVL*` 属于其它硬件路线，可在 Bluetooth 基线验证完成后分轮评估裁剪，不能和本轮成功配置一起大批删除。

## Rootfs 工具与固件

板端已确认存在：

```text
/usr/bin/hciattach
/usr/bin/rtk_hciattach
/usr/bin/hciconfig
/usr/bin/hcitool
```

SDK 源码搜索不到这些工具，不代表目标 rootfs 中也不存在。判断板端能力时应优先检查实际 rootfs：

```bash
which hciattach rtk_hciattach hciconfig hcitool bluetoothd bluetoothctl
```

固件目录：

```text
/lib/firmware/rtlbt/rtl8723d_fw       54980 bytes
/lib/firmware/rtlbt/rtl8723d_config     33 bytes
/lib/firmware/rtlbt/mp_rtl8723d_fw    55736 bytes
/lib/firmware/rtlbt/mp_rtl8723d_config   25 bytes
```

正常启动使用 `rtl8723d_fw` 和 `rtl8723d_config`；`mp_*` 是量产测试资源，不用于本次正常 HCI 初始化。

## 初始状态

内核 Bluetooth core 与 HCI UART 协议已经注册：

```text
Bluetooth: Core ver 2.22
Bluetooth: HCI UART driver ver 2.3
Bluetooth: HCI UART protocol H4 registered
Bluetooth: HCI UART protocol Three-wire (H5) registered
Bluetooth: RFCOMM socket layer initialized
Bluetooth: HIDP socket layer initialized
```

但是 attach 前：

```text
/sys/class/bluetooth/ 为空
rfkill0 name=bt_default type=bluetooth state=0
```

这说明协议栈存在，但 Bluetooth 芯片尚未上电并挂入 HCI 层。仅凭上述启动日志不能宣布蓝牙可用。

## 完整手工验证流程

### 1. 查找 Bluetooth RFKill

不要永久假定 Bluetooth 一定是 `rfkill0`。先按 `type` 查找：

```bash
BT_RFKILL=""
for node in /sys/class/rfkill/rfkill*; do
    if [ "$(cat "$node/type" 2>/dev/null)" = "bluetooth" ]; then
        BT_RFKILL="$node"
        break
    fi
done

[ -n "$BT_RFKILL" ] || {
    echo "Bluetooth RFKill node not found"
    exit 1
}

echo "$BT_RFKILL"
cat "$BT_RFKILL/name"
cat "$BT_RFKILL/state"
```

### 2. 上电

```bash
echo 1 > "$BT_RFKILL/state"
cat "$BT_RFKILL/state"
```

本轮实测 `state` 从 0 变为 1，并出现：

```text
[BT_RFKILL]: ENABLE UART_RTS
[BT_RFKILL]: DISABLE UART_RTS
[BT_RFKILL]: bt turn on power
[BT_RFKILL]: Request irq for bt wakeup host
```

### 3. UART8 H5 attach 与固件下载

```bash
killall rtk_hciattach 2>/dev/null || true

rtk_hciattach -n -s 115200 /dev/ttyS8 rtk_h5 \
    >/tmp/rtk_hciattach.log 2>&1 &
RTK_PID=$!

sleep 5
cat /tmp/rtk_hciattach.log
ps | grep '[r]tk_hciattach'
```

这里的 `115200` 是初始握手速度。实测配置文件随后让芯片和主机切换到 1.5 Mbit/s，不应直接把启动参数改成 1500000 来代替正常初始化流程。

### 4. 检查 HCI 注册

```bash
ls -l /sys/class/bluetooth/
hciconfig -a
```

本轮实测：

```text
hci0:   Type: Primary  Bus: UART
BD Address: 70:68:71:EC:10:67
DOWN
RX bytes:989 events:30 errors:0
TX bytes:798 commands:30 errors:0
```

`DOWN` 表示 HCI netdev 尚未由用户空间置为工作状态，不会推翻前面的芯片识别和固件下载证据；但也意味着射频扫描还未验证。

### 5. 启用并扫描

```bash
hciconfig hci0 up
hciconfig -a
hcitool dev
hcitool scan
```

预期 `hciconfig -a` 出现 `UP RUNNING`，`hcitool dev` 列出本地控制器，`hcitool scan` 返回至少一个处于可发现状态的外部设备。当前尚未提供这些命令的板端输出，所以它们仍属于下一步验证，不写成已完成。

### 6. 配对与业务验证

Classic Bluetooth 的稳定配对、信任、连接和 profile 测试通常需要 BlueZ 的 `bluetoothd` 与 `bluetoothctl`。当前板端工具列表只确认到 `hcitool/hciconfig`，没有 `bluetoothd/bluetoothctl` 的成功路径证据。

补齐 BlueZ 后至少验证：

```text
controller power on
scan on
pair <peer address>
trust <peer address>
connect <peer address>
```

具体 profile 还需按产品需求测试，例如 HID、RFCOMM/SPP 或音频；“能扫描到设备”不等于所有 profile 都可用。

## 本轮成功证据解释

| 输出 | 证明内容 |
|------|----------|
| `Get SYNC Resp Pkt` | H5 UART 基础通信成立 |
| `IC: RTL8723DS` | 芯片识别成立 |
| `rtl8723d_fw OK, size 54980` | 正常固件文件成功读取 |
| `FW version 0xaaa82df5` | 固件版本解析成功 |
| `Final speed 1500000` | UART 双方完成高速切换 |
| `Received cc of hci reset cmd` | 固件下载后 HCI 命令响应正常 |
| `Device setup complete` | `rtk_hciattach` 初始化完成 |
| `/sys/class/bluetooth/hci0` | 内核 HCI 设备已注册 |
| BD Address 与零 RX/TX error | 基础 HCI 命令交换正常 |

## Warning 与非问题

### UART8 DMA fallback

```text
of_dma_request_slave_channel: dma-names property of node '/serial@fe6c0000' missing or empty
dw-apb-uart fe6c0000.serial: failed to request DMA, use interrupt mode
```

UART8 缺少 DMA 属性后回退到中断模式。本轮 H5、固件下载、1.5 Mbit/s 切速和 HCI 命令均成功，因此它不是当前 attach 失败。若后续进行高吞吐蓝牙音频或长时间压力测试，应观察 CPU 占用、UART overrun 和丢包；添加 DMA 前必须核对 6.1 SoC DMA request 和已有参考 DTS，不能直接采用未经验证的通道号。

### 可选配置文件缺失

```text
Couldnt open extra config /opt/rtk_btconfig.txt
Couldnt access customer BT MAC file /opt/bdaddr
```

后续仍成功加载标准 config、获得 BD Address 并完成 setup，因此这两个可选文件在本轮不是阻塞项。产品化时再决定是否需要固定客户地址或额外配置。

### `Realtek: not found`

```text
-/bin/sh: Realtek: not found
```

这是后台 `rtk_hciattach` 输出与串口终端提示符混在一起后，被再次粘贴成 shell 命令造成的，不是驱动或固件报错。将输出重定向到日志文件即可避免。

## 当前证据边界

| 层级 | 状态 |
|------|------|
| Bluetooth core / HCI UART / H5 | `[VERIFIED]` |
| Rockchip RFKill 上电 | `[VERIFIED]` |
| UART8 H5 同步 | `[VERIFIED]` |
| RTL8723DS 识别与固件下载 | `[VERIFIED]` |
| UART 切换 1.5 Mbit/s | `[VERIFIED]` |
| `hci0` 与 BD Address 注册 | `[VERIFIED]` |
| `hci0 UP RUNNING` | `[PENDING]` |
| Classic Bluetooth inquiry 扫描 | `[PENDING]` |
| 配对、连接与业务 profile | `[PENDING]` |
| 冷启动自动 attach | `[PENDING]` |

当前项目状态应写为：

```text
[BLUETOOTH HCI + FIRMWARE RUNTIME VERIFIED]
[BLUETOOTH RF / PAIRING PENDING]
```

## 自动启动待办

手工流程通过后，可把 RFKill 上电、`rtk_hciattach` 和 `hciconfig hci0 up` 固化到启动脚本。脚本必须：

1. 按 RFKill `type=bluetooth` 动态查找节点，不固定 `rfkill0`。
2. 防止重复启动多个 `rtk_hciattach`。
3. 等待 `/sys/class/bluetooth/hci0` 出现后再执行 `hciconfig hci0 up`。
4. 将 attach 输出写入持久日志，失败时保留退出状态。
5. 做一次冷启动复验，确认 Wi-Fi、Bluetooth UART8 和系统其它 UART 不受影响。

自动化完成前，当前成功结论只覆盖手工启动路径。

## 下一步验收清单

```bash
hciconfig hci0 up
hciconfig -a
hcitool dev
hcitool scan
```

扫描通过后再补 BlueZ 配对和目标 profile 测试。只有 `UP RUNNING`、发现外部设备、配对连接和目标业务都取得输出，才能按产品目标升级为 `[BLUETOOTH FUNCTION VERIFIED]`。
