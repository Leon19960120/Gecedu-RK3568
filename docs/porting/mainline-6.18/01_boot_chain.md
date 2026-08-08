# RK3568 主线 Linux 6.18 启动日志（成功）

> **日期：** 2026-08-07
> **内核：** Linux 6.18.0 (hyl@HYL) — Arm GNU Toolchain 15.2.Rel1 (Build arm-15.86)
> **U-Boot：** next-dev-gaeec6f2bfd5-250929（Rockchip 厂商 U-Boot，SPL 2017.09）
> **DTS：** arch/arm64/boot/dts/rockchip/rk3568-evb1-v10.dtb（主线 EVB1 DDR4 V10）
> **boot 镜像：** 外置数据 FIT（`mkimage -f fit-image.its -E -p 0x800 boot.img`，gzip 压缩内核）
> **烧写方式：** RKDevTool 仅烧 `boot` 分区（Loader/parameter 不动）
> **结果：** ✅ 成功启动，自动进入出厂 rootfs 的 shell（Buildroot 2018.02-rc3）

---

## 一、里程碑意义

这是整个「RK3568 移植主线内核」项目最根本的突破：**从出厂 4.19.232 切换到主线 6.18 内核，内核 + DTB + 外置 FIT + 启动链全部打通，且为自动启动（上电即进 6.18，无需手动敲命令）**。

打通前踩的三个关键坑（详见 `../rockchip-6.6/00_overview.md` 与 `../../../porting/mainline-6.18/boot/fit-image.its` 注释）：
1. **FIT 必须是外置数据格式**：Rockchip `boot_fit` 启动前调 `fit_is_ext_type()`，要求 FIT 头 `fdt_totalsize < 4KiB`；普通 `mkimage -f` 内嵌会把头撑到 ~14MiB 直接被拒（`FIT: No fit blob`）。必须用 `mkimage -E -p 0x800`。
2. **内核需 gzip 压缩**：出厂 boot 分区仅 32MiB，39MiB 未压缩 Image 塞不下，gzip 后 ~14MiB。
3. **load 地址用真实 RAM 地址**：`kernel=0x04080000` / `fdt=0x08300000`（占位符 `0xffffff01/0xffffff00` 仅 SPL 阶段有效，手动启动路径不换算）。

---

## 二、完整启动日志

> 以下为串口（UART2, 1500000n8）完整捕获，从 SPL/DDR 训练到 `uname -a` 输出。日志中段出现一次 SoftReset 重训练属正常（首次 USB 下载触发），第二次起即正常走 SPL→BL31→U-Boot→内核。

