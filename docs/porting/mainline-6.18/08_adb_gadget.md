上电连接OTG就是ADC模式。

```bash
Stopping input-event-daemon:
input-event-daemon: Exiting...
done
stop auto-reboot finished
Stopping dnsmasq: OK
Stopping linuxptp system clock synchronization: OK
Stopping linuxptp daemon: OK
[  384.799516] android_work: sent uevent USB_STATE=DISCONNECTED
sh: 639: unknown operand
stop finishedStopping dropbear sshd: OK
Stopping ntpd: OK
Stopping dhcpcd...
stopped /sbin/dhcpcd (pid 524)
killall: rkaiq_3A_server: no process killed
Stopping network: OK
[  384.951923] [BT_RFKILL]: bt shut off power
Stopping system message bus: done
Saving random seed... done.
/usr/bin/modetest
Stopping logging: OK
[  385.150990] ffs_data_put(): freeing
[  385.280594] EXT4-fs (mmcblk0p6): re-mounted. Opts: (null)
The system is going down NOW!
Sent SIGTERM to all processes
[  385.289001] udevd[140]: could not touch /run/udev/queue: Read-only file syst                                                                                     em
[  385.290710] udevd[661]: '/usr/bin/usbdevice /devices/virtual/android_usb/and                                                                                     roid0 DISCONNECTED' [664] terminated by signal 15 (Terminated)
[  385.291645] udevd[140]: could not unlink /run/udev/queue: Read-only file sys                                                                                     tem
[  385.490168] cpu cpu0: min=816000, max=816000
[  385.506637] rk808 0-0020: reboot: not restore POWER_EN
[  385.507158] rk808 0-0020: reboot: force RK817_RST_FUNC_REG ok!
[  385.528554] dw-mipi-dsi fe060000.dsi: [drm:dw_mipi_dsi_encoder_enable] final                                                                                      DSI-Link bandwidth: 336 x 4 Mbps
[  385.704264] rockchip-vop2 fe040000.vop: [drm:vop2_crtc_atomic_disable] Crtc                                                                                      atomic disable vp0
[  385.737984] mpp_rkvdec2 fdf80200.rkvdec: shutdown device
[  385.738475] mpp_rkvenc fdf40000.rkvenc: shutdown device
[  385.738940] mpp_rkvenc fdf40000.rkvenc: shutdown success
[  385.743850] rkisp_hw fdff0000.rkisp: rkisp_hw_shutdown
[  385.752544] fan53555-regulator 0-001c: fan53555..... reset
[  385.753983] fan53555-regulator 0-001c: reset: force fan53555_reset ok!
[  385.755016] mpp_jpgdec fded0000.jpegd: shutdown device
[  385.755490] mpp-iep2 fdef0000.iep: shutdown device
[  385.755926] mpp_vepu2 fdee0000.vepu: shutdown device
[  385.756383] mpp_vdpu2 fdea0400.vdpu: shutdown device
[  385.758178] reboot: Restarting system with command 'loader'
DDR 5b48980fd7 typ 25/12/03-15:33.27,fwver: v1.25
In
wdqs_if: 0x1010100
LP4/4x derate en, other dram:1x trefi
SRX
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
tx vref: 33.0%
cs 0:
rdtrn RS:
DQS0:0x34, DQS1:0x33, DQS2:0x38, DQS3:0x30,
min  : 0xf 0x10 0x12  0xf  0x1  0x3  0x9  0x6 , 0xb  0x8  0x1  0x3  0xc  0xb  0                                                                                     xd  0xb ,
      0x15 0x13  0xf  0xe  0x3  0x2  0x3  0x8 , 0xe  0xb  0x7  0x1  0xe  0xf  0                                                                                     xb 0x12 ,
mid  :0x2a 0x2a 0x2d 0x2a 0x1b 0x1e 0x23 0x22 ,0x26 0x24 0x1c 0x1e 0x26 0x25 0x                                                                                     25 0x25 ,
      0x2f 0x2e 0x28 0x28 0x1f 0x1d 0x1d 0x23 ,0x27 0x24 0x21 0x1c 0x29 0x2a 0x                                                                                     27 0x2c ,
max  :0x45 0x45 0x49 0x45 0x35 0x3a 0x3d 0x3e ,0x42 0x40 0x37 0x3a 0x40 0x40 0x                                                                                     3e 0x40 ,
      0x4a 0x4a 0x42 0x43 0x3b 0x38 0x38 0x3e ,0x41 0x3e 0x3b 0x37 0x45 0x45 0x                                                                                     43 0x47 ,
range:0x36 0x35 0x37 0x36 0x34 0x37 0x34 0x38 ,0x37 0x38 0x36 0x37 0x34 0x35 0x                                                                                     31 0x35 ,
      0x35 0x37 0x33 0x35 0x38 0x36 0x35 0x36 ,0x33 0x33 0x34 0x36 0x37 0x36 0x                                                                                     38 0x35 ,
wrtrn RS:
DQS0:0x20, DQS1:0xe, DQS2:0x13, DQS3:0x0,
min  :0x6d 0x73 0x74 0x70 0x64 0x68 0x6c 0x69 0x6b ,0x59 0x56 0x50 0x52 0x5d 0x                   5a 0x5c 0x58 0x56 ,
      0x63 0x63 0x5e 0x5c 0x55 0x53 0x55 0x58 0x5b ,0x50 0x4c 0x4b 0x48 0x52 0x                                                                                     53 0x4e 0x55 0x4c ,
mid  :0x87 0x8c 0x8d 0x89 0x7b 0x7e 0x82 0x80 0x82 ,0x71 0x6f 0x68 0x6a 0x75 0x                                                                                     72 0x73 0x71 0x6e ,
      0x7c 0x7c 0x76 0x74 0x6c 0x6a 0x6c 0x6f 0x72 ,0x68 0x63 0x62 0x5f 0x6a 0x                                                                                     6a 0x66 0x6c 0x64 ,
max  :0xa2 0xa5 0xa6 0xa3 0x92 0x94 0x99 0x97 0x99 ,0x8a 0x88 0x81 0x82 0x8d 0x                                                                                     8a 0x8a 0x8a 0x87 ,
      0x95 0x95 0x8e 0x8d 0x84 0x82 0x84 0x87 0x8a ,0x81 0x7a 0x79 0x76 0x83 0x                                                                                     82 0x7f 0x84 0x7d ,
range:0x35 0x32 0x32 0x33 0x2e 0x2c 0x2d 0x2e 0x2e ,0x31 0x32 0x31 0x30 0x30 0x                                                                                     30 0x2e 0x32 0x31 ,
      0x32 0x32 0x30 0x31 0x2f 0x2f 0x2f 0x2f 0x2f ,0x31 0x2e 0x2e 0x2e 0x31 0x                                                                                     2f 0x31 0x2f 0x31 ,
CBT RS:
cs:0 min  :0x46 0x44 0x3b 0x37 0x3e 0x35 0x41 ,0x49 0x42 0x3e 0x38 0x3b 0x35 0x                                                                                     43 ,
cs:0 mid  :0x83 0x83 0x78 0x76 0x7a 0x74 0x6e ,0x85 0x82 0x7a 0x76 0x77 0x75 0x                                                                                     70 ,
cs:0 max  :0xc1 0xc2 0xb5 0xb5 0xb7 0xb3 0x9c ,0xc2 0xc3 0xb7 0xb5 0xb4 0xb5 0x                                                                                     9d ,
cs:0 range:0x7b 0x7e 0x7a 0x7e 0x79 0x7e 0x5b ,0x79 0x81 0x79 0x7d 0x79 0x80 0x                                                                                     5a ,
out
U-Boot SPL board init
U-Boot SPL 2017.09-g606f72bd97a-240527 #lxh (May 30 2024 - 16:08:15), fwver: v1.14                                                                                     
unknown raw ID 0 0 0
unrecognized JEDEC id bytes: 00, 00, 00
Trying to boot from MMC2
MMC: no card present
mmc_init: -123, time 0
spl: mmc init failed with error: -123
Trying to boot from MMC1
SPL: A/B-slot: _a, successful: 0, tries-remain: 7
Trying fit image at 0x4000 sector
## Verified-boot: 0
## Checking atf-1 0x00040000 ... sha256(fc070f5a40...) + OK
## Checking uboot 0x00a00000 ... sha256(e914f0763a...) + OK
## Checking fdt 0x00b39230 ... sha256(fcfda359c0...) + OK
## Checking atf-2 0xfdcc1000 ... sha256(b7e96f5509...) + OK
## Checking atf-3 0x0006c000 ... sha256(fd59386129...) + OK
## Checking atf-4 0xfdcd0000 ... sha256(415b5d518f...) + OK
## Checking atf-5 0xfdcce000 ... sha256(4d791bf003...) + OK
## Checking atf-6 0x0006a000 ... sha256(6e9d32ba23...) + OK
## Checking optee 0x08400000 ... sha256(af414b9c9f...) + OK
Jumping to U-Boot(0x00a00000) via ARM Trusted Firmware(0x00040000)
Total: 126.303/195.374 ms

INFO:    Preloader serial: 2
NOTICE:  BL31: v2.3():v2.3-578-gaef7950e4:huan.he
NOTICE:  BL31: Built : 14:05:25, Apr 19 2023
INFO:    GICv3 without legacy support detected.
INFO:    ARM GICv3 driver initialized in EL3
INFO:    pmu v1 is valid 220114
INFO:    dfs DDR fsp_param[0].freq_mhz= 1560MHz
INFO:    dfs DDR fsp_param[1].freq_mhz= 324MHz
INFO:    dfs DDR fsp_param[2].freq_mhz= 528MHz
INFO:    dfs DDR fsp_param[3].freq_mhz= 780MHz
INFO:    BL31: Initialising Exception Handling Framework
INFO:    BL31: Initializing runtime services
INFO:    BL31: Initializing BL32
I/TC:
I/TC: OP-TEE version: 3.13.0-651-gd84087907 #hisping.lin (gcc version 10.2.1 20201103 (GNU   Toolchain for the A-profile Architecture 10.2-2020.11 (arm-10.16)))                         #5 Fri Sep 16 15:39:33 CST 2022 aarch64
I/TC: Primary CPU initializing
I/TC: Primary CPU switching to normal world boot
INFO:    BL31: Preparing for EL3 exit to normal world
INFO:    Entry point address = 0xa00000
INFO:    SPSR = 0x3c9


U-Boot 2017.09 #gecedu (Aug 17 2025 - 12:43:41 +0800)

Model: Rockchip RK3568 Evaluation Board
PreSerial: 2, raw, 0xfe660000
DRAM:  2 GiB
Sysmem: init
Relocation Offset: 7d23f000
Relocation fdt: 7b9f8f00 - 7b9fecd0
CR: M/C/I
Using default environment

dwmmc@fe2b0000: 1, dwmmc@fe2c0000: 2, sdhci@fe310000: 0
Bootdev(atags): mmc 0
MMC0: HS200, 200Mhz
PartType: EFI
DM: v1
boot mode: loader
FIT: no signed, no conf required
DTB: rk-kernel.dtb
HASH(c): OK
I2c0 speed: 100000Hz
vsel-gpios- not found! Error: -2
vdd_cpu init 900000 uV
PMIC:  RK8090 (on=0x40, off=0x00)
vdd_logic init 900000 uV
vdd_gpu init 900000 uV
vdd_npu init 900000 uV
io-domain: OK
INFO:    ddr dmc_fsp already initialized in loader.
Could not find baseparameter partition
Model: Rockchip RK3568 EVB1 DDR4 V10 Board
Rockchip UBOOT DRM driver version: v1.0.1
VOP have 2 active VP
vp0 have layer nr:3[0 2 4 ], primary plane: 4
vp1 have layer nr:3[1 3 5 ], primary plane: 5
vp2 have layer nr:0[], primary plane: 0
Using display timing dts
dsi@fe060000:  detailed mode clock 51200 kHz, flags[8000000a]
    H: 1024 1184 1186 1346
    V: 0600 0612 0614 0637
bus_format: 100e
VOP update mode to: 1024x600p60, type: MIPI0 for VP0
VP0 set crtc_clock to 51000KHz
VOP VP0 enable Smart0[654x270->654x270@185x165] fmt[2] addr[0x7df04000]
final DSI-Link bandwidth: 336 Mbps x 4
hdmi@fe0a0000 disconnected
enter Rockusb!
RKUSB: LUN 0, dev 0, hwpart 0, sector 0x0, count 0x1d5a000

```

