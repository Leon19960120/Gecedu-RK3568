# RK3568 开发板系统移植全记录

> **作者：**HYL  
> **日期：** 2026年5月1日  
> **状态：** 主线 Linux 6.18 内核已成功启动（2026-08-07），下一步：先在 6.18 系统下验证基础外围

---

## 前言

本文档记录了在“rk3568”开发板（粤嵌 RK3568 EVB1 DDR4 V10）上，从出厂 Buildroot 4.19.232 系统向**主线 Linux 6.18 内核**移植的完整过程。该开发板无官方资料支持，本项目旨在通过逆向分析与系统调试，学习 Linux 内核编译与系统构建的过程。（早期曾评估 Ubuntu/Debian 完整发行版路线，已放弃；最终目标 = 主线 Kernel + 保留出厂 Buildroot rootfs 学习系统构建。）

---

## 一、硬件规格与初步评估

---

## 二、调试环境搭建

### 2.1 基础调试手段

- **USB-OTG调试：** 最稳定的调试途径，用于获取底层信息与执行命令，启动日志详见 `logs/` 及 `01_boot_chain.md`（主线 6.18 成功启动的完整日志）。
- 网口调试：SSH进入Bulidroot系统，进行调试。

### 2.4 尝试进入刷机模式

- **Loader 模式：** USB连接OTG，打开RKDevTool.exe 3.18，设备启动电脑自动识别，进入ADB模式，点击切换按钮，屏幕会显示“卡在芯片Logo”的画面，进入Loader模式。
- **Maskrom 模式：** 核心板上有按钮可以进入Maskrom模式。

---

## 三、固件提取与逆向分析

### 3.1 镜像备份

从瑞芯微开发工具读取开发板分区表、

分区备份：

全盘备份：

使用 `dd` 命令完整备份 eMMC 数据：

```bash
cd /storage/CE3297AB329796D5/backup/
dd if=/dev/block/mmcblk2 of=rk3568_android_full.img bs=4M conv=sync,noerror
```

> **说明：** `mmcblk2` 为 eMMC 设备节点，备份文件约 14GB，耗时较长，但能保证数据完整性。

### 3.2 `boot.img` 解包分析

使用 `binwalk` 解包 `boot.img`，提取以下关键组件：

```shell
:/tmp$ binwalk uboot.img

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             Flattened device tree, size: 3584 bytes, version: 17
875096        0xD5A58         CRC32 polynomial table, little endian
942064        0xE5FF0         Android bootimg, kernel size: 1919249152 bytes, kernel addr: 0x5F6C656E, ramdisk size: 1919181921 bytes, ramdisk addr: 0x5700635F, product name: ""
1930480       0x1D74F0        DES SP1, little endian
1930736       0x1D75F0        DES SP2, little endian
1937048       0x1D8E98        SHA256 hash constants, little endian
1965940       0x1DFF74        Unix path: /lib/libtomcrypt/hash.c
1967362       0x1E0502        DES PC1 table
1967418       0x1E053A        DES PC2 table
1968866       0x1E0AE2        Unix path: /lib/libtomcrypt/boringssl/bn/bn.c
2002944       0x1E9000        Flattened device tree, size: 14285 bytes, version: 17
2097152       0x200000        Flattened device tree, size: 3584 bytes, version: 17
2972248       0x2D5A58        CRC32 polynomial table, little endian
3039216       0x2E5FF0        Android bootimg, kernel size: 1919249152 bytes, kernel addr: 0x5F6C656E, ramdisk size: 1919181921 bytes, ramdisk addr: 0x5700635F, product name: ""
4027632       0x3D74F0        DES SP1, little endian
4027888       0x3D75F0        DES SP2, little endian
4034200       0x3D8E98        SHA256 hash constants, little endian
4063092       0x3DFF74        Unix path: /lib/libtomcrypt/hash.c
4064514       0x3E0502        DES PC1 table
4064570       0x3E053A        DES PC2 table
4066018       0x3E0AE2        Unix path: /lib/libtomcrypt/boringssl/bn/bn.c
4100096       0x3E9000        Flattened device tree, size: 14285 bytes, version: 17
```

使用 `binwalk` 解包 `boot.img`，提取以下关键组件：

#### 解包结果目录结构：