```
DDR 5b48980fd7 typ 25/12/03-15:33.27,fwver: v1.25
In
wdqs_if: 0x1010100
LP4/4x derate en, other dram:1x trefi
ddrconfig:0
MID:0x13
LPDDR4, 324MHz
BW=32 Col=10 Bk=8 CS0 Row=16 CS=1 Die BW=16 Size=2048MB
tdqss_lf: cs0 dqs0: 24ps, dqs1: -72ps, dqs2: -48ps, dqs3: -144ps,
tdqss_hf: cs0 dqs0: 24ps, dqs1: -72ps, dqs2: -48ps, dqs3: -144ps,

change to: 324MHz
PHY drv:clk:38,ca:38,DQ:30,odt:0
vrefinner:41%, vrefout:41%
dram drv:40,odt:0
clk skew:0x62

change to: 528MHz
PHY drv:clk:38,ca:38,DQ:30,odt:0
vrefinner:41%, vrefout:41%
dram drv:40,odt:0
clk skew:0x58

change to: 780MHz
PHY drv:clk:38,ca:38,DQ:30,odt:60
vrefinner:16%, vrefout:41%
dram drv:40,odt:0
clk skew:0x58
rx vref: 14.4%
tx vref: 38.0%

change to: 1560MHz(final freq)
PHY drv:clk:38,ca:38,DQ:30,odt:60
vrefinner:16%, vrefout:29%
dram drv:40,odt:80
vref_ca:00000068
clk skew:0x1c
rx vref: 14.4%
tx vref: 32.0%
cs 0:
rdtrn RS:
DQS0:0x38, DQS1:0x37, DQS2:0x39, DQS3:0x33,
min  :0x12 0x12 0x14 0x12  0x3  0x5  0xb  0x9 , 0xb  0x8  0x1  0x4  0xd  0xb  0xd  0xb ,
      0x15 0x13  0xf  0xe  0x3  0x0  0x2  0x7 , 0xe  0xb  0x7  0x2  0xe  0xf  0xc 0x12 ,
mid  :0x2d 0x2d 0x2f 0x2d 0x1d 0x21 0x25 0x25 ,0x26 0x24 0x1d 0x1f 0x28 0x26 0x26 0x26 ,
      0x2f 0x2e 0x28 0x28 0x1e 0x1b 0x1d 0x22 ,0x28 0x25 0x22 0x1d 0x2a 0x2a 0x28 0x2d ,
max  :0x48 0x48 0x4b 0x48 0x37 0x3d 0x3f 0x41 ,0x42 0x41 0x39 0x3b 0x43 0x42 0x40 0x42 ,
      0x4a 0x4a 0x42 0x42 0x3a 0x37 0x38 0x3d ,0x42 0x3f 0x3d 0x39 0x46 0x46 0x44 0x48 ,
range:0x36 0x36 0x37 0x36 0x34 0x38 0x34 0x38 ,0x37 0x39 0x38 0x37 0x36 0x37 0x33 0x37 ,
      0x35 0x37 0x33 0x34 0x37 0x37 0x36 0x36 ,0x34 0x34 0x36 0x37 0x38 0x37 0x38 0x36 ,
wrtrn RS:
DQS0:0x20, DQS1:0xe, DQS2:0x13, DQS3:0x0,
min  :0x6d 0x73 0x74 0x6f 0x62 0x65 0x6a 0x68 0x69 ,0x57 0x56 0x50 0x50 0x5c 0x59 0x5c 0x58 0x54 ,
      0x61 0x60 0x5c 0x5b 0x52 0x4f 0x52 0x56 0x59 ,0x4f 0x4b 0x49 0x45 0x50 0x52 0x4c 0x54 0x4b ,
mid  :0x87 0x8c 0x8d 0x89 0x7a 0x7c 0x81 0x80 0x81 ,0x70 0x6f 0x67 0x69 0x74 0x71 0x73 0x70 0x6d ,
      0x7a 0x7a 0x74 0x73 0x6b 0x68 0x6a 0x6e 0x71 ,0x67 0x63 0x61 0x5e 0x6a 0x6a 0x66 0x6c 0x64 ,
max  :0xa2 0xa6 0xa6 0xa4 0x93 0x93 0x99 0x99 0x99 ,0x8a 0x88 0x7e 0x82 0x8d 0x8a 0x8a 0x89 0x87 ,
      0x94 0x95 0x8d 0x8c 0x84 0x81 0x83 0x86 0x8a ,0x80 0x7b 0x79 0x77 0x84 0x83 0x80 0x84 0x7d ,
range:0x35 0x33 0x32 0x35 0x31 0x2e 0x2f 0x31 0x30 ,0x33 0x32 0x2e 0x32 0x31 0x31 0x2e 0x31 0x33 ,
      0x33 0x35 0x31 0x31 0x32 0x32 0x31 0x30 0x31 ,0x31 0x30 0x30 0x32 0x34 0x31 0x34 0x30 0x32 ,
CBT RS:
cs:0 min  :0x47 0x45 0x3b 0x37 0x3e 0x36 0x40 ,0x49 0x41 0x3e 0x36 0x3c 0x35 0x42 ,
cs:0 mid  :0x84 0x84 0x78 0x77 0x7a 0x75 0x6e ,0x85 0x81 0x7a 0x76 0x77 0x75 0x6f ,
cs:0 max  :0xc1 0xc3 0xb5 0xb7 0xb6 0xb4 0x9d ,0xc2 0xc2 0xb6 0xb6 0xb3 0xb5 0x9d ,
cs:0 range:0x7a 0x7e 0x7a 0x80 0x78 0x7e 0x5d ,0x79 0x81 0x78 0x80 0x77 0x80 0x5b ,
out
Boot1 Release Time: Apr 14 2023 10:04:54, version: 1.17
support nand flash type: slc
...nandc_flash_init enter...
No.1 FLASH ID:ff ff ff ff ff ff
sfc nor id: ff ff ff
sfc_nand id: ff ff ff
SD IO init 0
Set SD Clk: 200, 5
Set SD Clk: 200, 5
 SDC_BusRequest:  CMD=8  SDC_RESP_TIMEOUT 1736
 mmc0:cmd8,20
 SDC_BusRequest:  CMD=5  SDC_RESP_TIMEOUT 1736
 mmc0:cmd5,20
 SDC_BusRequest:  CMD=55  SDC_RESP_TIMEOUT 1736
 mmc0:cmd55,20
 SDC_BusRequest:  CMD=1  SDC_RESP_TIMEOUT 1736
 mmc0:cmd1,20
Set SD Clk: 200, 5
 ...(SD 卡检测超时，属正常，板子无 SD 卡)...
SdmmcInit=0 1
Emmc IO init.
EMMC_DLL_RXCLK = 0
Emmc IO init.
EMMC_DLL_RXCLK = 0
mmc_set_bus_width: 1
SetEmmcClk: 375000, 5
mmc_switch index:183, value:0x2
mmc_switch index:185, value:0x2
SetEmmcClk: 375000, 5
mmc_set_bus_width: 8
SetEmmcClk: 200000000, 1
Enable PHY CLK: 200000000
SdmmcInit=2 0
BootCapSize=100000
UserCapSize=15028MB
FwPartOffset=2000 , 100000
UsbBoot ...62080
powerOn 62297
SoftReset, 3442035 us
DDR 5b48980fd7 typ 25/12/03-15:33.27,fwver: v1.25
In
...(第二次 DDR 训练，同上，省略重复)...
out
U-Boot SPL board init
U-Boot SPL 2017.09-g606f72bd97a-240527 #lxh (May 30 2024 - 16:08:15), fwver: v1.14
unknown raw ID 0 0 0
unrecognized JEDEC id bytes: 00, 00, 00
Trying to boot from MMC2
MMC: no card present
mmc_init: -123, time 1
spl: mmc init failed with error: -123
Trying to boot from MMC1
SPL: A/B-slot: _a, successful: 0, tries-remain: 7
Trying fit image at 0x4000 sector
## Verified-boot: 0
## Checking atf-1 0x00040000 (gzip @0x00240000) ... sha256(3bb37dbaff...) + sha256(77f66bc3ae...) + OK
## Checking uboot 0x00a00000 (gzip @0x00c00000) ... sha256(c61e56eb47...) + sha256(ecac778f0e...) + OK
## Checking fdt 0x00b5d920 ... sha256(cb93004999...) + OK
## Checking atf-2 0xfdcc1000 ... sha256(5e891e12e9...) + OK
## Checking atf-3 0x0005c000 ... sha256(fc632865ba...) + OK
## Checking atf-4 0xfdcc1000 ... sha256(821ec3fca7...) + OK
## Checking atf-5 0xfdcd0000 ... sha256(37b2f43b0d...) + OK
## Checking atf-6 0x0005a000 ... sha256(384b87ec34...) + OK
## Checking optee 0x08400000 (gzip @0x08600000) ... sha256(736dc76820...) + sha256(69cf1dc21a...) + OK
Jumping to U-Boot(0x00a00000) via ARM Trusted Firmware(0x00040000)
Total: 171.953/241.125 ms

INFO:    Preloader serial: 2
NOTICE:  BL31: v2.3():v2.3-948-g0a207bf3c:huan.he, fwver: v1.46
NOTICE:  BL31: Built : 16:25:04, Sep 20 2025
INFO:    GICv3 without legacy support detected.
INFO:    ARM GICv3 driver initialized in EL3
INFO:    pmu v1 is valid 220114
INFO:    l3 cache partition cfg-0
INFO:    dfs DDR fsp_param[0].freq_mhz= 1560MHz
INFO:    dfs DDR fsp_param[1].freq_mhz= 324MHz
INFO:    dfs DDR fsp_param[2].freq_mhz= 528MHz
INFO:    dfs DDR fsp_param[3].freq_mhz= 780MHz
INFO:    Using opteed sec cpu_context!
INFO:    boot cpu mask: 0
INFO:    BL31: Initializing runtime services
INFO:    BL31: Initializing BL32
I/TC:
I/TC: OP-TEE version: 3.13.0-1018-g3864e29ae #hisping.lin (gcc version 10.2.1 20201103 ...) #2 Tue Jul  1 02:22:06 UTC 2025 aarch64, fwver: v2.16
I/TC: Primary CPU initializing
I/TC: CRYPTO_CRYPTO_VERSION_NEW no support. Skip all algo mode check.
I/TC: Primary CPU switching to normal world boot
INFO:    BL31: Preparing for EL3 exit to normal world
INFO:    Entry point address = 0xa00000
INFO:    SPSR = 0x3c9


U-Boot next-dev-gaeec6f2bfd5-250929 #linux (Dec 30 2025 - 23:50:52 +0800)

Model: Rockchip RK3568 Evaluation Board
MPIDR: 0x0
PreSerial: 2, raw, 0xfe660000
DRAM:  2 GiB
Sysmem: init
Relocation Offset: 7d102000
Relocation fdt: 7b7f9608 - 7b7fece8, kfdt: 00b63000 - 100362fff
CR: M/C/I
Using default environment

optee api revision: 2.0
dwmmc@fe2b0000: 1, dwmmc@fe2c0000: 2, sdhci@fe310000: 0
Bootdev(atags): mmc 0
MMC0: HS200, 200Mhz
PartType: EFI
TEEC: Waring: Could not find security partition
E/TC:? 0 storage_check_security_level_flag:581 Not support security level!
DM: v1
boot mode: normal
Failed to load DTB, ret=-19
No valid DTB, ret=-22
Failed to get kernel dtb, ret=-22
io-domain: OK
Failed to get scmi clk dev
No OTP device, ret=-19
dmc_fsp failed, ret=-19
Model: Rockchip RK3568 Evaluation Board
rockchip_set_serialno: could not find efuse/otp device
CLK: (sync kernel. arm: enter 816000 KHz, init 816000 KHz, kernel 0N/A)
  ...(时钟树信息)...
Net:   No ethernet found.
Hit key to stop autoboot('CTRL+C'):  0
ANDROID: reboot reason: "(none)"
Not AVB images, AVB skip
No valid android hdr
Android image load failed
Android boot failed, error -1.
## Booting FIT Image at 0x7a7f9fc0 with size 0x00dfe52c
Fdt Ramdisk skip relocation
## Loading kernel from FIT Image at 7a7f9fc0 ...
   Using 'conf' configuration
## Verified-boot: 0
   Trying 'kernel' kernel subimage
     Description:  Linux kernel 6.18 (RK3568)
     Type:         Kernel Image
     Compression:  gzip compressed
     Data Start:   0x7a7fa7c0
     Data Size:    14607600 Bytes = 13.9 MiB
     Architecture: AArch64
     OS:           Linux
     Load Address: 0x04080000
     Entry Point:  0x04080000
     Hash algo:    sha256
     Hash value:   40964e2d4916fe0ea161473b8f78385503fb7d4ae10cb6e94c869c64300e271a
   Verifying Hash Integrity ... sha256+ OK
## Loading fdt from FIT Image at 7a7f9fc0 ...
   Using 'conf' configuration
   Trying 'fdt' fdt subimage
     Description:  RK3568 EVB1 device tree
     Type:         Flat Device Tree
     Compression:  uncompressed
     Data Start:   0x7b5e8cb0
     Data Size:    63038 Bytes = 61.6 KiB
     Architecture: AArch64
     Load Address: 0x08300000
     Hash algo:    sha256
     Hash value:   ca1d2d69d984e1a5759fa02aa3b6dcda6dff84fbd3ce9c774e3d6a8253de84ec
   Verifying Hash Integrity ... sha256+ OK
   Using fdt from load-in fdt
   Loading fdt from 0x7b5e8cb0 to 0x08300000
   Booting using the fdt blob at 0x08300000
   Uncompressing GZIP Kernel Image from 0x7a7fa7c0 to 0x04080000 ... with 0270ba00 bytes OK
   kernel loaded at 0x04080000, end = 0x0678ba00
   Using Device Tree in place at 0000000008300000, end 000000000831263d
can't found rockchip,drm-logo, use rockchip,fb-logo
WARNING: could not set reg FDT_ERR_BADOFFSET.
failed to reserve fb-loader-logo memory
## reserved-memory:
  shmem@10f000: addr=10f000 size=100
Adding bank: 0x00200000 - 0x08400000 (size: 0x08200000)
Adding bank: 0x09400000 - 0x80000000 (size: 0x76c00000)
== DO RELOCATE == Kernel from 0x04080000 to 0x04000000
Total: 1128.896/1174.274 ms

Starting kernel ...

I/TC: Secondary CPU 1 initializing
I/TC: Secondary CPU 1 switching to normal world boot
I/TC: Secondary CPU 2 initializing
I/TC: Secondary CPU 2 switching to normal world boot
I/TC: Secondary CPU 3 initializing
I/TC: Secondary CPU 3 switching to normal world boot
[    0.000000] Booting Linux on physical CPU 0x0000000000 [0x412fd050]
[    0.000000] Linux version 6.18.0 (hyl@HYL) (aarch64-none-linux-gnu-gcc (Arm GNU Toolchain 15.2.Rel1 (Build arm-15.86)) 15.2.1 20251203, GNU ld (Arm GNU Toolchain 15.2.Rel1 (Build arm-15.86)) 2.45.1.20251203) #1 SMP PREEMPT Thu Aug  6 20:23:48 CST 2026
[    0.000000] KASLR disabled due to lack of seed
[    0.000000] random: crng init done
[    0.000000] Machine model: Rockchip RK3568 EVB1 DDR4 V10 Board
[    0.000000] efi: UEFI not found.
[    0.000000] OF: reserved mem: 0x000000000010f000..0x000000000010f0ff (0 KiB) nomap non-reusable shmem@10f000
[    0.000000] NUMA: Faking a node at [mem 0x0000000000200000-0x000000007fffffff]
[    0.000000] NODE_DATA(0) allocated [mem 0x7fbae840-0x7fbb0ebf]
[    0.000000] Zone ranges:
[    0.000000]   DMA      [mem 0x0000000000200000-0x000000007fffffff]
[    0.000000]   DMA32    empty
[    0.000000]   Normal   empty
[    0.000000] Movable zone start for each node
[    0.000000] Early memory node ranges
[    0.000000]   node   0: [mem 0x0000000000200000-0x00000000083fffff]
[    0.000000]   node   0: [mem 0x0000000009400000-0x000000007fffffff]
[    0.000000] Initmem setup node 0 [mem 0x0000000000200000-0x000000007fffffff]
[    0.000000] On node 0, zone DMA: 512 pages in unavailable ranges
[    0.000000] On node 0, zone DMA: 4096 pages in unavailable ranges
[    0.000000] cma: Reserved 32 MiB at 0x000000007ba00000
[    0.000000] psci: probing for conduit method from DT.
[    0.000000] psci: PSCIv1.1 detected in firmware.
[    0.000000] psci: Using standard PSCI v0.2 function IDs
[    0.000000] psci: Trusted OS migration not required
[    0.000000] psci: SMC Calling Convention v1.2
[    0.000000] percpu: Embedded 25 pages/cpu s62488 r8192 d31720 u102400
[    0.000000] Detected VIPT I-cache on CPU0
[    0.000000] CPU features: detected: GICv3 CPU interface
[    0.000000] CPU features: detected: Virtualization Host Extensions
[    0.000000] CPU features: detected: ARM errata 1165522, 1319367, or 1530923
[    0.000000] alternatives: applying boot alternatives
[    0.000000] Kernel command line: console=ttyS2,1500000 root=PARTUUID=614e0000-0000 rootwait
[    0.000000] printk: log buffer data + meta data: 131072 + 458752 = 589824 bytes
[    0.000000] Dentry cache hash table entries: 262144 (order: 9, 2097152 bytes, linear)
[    0.000000] Inode-cache hash table entries: 131072 (order: 8, 1048576 bytes, linear)
[    0.000000] software IO TLB: SWIOTLB bounce buffer size adjusted to 1MB
[    0.000000] software IO TLB: area num 4.
[    0.000000] software IO TLB: mapped [mem 0x000000007b600000-0x000000007b800000] (2MB)
[    0.000000] Fallback order for Node 0: 0
[    0.000000] Built 1 zonelists, mobility grouping on.  Total pages: 519680
[    0.000000] Policy zone: DMA
[    0.000000] mem auto-init: stack:all(zero), heap alloc:off, heap free:off
[    0.000000] SLUB: HWalign=64, Order=0-3, MinObjects=0, CPUs=4, Nodes=1
[    0.000000] rcu: Preemptible hierarchical RCU implementation.
[    0.000000] rcu:     RCU event tracing is enabled.
[    0.000000] rcu:     RCU restricting CPUs from NR_CPUS=512 to nr_cpu_ids=4.
[    0.000000]  Trampoline variant of Tasks RCU enabled.
[    0.000000]  Tracing variant of Tasks RCU enabled.
[    0.000000] rcu: RCU calculated value of scheduler-enlistment delay is 25 jiffies.
[    0.000000] rcu: Adjusting geometry for rcu_fanout_leaf=16, nr_cpu_ids=4
[    0.000000] RCU Tasks: Setting shift to 2 and lim to 1 rcu_task_cb_adjust=1 rcu_task_cpu_ids=4.
[    0.000000] RCU Tasks Trace: Setting shift to 2 and lim to 1 rcu_task_cb_adjust=1 rcu_task_cpu_ids=4.
[    0.000000] NR_IRQS: 64, nr_irqs: 64, preallocated irqs: 0
[    0.000000] GIC: enabling workaround for GICv3: non-coherent attribute
[    0.000000] GICv3: GIC: Using split EOI/Deactivate mode
[    0.000000] GICv3: 320 SPIs implemented
[    0.000000] GICv3: 0 Extended SPIs implemented
[    0.000000] GICv3: MBI range [296:319]
[    0.000000] GICv3: Using MBI frame 0x00000000fd410000
[    0.000000] Root IRQ handler: gic_handle_irq
[    0.000000] GICv3: GICv3 features: 16 PPIs
[    0.000000] GICv3: GICD_CTLR.DS=0, SCR_EL3.FIQ=1
[    0.000000] GICv3: CPU0: found redistributor 0 region 0:0x00000000fd460000
[    0.000000] ITS [mem 0xfd440000-0xfd45ffff]
[    0.000000] GIC: enabling workaround for ITS: Rockchip erratum RK3568002
[    0.000000] GIC: enabling workaround for ITS: non-coherent attribute
[    0.000000] ITS@0x00000000fd440000: allocated 8192 Devices @450000 (indirect, esz 8, psz 64K, shr 0)
[    0.000000] ITS@0x00000000fd440000: allocated 32768 Interrupt Collections @460000 (flat, esz 2, psz 64K, shr 0)
[    0.000000] ITS: using cache flushing for cmd queue
[    0.000000] GICv3: using LPI property table @0x0000000000470000
[    0.000000] GIC: using cache flushing for LPI property table
[    0.000000] GICv3: CPU0: using allocated LPI pending table @0x0000000000480000
[    0.000000] rcu: srcu_init: Setting srcu_struct sizes based on contention.
[    0.000000] arch_timer: cp15 timer running at 24.00MHz (phys).
[    0.000000] clocksource: arch_sys_counter: mask: 0xffffffffffffff max_cycles: 0xffffffffffff, max_idle_ns: 440795202592 ns
[    0.000001] sched_clock: 56 bits at 24MHz, resolution 41ns, wraps every 4398046511097ns
[    0.003341] Console: colour dummy device 80x25
[    0.003469] Calibrating delay loop (skipped), value calculated using timer frequency.. 48.00 BogoMIPS (lpj=96000)
[    0.003488] pid_max: default: 32768 minimum: 301
[    0.003624] LSM: initializing lsm=capability
[    0.003797] Mount-cache hash table entries: 4096 (order: 3, 32768 bytes, linear)
[    0.003820] Mountpoint-cache hash table entries: 4096 (order: 3, 32768 bytes, linear)
[    0.007118] rcu: Hierarchical SRCU implementation.
[    0.007132] rcu:     Max phase no-delay instances is 1000.
[    0.007507] Timer migration: 1 hierarchy levels; 8 children per group; 1 crossnode level
[    0.007799] fsl-mc MSI: msi-controller@fd440000 domain created
[    0.012819] EFI services will not be available.
[    0.013239] smp: Bringing up secondary CPUs ...
[    0.014779] Detected VIPT I-cache on CPU1
[    0.014934] GICv3: CPU1: found redistributor 100 region 0:0x00000000fd480000
[    0.014958] GICv3: CPU1: using allocated LPI pending table @0x0000000000490000
[    0.015017] CPU1: Booted secondary processor 0x0000000100 [0x412fd050]
[    0.016748] Detected VIPT I-cache on CPU2
[    0.016888] GICv3: CPU2: found redistributor 200 region 0:0x00000000fd4a0000
[    0.016909] GICv3: CPU2: using allocated LPI pending table @0x00000000004a0000
[    0.016956] CPU2: Booted secondary processor 0x0000000200 [0x412fd050]
[    0.018611] Detected VIPT I-cache no CPU3
[    0.018751] GICv3: CPU3: found redistributor 300 region 0:0x00000000fd4c0000
[    0.018772] GICv3: CPU3: using allocated LPI pending table @0x00000000004b0000
[    0.018818] CPU3: Booted secondary processor 0x0000000300 [0x412fd050]
[    0.019034] smp: Brought up 1 node, 4 CPUs
[    0.019046] SMP: Total of 4 processors activated.
[    0.019051] CPU: All CPU(s) started at EL2
[    0.019057] CPU features: detected: 32-bit EL0 Support
[    0.019061] CPU features: detected: 32-bit EL1 Support
[    0.019068] CPU features: detected: Data cache clean to the PoU not required for I/D coherence
[    0.019073] CPU features: detected: Common not Private translations
[    0.019077] CPU features: detected: CRC32 instructions
[    0.019090] CPU features: detected: RCpc load-acquire (LDAPR)
[    0.019095] CPU features: detected: LSE atomic instructions
[    0.019099] CPU features: detected: Privileged Access Never
[    0.019104] CPU features: detected: PMUv3
[    0.019108] CPU features: detected: RAS Extension Support
[    0.019120] CPU features: detected: Speculative Store Bypassing Safe (SSBS)
[    0.019193] alternatives: applying system-wide alternatives
[    0.024021] Memory: 1956792K/2078720K available (18176K kernel code, 5422K rwdata, 12944K rodata, 3264K init, 690K bss, 83648K reserved, 32768K cma-reserved)
[    0.024755] devtmpfs: initialized
[    0.042752] clocksource: jiffies: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 7645041785100000 ns
[    0.042796] posixtimers hash table entries: 2048 (order: 3, 32768 bytes, linear)
[    0.042876] futex hash table entries: 1024 (65536 bytes on 1 NUMA nodes, total 64 KiB, linear).
[    0.043593] 22576 pages in range for non-PLT usage
[    0.043606] 514096 pages in range for PLT usage
[    0.044009] pinctrl core: initialized pinctrl subsystem
[    0.048768] DMI not present or invalid.
[    0.052587] NET: Registered PF_NETLINK/PF_ROUTE protocol family
[    0.054501] DMA: preallocated 256 KiB GFP_KERNEL pool for atomic allocations
[    0.055805] DMA: preallocated 256 KiB GFP_KERNEL|GFP_DMA pool for atomic allocations
[    0.057264] DMA: preallocated 256 KiB GFP_KERNEL|GFP_DMA32 pool for atomic allocations
[    0.057336] audit: initializing netlink subsys (disabled)
[    0.057672] audit: type=2000 audit(0.052:1): state=initialized audit_enabled=0 res=1
[    0.061773] thermal_sys: Registered thermal governor 'step_wise'
[    0.061781] thermal_sys: Registered thermal governor 'power_allocator'
[    0.061912] cpuidle: using governor menu
[    0.062292] hw-breakpoint: found 6 breakpoint and 4 watchpoint registers.
[    0.062469] ASID allocator initialised with 65536 entries
[    0.067822] Serial: AMBA PL011 UART driver
[    0.096353] /vop@fe040000: Fixed dependency cycle(s) with /dsi@fe060000
[    0.096470] /dsi@fe060000: Fixed dependency cycle(s) with /dsi@fe060000/panel@0
[    0.096491] /dsi@fe060000: Fixed dependency cycle(s) with /vop@fe040000
[    0.096682] /dsi@fe060000/panel@0: Fixed dependency cycle(s) with /dsi@fe060000
[    0.097601] /vop@fe040000: Fixed dependency cycle(s) with /hdmi@fe0a0000
[    0.097722] /hdmi@fe0a0000: Fixed dependency cycle(s) with /vop@fe040000
[    0.130449] gpio gpiochip0: Static allocation of GPIO base is deprecated, use dynamic allocation.
[    0.131274] rockchip-gpio fdd60000.gpio: probed /pinctrl/gpio@fdd60000
[    0.132013] gpio gpiochip1: Static allocation of GPIO base is deprecated, use dynamic allocation.
[    0.132345] rockchip-gpio fe740000.gpio: probed /pinctrl/gpio@fe740000
[    0.133105] gpio gpiochip2: Static allocation of GPIO base is deprecated, use dynamic allocation.
[    0.133408] rockchip-gpio fe750000.gpio: probed /pinctrl/gpio@fe750000
[    0.134170] gpio gpiochip3: Static allocation of GPIO base is deprecated, use dynamic allocation.
[    0.134465] rockchip-gpio fe760000.gpio: probed /pinctrl/gpio@fe760000
[    0.135123] gpio gpiochip4: Static allocation of GPIO base is deprecated, use dynamic allocation.
[    0.135411] rockchip-gpio fe770000.gpio: probed /pinctrl/gpio@fe770000
[    0.143793] /hdmi@fe0a0000: Fixed dependency cycle(s) with /hdmi-con
[    0.143934] /hdmi-con: Fixed dependency cycle(s) with /hdmi@fe0a0000
[    0.153285] HugeTLB: registered 1.00 GiB page size, pre-allocated 0 pages
[    0.153300] HugeTLB: 0 KiB vmemmap can be freed for a 1.00 GiB page
[    0.153308] HugeTLB: registered 32.0 MiB page size, pre-allocated 0 pages
[    0.153312] HugeTLB: 0 KiB vmemmap can be freed for a 32.0 MiB page
[    0.153318] HugeTLB: registered 2.00 MiB page size, pre-allocated 0 pages
[    0.153323] HugeTLB: 0 KiB vmemmap can be freed for a 32.0 MiB page
[    0.153329] HugeTLB: registered 64.0 KiB page size, pre-allocated 0 pages
[    0.153332] HugeTLB: 0 KiB vmemmap can be freed for a 64.0 KiB page
[    0.156944] ACPI: Interpreter disabled.
[    0.165163] iommu: Default domain type: Translated
[    0.165178] iommu: DMA domain TLB invalidation policy: strict mode
[    0.165815] SCSI subsystem initialized
[    0.166433] usbcore: registered new interface driver usbfs
[    0.166494] usbcore: registered new interface driver hub
[    0.166543] usbcore: registered new device driver usb
[    0.169112] pps_core: LinuxPPS API ver. 1 registered
[    0.169120] pps_core: Software ver. 5.3.6 - Copyright 2005-2007 Rodolfo Giometti <giometti@linux.it>
[    0.169143] PTP clock support registered
[    0.169420] EDAC MC: Ver: 3.0.0
[    0.170394] scmi_core: SCMI protocol bus registered
[    0.172957] FPGA manager framework
[    0.174729] vgaarb: loaded
[    0.175457] clocksource: Switched to clocksource arch_sys_counter
[    0.175855] VFS: Disk quotas dquot_6.6.0
[    0.175887] VFS: Dquot-cache hash table entries: 512 (order 0, 4096 bytes)
[    0.176646] pnp: PnP ACPI: disabled
[    0.189749] NET: Registered PF_INET protocol family
[    0.189976] IP idents hash table entries: 32768 (order: 6, 262144 bytes, linear)
[    0.192187] tcp_listen_portaddr_hash hash table entries: 1024 (order: 2, 16384 bytes, linear)
[    0.192231] Table-perturb hash table entries: 65536 (order: 6, 262144 bytes, linear)
[    0.192252] TCP established hash table entries: 16384 (order: 5, 131072 bytes, linear)
[    0.192472] TCP bind hash table entries: 16384 (order: 7, 524288 bytes, linear)
[    0.192972] TCP: Hash tables configured (established 16384 bind 16384)
[    0.193144] UDP hash table entries: 1024 (order: 4, 65536 bytes, linear)
[    0.193235] UDP-Lite hash table entries: 1024 (order: 4, 65536 bytes, linear)
[    0.193504] NET: Registered PF_UNIX/PF_LOCAL protocol family
[    0.194192] RPC: Registered named UNIX socket transport module.
[    0.194201] RPC: Registered udp transport module.
[    0.194205] RPC: Registered tcp transport module.
[    0.194209] RPC: Registered tcp-with-tls transport module.
[    0.194212] RPC: Registered tcp NFSv4.1 backchannel transport module.
[    0.194231] PCI: CLS 0 bytes, default 64
[    0.200432] kvm [1]: nv: 568 coarse grained trap handlers
[    0.201112] kvm [1]: IPA Size Limit: 40 bits
[    0.201152] kvm [1]: GICv3: no GICV resource entry
[    0.201160] kvm [1]: disabling GICv2 emulation
[    0.201196] kvm [1]: GIC system register CPU interface enabled
[    0.201239] kvm [1]: vgic interrupt IRQ9
[    0.201289] kvm [1]: VHE mode initialized successfully
[    0.203668] Initialise system trusted keyrings
[    0.203977] workingset: timestamp_bits=42 max_order=19 bucket_order=0
[    0.204493] squashfs: version 4.0 (2009/01/31) Phillip Lougher
[    0.204947] NFS: Registering the id_resolver key type
[    0.204971] Key type id_resolver registered
[    0.204977] Key type id_legacy registered
[    0.205009] nfs4filelayout_init: NFSv4 File Layout Driver Registering...
[    0.205018] nfs4flexfilelayout_init: NFSv4 Flexfile Layout Driver Registering...
[    0.205333] 9p: Installing v9fs 9p2000 file system support
[    0.279684] Key type asymmetric registered
[    0.279694] Asymmetric key parser 'x509' registered
[    0.279779] Block layer SCSI generic (bsg) driver version 0.4 loaded (major 244)
[    0.279794] io scheduler mq-deadline registered
[    0.279801] io scheduler kyber registered
[    0.279859] io scheduler bfq registered
[    0.318896] ledtrig-cpu: registered to indicate activity on CPUs
[    0.383195] dma-pl330 fe530000.dma-controller: Loaded driver for PL330 DMAC-241330
[    0.383215] dma-pl330 fe530000.dma-controller:       DBUFF-128x8bytes Num_Chans-8 Num_Peri-32 Num_Events-16
[    0.386279] dma-pl330 fe550000.dma-controller: Loaded driver for PL330 DMAC-241330
[    0.386294] dma-pl330 fe550000.dma-controller:       DBUFF-128x8bytes Num_Chans-8 Num_Peri-32 Num_Events-16
[    0.419058] Serial: 8250/16550 driver, 4 ports, IRQ sharing enabled
[    0.424293] printk: legacy console [ttyS2] disabled
[    0.424841] fe660000.serial: ttyS2 at MMIO 0xfe660000 (irq = 25, base_baud = 1500000) is a 16550A
[    0.424950] printk: legacy console [ttyS2] enabled
[    0.551558] msm_serial: driver initialized
[    0.552990] SuperH (H)SCI(F) driver initialized
[    0.553990] STM32 USART driver initialized
[    0.564241] platform fdea0000.video-codec: Adding to iommu group 0
[    0.566521] platform fdee0000.video-codec: Adding to iommu group 1
[    0.568802] platform fe040000.vop: Adding to iommu group 2
[    0.579149] loop: module loaded
[    0.582387] megasas: 07.734.00.00-rc1
[    0.599863] tun: Universal TUN/TAP device driver, 1.6
[    0.603165] thunder_xcv, ver 1.0
[    0.603595] thunder_bgx, ver 1.0
[    0.603980] nicpf, ver 1.0
[    0.608150] e1000: Intel(R) PRO/1000 Network Driver
[    0.608599] e1000: Copyright (c) 1999-2006 Intel Corporation.
[    0.609181] e1000e: Intel(R) PRO/1000 Network Driver
[    0.609626] e1000e: Copyright(c) 1999 - 2015 Intel Corporation.
[    0.610215] igb: Intel(R) Gigabit Ethernet Network Driver
[    0.610697] igb: Copyright (c) 2007-2014 Intel Corporation.
[    0.611266] igbvf: Intel(R) Gigabit Virtual Function Network Driver
[    0.611854] igbvf: Copyright (c) 2009 - 2012 Intel Corporation.
[    0.613409] sky2: driver version 1.30
[    0.617860] VFIO - User Level meta-driver version: 0.3
[    0.629178] usbcore: registered new interface driver usb-storage
[    0.639222] i2c_dev: i2c /dev entries driver
[    0.669251] sdhci: Secure Digital Host Controller Interface driver
[    0.669818] sdhci: Copyright(c) Pierre Ossman
[    0.672699] Synopsys Designware Multimedia Card Interface Driver
[    0.676533] sdhci-pltfm: SDHCI platform and OF driver helper
[    0.686834] arm-scmi arm-scmi.0.auto: Using scmi_smc_transport
[    0.687379] arm-scmi arm-scmi.0.auto: SCMI max-rx-timeout: 30ms / max-msg-size: 104bytes / max-msg: 20
[    0.688466] scmi_protocol scmi_dev.1: Enabled polling mode TX channel - prot_id:16
[    0.689483] arm-scmi arm-scmi.0.auto: SCMI Notifications - Core Enabled.
[    0.690148] arm-scmi arm-scmi.0.auto: SCMI Protocol v2.0 'rockchip:' Firmware version 0x0
[    0.690988] arm-scmi arm-scmi.0.auto: Enabling SCMI Quirk [quirk_clock_rates_triplet_out_of_spec]
[    0.693476] SMCCC: SOC_ID: ARCH_SOC_ID not implemented, skipping ....
[    0.698535] usbcore: registered new interface driver usbhid
[    0.699043] usbhid: USB HID core driver
[    0.709937] hw perfevents: enabled with armv8_cortex_a55 PMU driver, 7 (0,8000003f) counters available
[    0.711512] mmc1: SDHCI controller on fe310000.mmc [fe310000.mmc] using ADMA
[    0.726378] NET: Registered PF_PACKET protocol family
[    0.726968] 9pnet: Installing 9P2000 support
[    0.727503] Key type dns_resolver registered
[    0.746897] registered taskstats version 1
[    0.747546] Loading compiled-in X.509 certificates
[    0.761853] Demotion targets for Node 0: null
[    0.779171] mmc1: new HS200 MMC card at address 0001
[    0.780667] mmcblk1: mmc1:0001 DA2016 14.7 GiB
[    0.786134]  mmcblk1: p1 p2 p3 p4 p5 p6 p7 p8 p9
[    0.789090] mmcblk1boot0: mmc1:0001 DA2016 4.00 MiB
[    0.792371] mmcblk1boot1: mmc1:0001 DA2016 4.00 MiB
[    0.795745] mmcblk1rpmb: mmc1:0001 DA2016 4.00 MiB, chardev (511:0)
[    0.834453] ehci-platform fd800000.usb: EHCI Host Controller
[    0.835034] ehci-platform fd800000.usb: new USB bus registered, assigned bus number 1
[    0.835951] ehci-platform fd800000.usb: irq 37, io mem 0xfd800000
[    0.837631] ehci-platform fd880000.usb: EHCI Host Controller
[    0.838185] ehci-platform fd880000.usb: new USB bus registered, assigned bus number 2
[    0.839049] ehci-platform fd880000.usb: irq 38, io mem 0xfd880000
[    0.839154] ohci-platform fd840000.usb: Generic Platform OHCI controller
[    0.840317] ohci-platform fd840000.usb: new USB bus registered, assigned bus number 3
[    0.841261] ohci-platform fd840000.usb: irq 39, io mem 0xfd840000
[    0.841720] ohci-platform fd8c0000.usb: Generic Platform OHCI controller
[    0.842369] fan53555-regulator 0-001c: FAN53555 Option[12] Rev[15] Detected!
[    0.842429] ohci-platform fd8c0000.usb: new USB bus registered, assigned bus number 4
[    0.843875] ohci-platform fd8c0000.usb: irq 65, io mem 0xfd8c0000
[    0.847516] ehci-platform fd800000.usb: USB 2.0 started, EHCI 1.00
[    0.849134] hub 1-0:1.0: USB hub found
[    0.849528] hub 1-0:1.0: 1 port detected
[    0.859491] ehci-platform fd880000.usb: USB 2.0 started, EHCI 1.00
[    0.861000] hub 2-0:1.0: USB hub found
[    0.861419] hub 2-0:1.0: 1 port detected
[    0.900514] hub 3-0:1.0: USB hub found
[    0.900952] hub 3-0:1.0: 1 port detected
[    0.904401] hub 4-0:1.0: USB hub found
[    0.904797] hub 4-0:1.0: 1 port detected
[    0.905658] vdda0v9_image: Bringing 600000uV into 900000-900000uV
[    0.917275] vccio_acodec: Bringing 600000uV into 3300000-3300000uV
[    0.935867] vcca1v8_image: Bringing 600000uV into 1800000-1800000uV
[    0.957085] dwmmc_rockchip fe2b0000.mmc: IDMAC supports 32-bit address mode.
[    0.957754] dwmmc_rockchip fe2b0000.mmc: Using internal DMA controller.
[    0.958342] dwmmc_rockchip fe2b0000.mmc: Version ID is 270a
[    0.958884] dwmmc_rockchip fe2b0000.mmc: DW MMC controller at irq 66,32 bit host data width,256 deep fifo
[    0.960160] dwmmc_rockchip fe2b0000.mmc: Got CD GPIO
[    0.975690] mmc_host mmc0: Bus speed (slot 0) = 375000Hz (slot req 400000Hz, actual 375000HZ div = 0)
[    0.977903] clk: Disabling unused clocks
[    0.980746] PM: genpd: Disabling unused power domains
[    0.981739] dw-apb-uart fe660000.serial: forbid DMA for kernel console
[    0.982406] check access for rdinit=/init failed: -2, ignoring
[    1.006927] EXT4-fs (mmcblk1p6): mounted filesystem 49997890-742a-4d5f-96ec-bf13897cae5c ro with ordered data mode. Quota mode: none.
[    1.008170] VFS: Mounted root (ext4 filesystem) readonly on device 179:6.
[    1.014940] devtmpfs: mounted
[    1.016523] Freeing unused kernel memory: 3264K
[    1.017005] Run /sbin/init as init process
[    1.107484] usb 1-1: new high-speed USB device number 2 using ehci-platform
[    1.113515] EXT4-fs (mmcblk1p6): re-mounted 49997890-742a-4d5f-96ec-bf13897cae5c r/w.
[    1.252826] hub 1-1:1.0: USB hub found
[    1.253302] hub 1-1:1.0: 4 ports detected
[    1.342247] /dev/block/by-name/oem: Can't lookup blockdev
[    1.342892] /dev/block/by-name/userdata: Can't lookup blockdev
NAME=Buildroot
VERSION=2018.02-rc3-gce1bf8b5-dirty
ID=buildroot
VERSION_ID=2018.02-rc3
PRETTY_NAME="Buildroot 2018.02-rc3"
Starting logging: OK
/usr/bin/modetest
Populating /dev using udev: [    1.391078] udevd[112]: starting version 3.2.7
[    1.398827] udevd[112]: specified group 'kvm' unknown
[    1.412752] udevd[113]: starting eudev-3.2.7
done
Initializing random number generator... done.
mount: /sys/fs/pstore: pstore already mounted or mount point busy.
Will now mount all partitions in /etc/fstab
Note: Create /.skip_fsck to skip fsck
 - The check might take a while if didn't shutdown properly!
Handling rootfs: /dev/mmcblk1p6 / ext2 rw,noauto 1
Checking /dev/mmcblk1p6(ext2)
[    1.997019] EXT4-fs (mmcblk1p6): re-mounted 49997890-742a-4d5f-96ec-bf13897cae5c ro.
e2fsck 1.43.9 (8-Feb-2018)
rootfs: clean, 8861/393216 files, 198979/1572864 blocks
[    2.060111] EXT4-fs (mmcblk1p6): re-mounted 49997890-742a-4d5f-96ec-bf13897cae5c r/w.
Handling misc: /dev/mmcblk1p2 /misc emmc defaults 0
Unsupported file system emmc for /dev/mmcblk1p2
Handling oem: /dev/mmcblk1p7 /oem ext2 defaults 2
Wrong fs type(ext2) for /dev/mmcblk1p7
Handling userdata: /dev/mmcblk1p9 /userdata ext2 defaults 2
Wrong fs type(ext2) for /dev/mmcblk1p9
Log saved to /tmp/mountall.log
Starting system message bus: done
[    2.501200] module goodix: .gnu.linkonce.this_module section size must match the kernel's built struct module size at run time
[    2.502393] module goodix: .gnu.linkonce.this_module section size must match the kernel's built struct module size at run time
insmod: can't insert '/system/lib/modules/goodix.ko': invalid module format
/etc/init.d/S36load_wifi_modules: line 43: can't create /sys/class/rfkill/rfkill1/state: nonexistent directory
[    2.553039] module 8723ds: .gnu.linkonce.this_module section size must match the kernel's built struct module size at run time
[    2.566621] module 8723ds: .gnu.linkonce.this_module section size must match the kernel's built struct module size at run time
insmod: can't insert '/system/lib/modules/8723ds.ko': invalid module format
Starting network: OK
Starting dhcpcd...
dev: loaded udev
no valid interfaces found
no interfaces have a carrier
forked to background, child pid 469
Starting ntpd: OK
Starting dropbear sshd: OK
Starting launcher: Error: cannot open framebuffer device: No such file or directory
unable open evdev interface:: No such file or directory
LV_HOR_RES_MAX=1024, LV_VER_RES_MAX=600
Debug: configfs_init
mkdir: cannot create directory '/sys/kernel/config/usb_gadget/rockchip': No such file or directory
/etc/init.d/S50usbdevice: line 437: can't create /sys/kernel/config/usb_gadget/rockchip/idVendor: nonexistent directory
...(S50usbdevice 一批 configfs 失败，原因同)...
mount: /dev/usb-ffs/adb: unknown filesystem type 'functionfs'.
/etc/init.d/S50usbdevice: line 437: can't create /sys/kernel/config/usb_gadget/rockchip/UDC: nonexistent directory
Starting linuxptp daemon: OK
Starting linuxptp system clock synchronization: OK
Starting dnsmasq: OK
Trying to reconnect Wifi
Starting input-event-daemon: input-event-daemon: Start parsing /etc/input-event-daemon.conf...
input-event-daemon: open(/dev/input/event*): No such file or directory
input-event-daemon: no listener found!
input-event-daemon: Exiting...
done
[root@RK356X:/]#
[root@RK356X:/]# [   10.992158] platform fcc00000.usb: deferred probe pending: dwc3: failed to initialize core
[   10.992902] platform fd000000.usb: deferred probe pending: dwc3: failed to initialize core
[   10.993645] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fd000000.usb
[   10.994559] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fcc00000.usb
[   10.995504] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fde60000.gpu
[   10.996419] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fdea0000.video-codec
[   10.997393] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fdeb0000.rga
[   10.998306] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fdee0000.video-codec
[   10.999279] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fe040000.vop
[   11.000226] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fe060000.dsi
[   11.001146] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fe0a0000.hdmi
[   11.002069] rockchip-pm-domain fdd90000.power-management:power-controller: sync_state() pending due to fe850000.mipi-dphy
[root@RK356X:/]# uname -a
Linux RK356X 6.18.0 #1 SMP PREEMPT Thu Aug  6 20:23:48 CST 2026 aarch64 GNU/Linux
```

