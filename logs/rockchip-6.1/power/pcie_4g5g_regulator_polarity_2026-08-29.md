# GPIO3_A4 / 4G5G_3V6 regulator 极性修复证据

> 日期：2026-08-29
>
> 状态：`[VERIFIED RESOLVED]`
>
> 目标：消除 fixed-regulator 的 `GPIO handle specifies active low - ignored` 极性冲突。

## 硬件定位

原理图确认 `GPIO3_A4_d` 直接连接 U400 MP2315 的 `EN` 引脚，中间没有反相器。U400 将 `RAW_12V` 转换为 `4G5G_3V6`，为 J400 MINI_PCIE 52PIN 的 4G/5G 模块供电。

MP2315 的 EN 为高电平使能，因此该 GPIO 应描述为 `GPIO_ACTIVE_HIGH`。

## 修复前

Linux 5.10 和最初复制到 6.1 的 GEC 板级节点同时包含：

```dts
enable-active-high;
gpio = <&gpio3 RK_PA4 GPIO_ACTIVE_LOW>;
```

Linux 6.1.99 #22 启动时打印：

```shell
[    1.812486] gpio-regulator GPIO handle specifies active low - ignored
```

固定 regulator 的兼容逻辑以 `enable-active-high` 为准，忽略 GPIO phandle 中冲突的 active-low flag，因此旧镜像实际仍按高电平使能，但 DTS 表达自相矛盾。

## DTS 修复

文件：

```text
/home/hyl/lubancat-linux-sdk/kernel-6.1/arch/arm64/boot/dts/rockchip/rk3568-evb1-gec-v11.dtsi
```

修改为：

```dts
vcc3v3_pcie: gpio-regulator {
    compatible = "regulator-fixed";
    regulator-name = "vcc3v3_pcie";
    regulator-min-microvolt = <3300000>;
    regulator-max-microvolt = <3300000>;
    enable-active-high;
    regulator-always-on;
    gpio = <&gpio3 RK_PA4 GPIO_ACTIVE_HIGH>;
    startup-delay-us = <5000>;
    vin-supply = <&dc_12v>;
};
```

已编译 `rk3568-evb1-gec-v11-linux.dtb` 的反编译结果为：

```dts
enable-active-high;
gpio = <0x8d 0x04 0x00>;
```

末尾 flag `0x00` 对应 `GPIO_ACTIVE_HIGH`，说明修复已进入 DTB，不只停留在 DTS 源码。

## 板端验证

新镜像启动后连续执行：

```shell
[root@RK356X:/kf2]# dmesg | grep -F 'GPIO handle specifies active low - ignored'
[root@RK356X:/kf2]# dmesg | grep -F 'GPIO handle specifies active low - ignored'
[root@RK356X:/kf2]# [   17.757412] platform mtd_vendor_storage: deferred probe pending
^C
[root@RK356X:/kf2]# dmesg | grep -F 'GPIO handle specifies active low - ignored'
[root@RK356X:/kf2]#
```

三次检索均无匹配；中间的 `mtd_vendor_storage` 是异步打印的另一项 deferred probe，与 regulator 极性无关。

## 结论与边界

以下证据已经闭环：

1. 原理图确认 GPIO3_A4 直接控制高有效 EN。
2. DTS 已改为 `GPIO_ACTIVE_HIGH`。
3. 编译 DTB 已包含 active-high flag。
4. 板端新镜像中原 warning 消失。

因此“PCIe 3.3 V regulator 极性冲突”问题标记为 `[VERIFIED RESOLVED]`。

本结论不等于 J400 或 4G/5G 模块功能已经通过。原理图网络名为 `4G5G_3V6`，而 DTS 仍名为 `vcc3v3_pcie` 并声明 3.3 V；实际输出电压、`regulator-always-on` 策略和 4G/5G 模块枚举应作为后续独立项目验证。
