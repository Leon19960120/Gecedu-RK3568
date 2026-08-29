# 12 - WiFi RTL8723DS (SDIO) 驱动编译与加载

> 目标：在 LubanCat SDK（Rockchip BSP 5.10.209）上，把 rtl8723ds 的 SDIO WiFi 驱动编译成 `8723ds.ko` 并在板子上加载出 `wlan0`。

## 当前状态

| 层 | 状态 | 证据 |
|----|------|------|
| `8723ds.ko` 编译 | `[BSP-5.10 RUNTIME VERIFIED]` | 产物 `8723ds.ko`（4.4 MB，aarch64，vermagic `5.10.209 SMP mod_unload aarch64`） |
| SDIO 卡识别 | `[BSP-5.10 RUNTIME VERIFIED]` | dmesg `RTW: == SDIO Card Info ==` + `card: 00000000daf42ca2`，`clock: 50000000 Hz` |
| `wlan0` / `p2p0` 网卡 | `[BSP-5.10 RUNTIME VERIFIED]` | `RTW: module init ret=0`，`ifconfig -a` 出现 `wlan0`（`70:68:71:ec:10:66`）与 `p2p0` |
| WiFi 扫描/联网 | `[MANUAL WRITTEN, PENDING-VERIFY]` | 操作手册见「运行态操作手册」（第 0–7 步）；板上实测待回填 |
| BT（UART8） | `[PENDING]` | 本文只覆盖 WiFi 侧；BT 走 `hci_uart` + `BT_HCIUART_RTL`，另行跟进 |

## 背景

- 板子：GEC / GecEdu RK3568 V11，运行模型 `Rockchip RK3568 GEC DDR4 V10 Board`
- SDK：`lubancat-linux-sdk`，内核 `kernel-5.10`（5.10.209），交叉编译器 `prebuilts/.../aarch64-rockchip1031-linux-gnu-`（gcc 10.3）
- 芯片：Realtek RTL8723DS（WiFi SDIO + BT UART8）
- 关键事实：树内 `drivers/net/wireless/rockchip_wlan/Makefile` 里 `obj-$(CONFIG_RTL8723DS) += rtl8723ds/` 被**注释掉**，所以 rtl8723ds **只能 out-of-tree 单独编译**；SDK 自带的 `./build.sh wifibt` 又因缺少 `external/rkwifibt` 目录而不可用。

## 结论（一句话）

这个 vendor 驱动是为旧内核写的，在 5.10 + Android GKI 内核上有**两类叠加障碍**：

1. **Rockchip BSP 的编译门槛**：`gcc-wrapper.py` 把任何警告当致命错误，加上内核自带的具体 `-Werror=*`，导致无害警告也能打断编译。
2. **真实的 API/符号不兼容**：驱动捆绑的 crypto、`proc` 接口、`cfg80211_ops`、`sched_param`、GKI 的 VFS 符号命名空间等，都与 5.10 不一致。

两类问题都要解决，缺一不可。下面是按遇到顺序的完整排查记录。

## 编译流程

> **⚠️ 重要：rtl8723ds 必须走 out-of-tree 单独编译，不能进 `build.sh kernel`。**
> 两个硬约束：
> 1. `drivers/net/wireless/rockchip_wlan/Makefile` 第 10 行 `obj-$(CONFIG_RTL8723DS) += rtl8723ds/` **必须保持注释**。
> 2. `CONFIG_RTL8723DS=m` **不能写进 `rockchip_linux_defconfig`**。
>
> 否则 `./build.sh kernel` 会 `make rockchip_linux_defconfig` 重生成 `.config`（`CONFIG_WERROR=y` 复活），把 rtl8723ds 当树内模块编译，被 `-Werror=implicit-fallthrough` + `gcc-wrapper.py` 卡死。

```bash
cd ~/lubancat-linux-sdk/kernel-5.10/drivers/net/wireless/rockchip_wlan/rtl8723ds

# 用目录内 standalone 方式：它会自己 export CONFIG_RTL8723DS=m，
# 不依赖内核 .config，因此不必往 defconfig 塞 CONFIG_RTL8723DS=m。
make ARCH=arm64 \
  CROSS_COMPILE=~/lubancat-linux-sdk/prebuilts/gcc/linux-x86/aarch64/gcc-arm-10.3-2021.07-x86_64-aarch64-none-linux-gnu/bin/aarch64-rockchip1031-linux-gnu- \
  CC=~/lubancat-linux-sdk/prebuilts/gcc/linux-x86/aarch64/gcc-arm-10.3-2021.07-x86_64-aarch64-none-linux-gnu/bin/aarch64-rockchip1031-linux-gnu-gcc \
  KSRC=~/lubancat-linux-sdk/kernel-5.10

# 产物
ls -la 8723ds.ko
```