---

## 三、关键节点解读

| 阶段 | 日志证据 | 含义 |
|---|---|---|
| FIT 被接受 | `## Booting FIT Image at 0x7a7f9fc0 ... Uncompressing GZIP Kernel Image ... with 0270ba00 bytes OK` | 外置 FIT 过了 `fit_is_ext_type()`，gzip 解压成功 |
| 内核真正启动 | `[ 0.000000] Linux version 6.18.0 (hyl@HYL) ... #1 SMP PREEMPT` | 主线 6.18 在跑 |
| 4 核全部上线 | `smp: Brought up 1 node, 4 CPUs` / `CPUx: Booted secondary processor` | A55 四核全部启动，EL2 |
| 命令行正确 | `Kernel command line: console=ttyS2,1500000 root=PARTUUID=614e0000-0000 rootwait` | U-Boot default env 自带（ttyS2 而非 ttyFIQ0），root 挂载参数自动满足 |
| 根文件系统挂载 | `[ 1.008170] VFS: Mounted root (ext4) on device 179:6` → `Run /sbin/init` | 之前担心的 VFS/rootargs 问题没出现 |
| 进 shell | `[root@RK356X:/]#` + `uname -a → Linux RK356X 6.18.0 ... aarch64` | 完整用户态可用 |

**注意**：本次是**自动启动**成功的——U-Boot `bootcmd` 链（`boot_android; boot_fit; ...`）自动走到 `boot_fit` 就把新内核拉起来了，无需手动敲命令。断电上电即进 6.18。

