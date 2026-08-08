# 03 - RKNPU 驱动 / RKNN Runtime / Toolkit2（规划）

> ⚠️ **规划文档，尚未实测。** 这是转 BSP 6.6 的首要动机：在 RK3568 上跑 NPU 推理。
> 未实测成功前不写为"已完成"。

---

## 1. 为什么主线不行

Mainline Linux（任意版本 6.6 / 6.18 / 7.x）**均无 RK3568 NPU 官方驱动**。
主线仅有的 "Rocket" NPU 驱动只支持 RK3588 及更新芯片。社区有把 rknpu 抽成 DKMS 的移植
（`w568w/rknpu-module` 支持到 6.19、`rkojedzinszky/rknpu-dkms` 抽自 Rockchip 6.6.y），
但属于"魔改"，DVFS 关、IOMMU 在 4GB 板上偶有坑，不稳。

**正确做法**：用 **Rockchip BSP 6.6**，其 `rknpu` 是 **in-tree**（`drivers/rknpu/`，DTS `npu@fde40000`），
成熟可用。

---

## 2. 内核侧（BSP 自带）

- 驱动：`drivers/rknpu/`（Rockchip NPU 驱动，in-tree）
- DTS 节点：`npu@fde40000`，BSP 默认启用
- 验证目标：`rknpu.ko` 加载、`dmesg` 见 NPU probe、`/dev/dri/renderD128` 出现

```bash
# 板端验证（预期，待实测）
dmesg | grep -i rknpu
ls /dev/dri/renderD*
```

---

## 3. 用户态：RKNN Runtime + Toolkit2

NPU 计算需用户态库：

| 组件 | 获取 | 说明 |
|------|------|------|
| `librknnrt` | Rockchip 闭源分发（`airockchip/rknn-toolkit2` 仓库内含） | NPU 运行时，需另行获取 |
| `rknn-toolkit2` | <https://github.com/airockchip/rknn-toolkit2> | Python 推理工具链 / 模型转换 |
| 示例模型 | `rknn-toolkit2/examples/` | 如 MobileNet 等 |

> `librknnrt` 是闭源二进制，不在内核树里，需按 Rockchip 许可另行下载并部署到 rootfs。

---

## 4. 验证计划（待执行）

1. BSP 6.6 启动 + `rknpu.ko` 加载成功（见 `02_board_dts.md`）。
2. 在 rootfs 部署 `librknnrt` + `rknn-toolkit2`。
3. 跑一个示例推理（如 MobileNet），确认 NPU 实际工作（非仅驱动加载）。
4. 记录推理性能（FPS / 功耗）到 `logs/`（待建 BSP 日志目录）。

---

## 5. 风险

- `librknnrt` 闭源，版本需与 BSP 内核 / Toolkit2 匹配。
- 4GB 板（2GB LPDDR4）上 IOMMU 偶有坑（社区 DKMS 反馈），BSP in-tree 应更稳，但仍待实测。
- 一切以"实测推理通过"为完成标准，驱动加载 ≠ 推理可用。
