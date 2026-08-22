# 04 - GT911 触摸屏

> 状态：`[BSP-5.10 RUNTIME VERIFIED]`

## 运行时已验证

当前已验证路径：

| 项目 | 值 |
|------|----|
| 总线 | I2C1 |
| 地址 | `0x5d` |
| 驱动日志 | `Goodix-TS 1-005d` |
| Chip ID | `911` |
| Version | `1060` |
| Input name | `Goodix Capacitive TouchScreen` |

不要把 `/dev/input/eventX` 写成固定接口。`eventX` 编号取决于 probe 顺序，每次系统状态变化后都可能不同。

## 驱动冲突

一个已知失败模式是同时启用多套 Goodix 驱动：

```text
CONFIG_TOUCHSCREEN_GOODIX=y
CONFIG_TOUCHSCREEN_GT9XX=y
```

这可能导致：

```text
Driver 'Goodix-TS' is already registered
```

当前方向是只保留一套 Goodix 驱动栈。历史笔记提到过 `GT1X`，最终写入前要以当前 SDK 的 `.config` 为准。

曾确认可工作的配置风格：

```text
CONFIG_TOUCHSCREEN_GOODIX=y
# CONFIG_TOUCHSCREEN_GT1X is not set
# CONFIG_TOUCHSCREEN_GT9XX is not set
```

如果当前 SDK 使用模块方式而不是 built-in，需要同步更新 config fragment 和本文档。