```shell
hyl@HYL:~$ docker run --rm -v /tmp:/tmp binwalkv3:latest /tmp/boot.img

                                                                                              /tmp/boot.img
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DECIMAL                            HEXADECIMAL                        DESCRIPTION
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
0                                  0x0                                Device tree blob (DTB), version: 17, CPU ID: 0, total size: 1536 bytes
2048                               0x800                              Device tree blob (DTB), version: 17, CPU ID: 0, total size: 137367 bytes
315968                             0x4D240                            SHA256 hash constants, little endian
14033704                           0xD62328                           Linux version 4.19.232 (gecedu@Gecedu) (gcc version 10.3.1 20210621 (GNU Toolchain for the A-profile Architecture 10.3-2021.07
                                                                      (arm-10.29)), GNU ld (GNU Toolchain for the A-profile Architecture 10.3-2021.07 (arm-10.29)) 2.36.1.20210621) #5 SMP Thu Aug 14
                                                                      19:27:53 CST 2025, has symbol table: false
14057984                           0xD68200                           ELF binary, 64-bit shared object, ARM 64-bit for System-V (Unix), little endian
14064208                           0xD69A50                           SHA256 hash constants, little endian
14064464                           0xD69B50                           AES RCON
14064576                           0xD69BC0                           AES S-Box
14081904                           0xD6DF70                           gzip compressed data, operating system: Unix, timestamp: 1970-01-01 00:00:00, total size: 35000 bytes
14549696                           0xDE02C0                           PKCS DER hash, SHA512
14549715                           0xDE02D3                           PKCS DER hash, SHA384
14549734                           0xDE02E6                           PKCS DER hash, SHA256
14549787                           0xDE031B                           PKCS DER hash, SHA1
14549802                           0xDE032A                           PKCS DER hash, MD5
14564460                           0xDE3C6C                           AES RCON
14592896                           0xDEAB80                           CRC32 polynomial table, little endian
18195283                           0x115A353                          Copyright text: "Copyright 2005-2007 Rodolfo Giometti <giometti@linux.it> "
18260794                           0x116A33A                          Copyright text: "Copyright(c) Pierre Ossman "
19614674                           0x12B4BD2                          JBOOT STAG header, system upgrade image, header size: 16 bytes, kernel data size: 327681 bytes
20447784                           0x1380228                          CPIO ASCII archive, file count: 3
20568000                           0x139D7C0                          AES Reverse Table
20576192                           0x139F7C0                          AES Forward Table
22410240                           0x155F400                          Device tree blob (DTB), version: 17, CPU ID: 0, total size: 137367 bytes
22547968                           0x1580E00                          BMP image, total size: 12936
22561280                           0x1584200                          BMP image, total size: 22364
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Analyzed 1 file for 111 file signatures (251 magic patterns) in 166.0 milliseconds

```

- **内核（Kernel）：** 提取成功，可用于后续编译或替换。
- **设备树（DTB）：** 提取成功，确认设备型号为 `RK3568-EVB1-V10`。

---

## 四、主线内核移植进展（2026-08-07 里程碑）

### 4.1 已达成
- **主线 Linux 6.18.0 内核成功启动并进入出厂 rootfs（Buildroot 2018.02-rc3）shell**，`uname -a` 输出 `Linux RK356X 6.18.0 ... aarch64`。
- 打通路径：内核 + DTB + 外置数据 FIT（Rockchip `mkimage -E -p 0x800`）+ 厂商 U-Boot 启动链（`boot_android; boot_fit; bootrkp; distro_bootcmd`）。
- 完整启动日志见 `01_boot_chain.md`。

### 4.2 当前遗留（均非致命）
| 问题 | 现象 | 原因 |
|---|---|---|
| 触摸 / WiFi 模块 | `goodix.ko` / `8723ds.ko: invalid module format` | rootfs 内为 4.19.232 编译，需为 6.18 重编 |
| MIPI-DSI 屏 | `cannot open framebuffer device` | 屏驱动未做（T2 大任务） |
| dwc3 USB3 | `dwc3: failed to initialize core` | 时钟/供电域/phy 待查（小任务） |
| configfs / USB gadget | `/sys/kernel/config/usb_gadget` 不存在 | 内核未编 configfs（非致命） |
| oem / userdata | `Wrong fs type(ext2)` | fstab 类型不符（非致命） |

### 4.3 下一步：先玩系统（T1，当前进行中）
已能进 6.18 shell 跑命令，学习 Linux 命令 / 系统构建的首要目标已满足。暂不动内核 / 外设驱动，先在 6.18 下验证基础外围（主线自带驱动应可直接用），对照之前逆向 `rk356x-demo` 的脚位。

**批次 1 — 系统信息自检（先跑这组，看懂输出再进下一批）：**
```bash
uname -a
cat /proc/version
nproc
free -h
ls /lib/modules/            # 确认是否有 6.18.0（当前应只有 4.19.232）
cat /sys/firmware/devicetree/base/model
cat /proc/partitions
mount | grep -E 'mmcblk|rootfs'
```
**批次 2 — 网络（RTL8211F，主线 stmmac）：**
```bash
ip link                    # 看 eth0 是否存在
cat /sys/class/net/eth0/operstate
# 若 up 但无 IP：udhcpc -i eth0（rootfs 已用 dhcpcd，一般自动获取）
```
**批次 3 — IIO 传感器（光照 / 六轴 / SARADC，主线 iio 驱动）：**
```bash
ls /sys/bus/iio/devices/
# SARADC:  iio:device0/in_voltage6_raw（ADC 测试键）
# 光照:    iio:device2/in_illuminance_raw（bh1750）
# 六轴:    iio:device1/（mpu6050，raw 加速度 / 角速度）
```
**批次 4 — I2C / GPIO / LED（用户态）：**
```bash
ls /sys/bus/i2c/devices/   # eeprom@i2c2-0x50、gt911@i2c1-0x5d 等
ls /sys/class/gpio/        # LED 脚位 gpio120/121/123/124（sysfs 编号）
cat /sys/class/thermal/thermal_zone0/temp
```

> 注意：`goodix` / `8723ds` 模块因版本错暂不可用，WiFi / 触摸需待 B 任务（为 6.18 重编模块）解决。