> 注：`CC=` 用于绕过 `gcc-wrapper.py`（见问题 2）。若习惯用 `make -C KDIR M=<dir> modules` 形式，则需先把 `CONFIG_RTL8723DS=m` 临时写进内核 `.config`/`auto.conf`（但**不要**写进 defconfig）。

## 遇到的问题与根因

### 问题 1：`#error CONFIG_RESUME_IN_WORKQUEUE without CONFIG_WAKELOCK/ANDROID_POWER`

```
drv_conf.h:160 #error "enable CONFIG_RESUME_IN_WORKQUEUE without CONFIG_WAKELOCK or CONFIG_ANDROID_POWER..."
```

- **根因**：`rtl8723ds/Makefile` 里有 3 处 `EXTRA_CFLAGS += -DCONFIG_RESUME_IN_WORKQUEUE`，该宏依赖 Android 电源管理（`CONFIG_WAKELOCK`/`CONFIG_ANDROID_POWER`），Buildroot 内核没有。
- **修**：把 3 行 `EXTRA_CFLAGS += -DCONFIG_RESUME_IN_WORKQUEUE` 注释掉。

### 问题 2：`error, forbidden warning:rtw_mlme.c:3281`（gcc-wrapper.py）

- **根因**：Rockchip BSP 的 `Makefile:493-494` 无条件把 `CC` 包成 `scripts/gcc-wrapper.py $(CROSS_COMPILE)gcc`，这个 Python 脚本把 gcc 的**任何**非白名单警告都转成 `error, forbidden warning` 并删掉 `.o`、退出非零。
- **修**：编译命令显式加 `CC=$(CROSS_COMPILE)gcc`，绕过 wrapper（只影响本模块编译，`build.sh kernel` 编内核时不编 rtl8723ds，所以不受影响）。

### 问题 3：`cc1: some warnings being treated as errors`（内核 `-Werror=*`）

- **根因**：即使关掉 `CONFIG_WERROR`，内核 `Makefile` 仍硬加了一组**具体**的 `-Werror=*`（`Makefile:528` 的 `-Werror=strict-prototypes` 等、`1044` 的 `-Werror=date-time`、`1047` 的 `-Werror=incompatible-pointer-types`、`1050` 的 `-Werror=designated-init`）。gcc 对「后面的通用 `-Wno-error`」**无法撤销**前面具体的 `-Werror=foo`，必须用对应的 `-Wno-error=foo`。
- **修**：在 `rtl8723ds/Makefile` 加：
  ```make
  EXTRA_CFLAGS += -Wno-error=strict-prototypes -Wno-error=implicit-function-declaration \
                  -Wno-error=implicit-int -Wno-error=return-type -Wno-error=date-time \
                  -Wno-error=incompatible-pointer-types -Wno-error=designated-init
  ```
  （`EXTRA_CFLAGS` 位于编译命令里 `KBUILD_CFLAGS` 之后，能可靠覆盖。）

### 问题 4：`make` 一个 `.c` 都不编译（0 个 `.o`，空 `obj-m`）

- **根因**：`rtl8723ds/Makefile:2353` 是 `obj-$(CONFIG_RTL8723DS) := $(MODULE_NAME).o`（`:=` **立即求值**），而它自己的 `export CONFIG_RTL8723DS = m` 在 2357 行之后才出现。所以该变量对模块 Makefile 自身是空的，`obj-m` 完全靠内核 `auto.conf` **预注入** `CONFIG_RTL8723DS=m` 才成立。此前一次 `syncconfig` 重生成把 `CONFIG_RTL8723DS=m` 从 `auto.conf` 里丢了（因为它不是 defconfig 默认项）。
- **修**：把 `CONFIG_RTL8723DS=m` 写进 `.config`、`include/config/auto.conf`、`arch/arm64/configs/rockchip_linux_defconfig` 三处，并 `touch include/config/auto.conf` 避免被重新生成覆盖。

### 问题 5：`struct sched_param` 不完整类型

```
rtw_recv.c:4591: error: variable 'param' has initializer but incomplete type
```

- **根因**：新内核把 `struct sched_param`（含 `sched_priority`）完整定义放到了 `<uapi/linux/sched/types.h>`；驱动只通过 `<linux/sched.h>` 拿到了前向声明。
- **修**：`include/drv_types.h` 加 `#include <uapi/linux/sched/types.h>`。