---

## 四、启动后报错（全部非致命，且预期内）

| 问题 | 日志 | 原因 | 影响 |
|---|---|---|---|
| 触摸/WiFi 模块版本错 | `goodix.ko` / `8723ds.ko: invalid module format` | rootfs 里是给 4.19.232 编的，6.18 的 module struct 变了 | 触摸(gt911) + WiFi(RTL8723DS) 暂不可用 |
| 屏/帧缓冲没起 | `cannot open framebuffer device`；VOP/DSI/HDMI/GPU `deferred probe pending` | MIPI-DSI 屏驱动（大任务）未做 | 屏幕不亮，launcher 起不来 |
| USB3(dwc3)失败 | `fcc00000.usb` / `fd000000.usb: dwc3: failed to initialize core` | 时钟/供电域/phy 配置不全 | OTG/USB3 暂不能用（USB2/EHCI 正常） |
| configfs 没挂 | `/sys/kernel/config/usb_gadget/rockchip 不存在` | 内核未编 configfs/usb gadget | adb/USB gadget 不可用 |
| oem/userdata 挂载失败 | `Wrong fs type(ext2)` | fstab 当 ext2，实际不是 | 非致命 |
| kvm 组未知 | `udevd: specified group 'kvm' unknown` | rootfs 无 kvm 组 | 非致命 |

