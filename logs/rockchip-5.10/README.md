# Rockchip BSP 5.10 运行日志

本目录用于保存 BSP 5.10 的运行证据。不要伪造日志；只有从真实硬件采集到串口输出或命令输出后，才加入这里。

建议分组：

| 目录 | 证据 |
|------|------|
| `boot/` | U-Boot + kernel 启动日志、model / compatible 证明 |
| `display/` | DRM、DSI、panel、backlight 日志 |
| `touch/` | Goodix GT911 probe 与 input 注册 |
| `iio/` | SARADC、MPU6050、BH1750 sysfs 与 dmesg |
| `rtc/` | RK809 RTC 与 PCF8563 RTC 日志 |
| `power/` | PowerKey 与 suspend entry 日志、电源轨核对 |
| `can/` | SocketCAN 配置与运行测试 |
| `npu/` | RKNPU probe 与 RKNN inference 日志 |

## 已归档证据

| 证据页 | 内容 |
|--------|------|
| `display/logo_vp0_route.md` | DSI 启动 logo 根因（`route_dsi0` 回 VP0）+ U-Boot/内核日志 |
| `iio/bh1750_iio.md` | BH1750 probe + 实测照度读数（raw/scale/lux） |
| `power/regulator_audit.md` | DTS⇄运行时电源轨全量核对（含 vccio_acodec 偏差记录） |

（持续归档：新证据按上表格式加一行。）

## 采集脚本

可使用下面两个只读脚本采集一致快照：

```bash
sh scripts/check_bsp_5_10.sh
sh scripts/check_i2c_bindings.sh
```