### 问题 6：`macro 'crc32' requires 3 arguments, but only 2 given`

- **根因**：内核 `<linux/crc32.h>` 定义 `crc32(seed, data, length)` 宏，把驱动自己的 2 参函数声明 `u32 crc32(const u8 *frame, size_t frame_len)` 宏展开了。
- **修**：`core/crypto/rtw_crypto_wrap.h` 在声明前 `#undef crc32`。

### 问题 7：`redefinition of 'struct sha256_state'`

- **根因**：驱动捆绑了自己的 sha256（结构体布局与内核不同：`u64 length; u32 state[8], curlen; u8 buf[64]`），与内核 `<crypto/sha.h>` 的 `struct sha256_state` 撞名，函数 `sha256_init/update/...` 也冲突。
- **修**：`core/crypto/sha256_i.h` + `sha256-internal.c` 里的符号统一加前缀改成 `rtw_sha256_state` / `rtw_sha256_init` / `rtw_sha256_process` / `rtw_sha256_done`。

### 问题 8：`'struct cfg80211_ops' has no member named 'mgmt_frame_register'`

- **根因**：`mgmt_frame_register` 回调在 5.8 被移除，换成了 `update_mgmt_frame_registrations`（参数是 subtype 位图，模型不同）。
- **修**：`os_dep/linux/ioctl_cfg80211.c` 里，函数定义和 ops 结构体的 `.mgmt_frame_register` 赋值都用 `#if (LINUX_VERSION_CODE < KERNEL_VERSION(5, 8, 0))` 守护（5.10 不编该回调；`mgmt_tx` 保留）。

### 问题 9：`proc_create_data` 要求 `struct proc_ops *`（而非 `file_operations *`）

- **根因**：5.6+ 把 proc 文件操作从 `struct file_operations` 换成 `struct proc_ops`（成员名 `.open→.proc_open`、`.read→.proc_read`、`.llseek→.proc_lseek`、`.release→.proc_release`、`.write→.proc_write`），且 `proc_ops` 没有 `.owner` 成员。函数指针签名完全一致，只是结构体类型和成员名不同。
- **修**：`os_dep/linux/rtw_proc.c` 加一组宏按内核版本切换：
  ```c
  #if (LINUX_VERSION_CODE >= KERNEL_VERSION(5, 6, 0))
  #define RTW_PROC_FOPS   struct proc_ops
  #define RTW_PROC_OPEN   .proc_open
  ...
  #else
  #define RTW_PROC_FOPS   struct file_operations
  #define RTW_PROC_OPEN   .open
  ...
  #endif
  ```
  再把 8 个 fops 结构体、`rtw_proc_create_entry` 的 `fops` 参数、以及 `.owner = THIS_MODULE` 统一改到宏上。

### 问题 10：modpost 报 VFS 符号命名空间未导入

```
ERROR: modpost: module 8723ds uses symbol kernel_write from namespace
       VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver, but does not import it.
（同样还有 kernel_read、filp_open）
```

- **根因**：这是 **Android GKI 内核**（内核编译参数里带 `-DANDROID_GKI_VFS_EXPORT_ONLY=VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver`），把 `kernel_read`/`kernel_write`/`filp_open` 限制在内部命名空间，驱动直接用会 modpost 失败。驱动在 `os_dep/osdep_service.c`、`core/rtw_wlan_util.c` 里用了这三个函数（读 wpa_supplicant.conf / phy 参数文件）。
- **修**：`os_dep/linux/os_intfs.c` 的模块声明处加：
  ```c
  #if defined(MODULE_IMPORT_NS) && (LINUX_VERSION_CODE >= KERNEL_VERSION(5, 4, 0))
  MODULE_IMPORT_NS(VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver);
  #endif
  ```

## 最终成果

`8723ds.ko` 编译产物：

```text
8723ds.ko: ELF 64-bit LSB relocatable, ARM aarch64, version 1 (SYSV), with debug_info, not stripped
filename:   8723ds.ko
import_ns:  VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver
description: Realtek Wireless Lan Driver
license:    GPL
alias:      sdio:c*v024CdD724*    # Realtek 8723DS
vermagic:   5.10.209 SMP mod_unload aarch64
```

板子上加载（`insmod /system/lib/modules/8723ds.ko`）关键日志：