以上没有一个阻止进系统，均为「出厂 4.19 rootfs 跑 6.18 内核」的必然摩擦。

---

## 五、下一步方向（待用户决定，AI 不擅自改文件）

- **A. 先玩转当前系统（最贴合学习目标）**：在 6.18 shell 里看 `/proc`、`/sys`、`dmesg`，验证主线内置的 userspace 外围（I2C、GPIO、SARADC、传感器）——这些驱动主线自带，应可直接用，正好对照之前逆向的 `rk356x-demo` 脚位。
- **B. 编译 6.18 内核模块，恢复触摸 + WiFi**：goodix 主线已有；8723ds 需取 rtw88 / lwfinger 源码树，编译后装进 rootfs 的 `/lib/modules/6.18.0/`。
- **C. MIPI-DSI 屏驱动（大任务）**：让屏幕亮起来，工作量最大。
- **D. dwc3 USB3 小修**：让 OTG/USB3 工作。

---

## 六、复现本结果的关键命令（WSL 内核树）

```bash
cd ~/linux-rk3568
# 1. 打包外置数据 FIT（内核 gzip，DTS 用主线 EVB1）
mkimage -f ../../porting/mainline-6.18/boot/fit-image.its -E -p 0x800 boot.img
# 2. 自检：头必须 <0x1000 且 <=0x800（否则改 -p 0x1000）
python3 - <<'PY'
import struct
with open("boot.img","rb") as f:
    magic, totalsize = struct.unpack(">II", f.read(8))
assert magic == 0xd00dfeed and totalsize < 0x1000 and totalsize <= 0x800
PY
# 3. 安全截断到 32MiB（先 stat 确认 <32MiB 才 truncate，避免砍尾）
size=$(stat -c%s boot.img); limit=$((32*1024*1024))
[ "$size" -le "$limit" ] && truncate -s 32M boot.img || echo "超 32MiB, 检查 gzip"
# 4. 拷回 Windows，RKDevTool 仅烧 boot 分区
```

