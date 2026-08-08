分区表

```bash
root@RK356X:~# fdisk -l
Found valid GPT with protective MBR; using GPT

Disk /dev/mmcblk0: 30777344 sectors, 2740M
Logical sector size: 512
Disk identifier (GUID): 73987b6b-4974-4c94-a3e8-58ab2eb7a946
Partition table holds up to 128 entries
First usable sector is 34, last usable sector is 30777310

Number  Start (sector)    End (sector)  Size Name
     1           16384           24575 4096K uboot
     2           24576           32767 4096K misc
     3           32768           98303 32.0M boot
     4           98304          163839 32.0M recovery
     5          163840          229375 32.0M backup
     6          229376        12812287 6144M rootfs
     7        12812288        13074431  128M oem
     8        13074432        13107199 16.0M logo
     9        13107200        30777310 8627M userdata

```



```bash
# 1. 开发板硬件配置（非常重要）
cat BoardConfig.xml
root@RK356X:/info# cat BoardConfig.xml
#!/bin/bash

# Target arch
export RK_ARCH=arm64
# Uboot defconfig
export RK_UBOOT_DEFCONFIG=rk3568
# Uboot image format type: fit(flattened image tree)
export RK_UBOOT_FORMAT_TYPE=fit
# Kernel defconfig
export RK_KERNEL_DEFCONFIG=rockchip_linux_defconfig
# Kernel defconfig fragment
export RK_KERNEL_DEFCONFIG_FRAGMENT=
# Kernel dts
export RK_KERNEL_DTS=rk3568-evb1-ddr4-v10-linux
# boot image type
export RK_BOOT_IMG=boot.img
# kernel image path
export RK_KERNEL_IMG=kernel/arch/arm64/boot/Image
# kernel image format type: fit(flattened image tree)
export RK_KERNEL_FIT_ITS=boot.its
# parameter for GPT table
export RK_PARAMETER=parameter-buildroot-fit.txt
# Buildroot config
export RK_CFG_BUILDROOT=rockchip_rk3568
# Recovery config
export RK_CFG_RECOVERY=rockchip_rk356x_recovery
# Recovery image format type: fit(flattened image tree)
export RK_RECOVERY_FIT_ITS=boot4recovery.its
# ramboot config
export RK_CFG_RAMBOOT=
# Pcba config
export RK_CFG_PCBA=
# Build jobs
export RK_JOBS=12
# target chip
export RK_TARGET_PRODUCT=rk356x
# Set rootfs type, including ext2 ext4 squashfs
export RK_ROOTFS_TYPE=ext4
# Set debian version (debian10: buster, debian11: bullseye)
export RK_DEBIAN_VERSION=buster
# yocto machine
export RK_YOCTO_MACHINE=rockchip-rk3568-evb
# rootfs image path
export RK_ROOTFS_IMG=rockdev/rootfs.${RK_ROOTFS_TYPE}
# Set ramboot image type
export RK_RAMBOOT_TYPE=
# Set oem partition type, including ext2 squashfs
export RK_OEM_FS_TYPE=ext2
# Set userdata partition type, including ext2, fat
export RK_USERDATA_FS_TYPE=ext2
#OEM config
export RK_OEM_DIR=oem_normal
# OEM build on buildroot
#export RK_OEM_BUILDIN_BUILDROOT=YES
#userdata config
export RK_USERDATA_DIR=userdata_normal
#misc image
export RK_MISC=wipe_all-misc.img
#choose enable distro module
export RK_DISTRO_MODULE=
# Define pre-build script for this board
export RK_BOARD_PRE_BUILD_SCRIPT=app-build.sh


# 2. 内核符号表（很大，内容极多）
cat System.map-4.19

# 3. 开机动画日志
cat bootanim.log

root@RK356X:/info# cat bootanim.log
Starting bootanim: 464...
Starting hook: /etc/bootanim.d/gst-bootanim.sh...
Stopping bootanim: none for 464...


# 4. 系统时钟汇总
cat clk_summary

# 5. 内核启动参数
cat cmdline
root@RK356X:/info# cat cmdline
storagemedia=emmc androidboot.storagemedia=emmc androidboot.mode=normal  androidboot.verifiedbootstate=orange rw rootwait earlycon=uart8250,mmio32,0xfe660000 console=ttyFIQ0 root=PARTUUID=614e0000-0000


# 6. 内核编译配置
cat config-4.19

# 7. CPU 信息（写文档必用）
cat cpuinfo

# 8. 磁盘统计信息
cat diskstats

# 9. DMA 缓冲信息
cat dma_buf

# 10. 文件系统挂载表
cat fstab

# 11. GPIO 信息
cat gpio
root@RK356X:/info# cat gpio
gpiochip0: GPIOs 0-31, parent: platform/fdd60000.gpio, gpio0:
 gpio-6   (                    |vcc5v0_otg          ) out lo
 gpio-23  (                    |vcc3v3_lcd0_n       ) out hi
 gpio-29  (                    |vcc3v3_vga          ) out hi

gpiochip1: GPIOs 32-63, parent: platform/fe740000.gpio, gpio1:
 gpio-40  (                    |GPIO Key UP         ) in  hi
 gpio-42  (                    |GPIO Key DOWN       ) in  hi

gpiochip2: GPIOs 64-95, parent: platform/fe750000.gpio, gpio2:
 gpio-73  (                    |bt_default_rts      ) in  hi
 gpio-79  (                    |bt_default_reset    ) out lo
 gpio-80  (                    |bt_default_wake_host) in  hi
 gpio-82  (                    |bt_default_wake     ) in  lo
 gpio-84  (                    |reset               ) out hi
 gpio-94  (                    |reset               ) out lo

gpiochip3: GPIOs 96-127, parent: platform/fe760000.gpio, gpio3:
 gpio-98  (                    |spk-ctl             ) out lo
 gpio-100 (                    |vcc3v3_pcie         ) out hi
 gpio-103 (                    |reset               ) out hi
 gpio-107 (                    |irq                 ) in  hi
 gpio-108 (                    |reset               ) in  hi
 gpio-109 (                    |mdio-reset          ) out hi
 gpio-111 (                    |sysfs               ) out lo
 gpio-114 (                    |Headphone detection ) in  lo
 gpio-120 (                    |sysfs               ) out lo
 gpio-121 (                    |sysfs               ) out lo
 gpio-123 (                    |sysfs               ) out lo
 gpio-124 (                    |sysfs               ) out lo

gpiochip4: GPIOs 128-159, parent: platform/fe770000.gpio, gpio4:

gpiochip5: GPIOs 511-511, parent: platform/rk805-pinctrl, rk817-gpio, can sleep:

# 12. 中断信息
cat interrupts

# 13. 物理内存映射
cat iomem

# 14. 内核符号（非常大）
cat kallsyms

# 15. 内存信息（2GB LPDDR4 看这里）
cat meminfo

# 16. 挂载日志
cat mount-all.log

# 17. 系统版本信息
cat os-release
root@RK356X:/info# cat os-release
NAME=Buildroot
VERSION=2018.02-rc3-dirty
ID=buildroot
VERSION_ID=2018.02-rc3
PRETTY_NAME="Buildroot 2018.02-rc3"
BUILD_INFO="gecedu@Gecedu Sun Aug 17 12:45:22 CST 2025 - /home/gecedu/file_share/code_rk3568/gec-rk3568-linuxrelease/RK356X_Linux_V1.3.2/buildroot/configs/rockchip_rk3568_defconfig"
KERNEL="4.19 - rockchip_linux_defconfig"
root@RK356X:/info#

# 18. 分区信息
cat partitions

# 19. 引脚复用配置
cat pinctrl

# 20. 分区扩容日志
cat resize-all.log

# 21. RK DMA 缓冲
cat rk_dmabuf

# 22. 内核 slab 内存信息
cat slabinfo

# 23. 软中断统计
cat softirqs

# 24. USB 设备日志
cat usbdevice.log
root@RK356X:/info# cat usbdevice.log
[2026-05-09 22:18:59] Handling start request
[2026-05-09 22:18:59] Run stage: usb_prepare
[2026-05-09 22:18:59] Run stage: usb_init
[2026-05-09 22:18:59] Initializing
[2026-05-09 22:18:59] Run stage: usb_start
[2026-05-09 22:18:59] Starting functions: adb
[2026-05-09 22:18:59] Preparing instance: ffs.adb
[2026-05-09 22:18:59] Run stage: adb_prepare
[2026-05-09 22:18:59] Starting instance: ffs.adb
[2026-05-09 22:18:59] Done start request



# 25. 内核版本
cat version
root@RK356X:/info# cat version
Linux version 4.19.232 (gecedu@Gecedu) (gcc version 10.3.1 20210621 (GNU Toolchain for the A-profile Architecture 10.3-2021.07 (arm-10.29)), GNU ld (GNU Toolchain for the A-profile Architecture 10.3-2021.07 (arm-10.29)) 2.36.1.20210621) #5 SMP Thu Aug 14 19:27:53 CST 2025


# 26. 唤醒源信息
cat wakeup_sources
```