```text
==== Launching Wi-Fi driver! (Powered by Rockchip) ====
[WLAN_RFKILL]: wifi turn on power [GPIO-1-0]
RTW: rtl8723ds v5.10.1-20-g5af20e016.20200310_beta
RTW: == SDIO Card Info ==
RTW:   card: 00000000daf42ca2
RTW:   clock: 50000000 Hz
RTW:   timing spec: sd high-speed
RTW: rtw_ndev_init(wlan0) if1 mac_addr=70:68:71:ec:10:66
RTW: rtw_ndev_init(p2p0) if2 mac_addr=72:68:71:ec:10:66
RTW: module init ret=0
```

`ifconfig -a` 出现 `wlan0`（`70:68:71:EC:10:66`）和 `p2p0`。

> 非致命提示：`get_wifi_addr_vendor: rk_vendor_read wifi mac address failed (-1)` —— 只是 vendor 分区没读到 MAC，回退用芯片 EFUSE 的 MAC，不影响使用。

## 部署

```bash
# 复制（Windows cmd 下，先 cd 到 ko 所在目录）
cd C:\Users\17937\Desktop
scp 8723ds.ko root@192.168.100.194:/system/lib/modules/8723ds.ko

# 板子上
insmod /system/lib/modules/8723ds.ko
dmesg | tail -30
ifconfig -a
```

## 运行态操作手册：从 wlan0 到能上网

> 前置：已完成上面「编译流程」并 `insmod 8723ds.ko`，`ifconfig -a` 能看到 `wlan0`。
> 内核已开 `CONFIG_CFG80211=y` / `CONFIG_MAC80211=y` / `CONFIG_WIRELESS_EXT=y`（已核实），所以 `iw` 与 `wpa_supplicant` 的用户态路径可用。
> 标 `[PENDING-VERIFY]` 的输出为**尚未在板上实采**、按已知行为预填，待实测后回填。

### 第 0 步：确认板上用户态工具

RTL8723DS 驱动只负责把 `wlan0` 拉起来；**扫描/关联/拿 IP 全部靠用户态工具**。先查板子有没有：

```bash
# 板上执行
which iw wpa_supplicant wpa_cli udhcpc 2>/dev/null
ls -l /usr/sbin/iw /usr/sbin/wpa_supplicant /sbin/udhcpc 2>/dev/null
```

- `iw`：扫描、看链路状态（需要 `nl80211`，即上面的 CFG80211）
- `wpa_supplicant` + `wpa_cli`：WPA/WPA2 个人版关联（RTL8723DS 不支持裸 open 以外的加密，几乎必须）
- `udhcpc`：busybox 自带 DHCP 客户端（LubanCat rootfs 通常已有）

> **SDK 现状**：`lubancat-linux-sdk/buildroot` 里**没有** `wpa_supplicant` / `iw` 包（已核实 `buildroot/package/` 下不存在）。所以板子出厂 rootfs 大概率**缺这两个**。
> 两种补法：
> 1. **交叉编译** `iw` 和 `wpa_supplicant`（依赖 `libnl`，iw 还需要 `libnl-3`/`libnl-genl-3`），拷到板子 `/usr/sbin/`。
> 2. 若 SDK 用的是其它 rootfs（Debian/Ubuntu 基底），直接 `apt-get install iw wpasupplicant` 或 `udhcpc` 对应包。
>
> 下面步骤假设工具已就位；缺哪一步命令报 `command not found` 就回到这里补。

### 第 1 步：确认 rfkill 没把 WiFi 锁死

RTL8723DS 走 Rockchip 的 `[WLAN_RFKILL]`（加载驱动时 `wifi turn on power [GPIO-1-0]` 已证明上电）。仍确认一下软/硬阻塞：

```bash
rfkill list
# 期望：看到 Wireless LAN，soft/hard 都是 no（或 unblocked）
rfkill unblock all   # 若被 blocked，先解
```

若 `rfkill` 命令本身不存在，可跳过——驱动加载日志已显示上电成功，通常无需额外解阻塞。

### 第 2 步：把 wlan0 拉 up（不配 IP）

```bash
ip link set wlan0 up
ip link show wlan0
# 期望：<BROADCAST,MULTICAST,UP,LOWER_UP> ... state UP
dmesg | tail -5
# 期望：RTW: nolinked power save leave 之类，无 error
```

> 若 `ip link set wlan0 up` 后立刻 `RTW: ... disconnect` 或没 `LOWER_UP`，先查天线/SDIO 时钟；但本驱动 SDIO clock 已 50MHz 且 card info 正常，通常不是这里的问题。

### 第 3 步：扫描 AP（iw）