`fit-image.its` 模板位置：`../../porting/mainline-6.18/boot/fit-image.its`（kernel load/entry=0x04080000，fdt load=0x08300000，gzip + 双 sha256）。

---

## 七、附录 A：出厂 boot.img 解包证据（binwalk）

为确认「外置数据型 FIT + 内核 4.19.232 + 设备树型号」这一基线，对出厂 `boot.img` 做 `binwalk` 提取：

```text
DECIMAL   HEXADECIMAL   DESCRIPTION
0         0x0           Device tree blob (DTB), version: 17, total size: 1536 bytes
2048      0x800         Device tree blob (DTB), version: 17, total size: 137367 bytes
315968    0x4D240       SHA256 hash constants
14033704  0xD62328      Linux version 4.19.232 (gecedu@Gecedu) ... #5 SMP Thu Aug 14 19:27:53 CST 2025
14057984  0xD68200      ELF binary, 64-bit shared object, ARM 64-bit
14081904  0xD6DF70      gzip compressed data, total size: 35000 bytes
14549696  0xDE02C0      PKCS DER hash, SHA512 / SHA384 / SHA256 / SHA1 / MD5
22410240  0x155F400     Device tree blob (DTB), version: 17, total size: 137367 bytes
22547968  0x1580E00     BMP image, total size: 12936
22561280  0x1584200     BMP image, total size: 22364
```

关键结论：

- **DTB 在偏移 `0x800`（2048 字节）**：这正是外置数据 FIT 的判据——头部 DTB 极小（1536 字节），
  真正的内核/设备树数据在后面。**我们的 `mkimage -E -p 0x800` 即对齐这一结构**（数据外置、从 0x800 起）。
- **内核版本 4.19.232**（厂内构建），提取成功 → 可用于对照或替换研究。
- **设备树型号确认为 RK3568-EVB1-V10**（反编译后 compatible / model 字段，见 `03_device_tree.md` §1）。
- 两段 `gzip compressed data`（35000 字节）是启动 logo / 资源，主线内核用不到，FIT 里省略。

> 完整解包记录另见原文件 `docs/development/解包boot.md`（保留为原始素材，未删除）。