```bash
iw dev wlan0 scan | grep -E "SSID|signal|freq" | head -40
# 期望：列出周围 AP 的 SSID / 信号强度 / 频段
# [PENDING-VERIFY] 例：
#   SSID: MyRouter_2.4G
#   signal: -45 dBm
#   freq: 2437 MHz
```

- 扫不到任何 SSID：先确认路由器是 **2.4GHz**（RTL8723DS 不支持 5GHz）；再 `iw dev wlan0 info` 看 `wiphy` / `channel` 是否正常。
- `iw: command not found`：回到第 0 步补 `iw`。

> 也可用 `iwlist wlan0 scan`（wireless-tools，依赖 WIRELESS_EXT，内核已开）。

### 第 4 步：写 wpa_supplicant 配置并关联

```bash
# 板上创建配置（SSID/密码替换成你的）
cat > /etc/wpa_supplicant.conf <<'EOF'
ctrl_interface=/var/run/wpa_supplicant
update_config=1

network={
    ssid="你的SSID"
    psk="你的密码"
    key_mgmt=WPA-PSK
}
EOF

# 后台启动（-B 守护，-i 接口，-c 配置，-D 驱动后端用 nl80211）
wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant.conf -D nl80211,wext
# 期望：无 fatal，后台静默；看日志：
wpa_cli -i wlan0 status
# [PENDING-VERIFY] 期望出现：
#   wpa_state=COMPLETED
#   ssid=你的SSID
#   pairwise_cipher=CCMP
#   key_mgmt=WPA2-PSK
```

关联失败排查：

| 现象 | 原因 / 处理 |
|------|------------|
| `wpa_state=SCANNING` 卡住 | SSID 隐藏 / 密码错 → 检查 `wpa_cli` 的 `CTRL-EVENT-*` 日志 |
| `nl80211 not found` | 驱动后端换 `-D wext`（内核有 WIRELESS_EXT） |
| 一直 `ASSOCIATING` 失败 | 路由器是 WPA3 或个人版不支持 → 确认是 WPA2-PSK |
| `wpa_supplicant: command not found` | 第 0 步补包 |

### 第 5 步：拿 IP（udhcpc）

```bash
# busybox udhcpc（LubanCat rootfs 通常自带）
udhcpc -i wlan0 -t 10 -n
# 期望：
#   Sending discover...
#   Sending select for 192.168.x.x...
#   Lease of 192.168.x.x obtained, lease time N
ip addr show wlan0
# 期望：inet 192.168.x.x/24
```

> 若 rootfs 是 Debian 基底，用 `dhclient wlan0` 或 `systemctl restart networking` 替代 `udhcpc`。

### 第 6 步：验证连通

```bash
# 网关（从 ip route 看）
ip route show default
# 期望：default via 192.168.x.1 dev wlan0

ping -c 3 192.168.x.1      # 先 ping 网关
ping -c 3 8.8.8.8          # 再 ping 外网（需 DNS，见下）
# 若外网不通但网关通：检查 /etc/resolv.conf 是否有 nameserver
echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

### 第 7 步：开机自启（可选，固化）

把第 4、5 步做成板子启动脚本（或在 `/etc/network/interfaces`、`systemd`/`procd` 里配 `wlan0` + `wpa_supplicant + udhcpc`）。驱动 `8723ds.ko` 建议放到 `/system/lib/modules/` 或 `/lib/modules/$(uname -r)/` 并在启动早期 `insmod`（注意 vermagic 必须匹配 `5.10.209`）。

### 实测回填区

| 步骤 | 实测命令输出 | 日期 |
|------|-------------|------|
| 第 3 步 扫描 | `[PENDING-VERIFY]` | — |
| 第 4 步 关联 `wpa_cli status` | `[PENDING-VERIFY]` | — |
| 第 5 步 拿 IP | `[PENDING-VERIFY]` | — |
| 第 6 步 ping 网关/外网 | `[PENDING-VERIFY]` | — |

> 后续在板上跑通后，把真实输出替换 `[PENDING-VERIFY]` 并填日期，这节就从「手册」变成「已验证证据」。

## 后续（未完成）

- BT：UART8 + `hci_uart` + `BT_HCIUART_RTL` + `SERIAL_DEV_BUS` / `SERIAL_DEV_CTRL_TTYPORT`，DTS 侧沿用 Rockchip BSP 的 `rfkill-bluetooth` 节点（boot log 已证明 `[BT_RFKILL]` 存在且工作，勿改 DTS 绑定）。
