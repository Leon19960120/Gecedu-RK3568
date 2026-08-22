# DTB 分析工具

从 `tmp_boot_cmp/` 沉淀下来的 DTB 对比/解包脚本，全部 Python3 标准库实现，无第三方依赖。用途是把「反编译 factory DTB → 对比 GEC 板级 DTB」这套 DTS 移植方法论（见 `docs/porting/dts_porting_methodology.md`）工具化。

## 脚本清单

| 脚本 | 用途 | 用法 |
|------|------|------|
| `unpack_boot.py` | 解包 boot.img（自动识别 FIT / uImage），提取内核与 DTB | `python3 unpack_boot.py <boot.img> [outdir]` |
| `extract_cfg_dtb.py` | 从 arm64 kernel Image 提取 IKCONFIG 内核配置 + 嵌入 DTB | `python3 extract_cfg_dtb.py <kernel_image> [outdir]` |
| `dtb2dts.py` | DTB → 可读 DTS 文本（属性值智能识别字符串/u32 数组/字节） | `python3 dtb2dts.py <a.dtb> [b.dtb ...]` |
| `dtb_cmp.py` | 按节点路径对比两个 DTB，输出「仅官方 / 仅 gec / 属性差异」 | `python3 dtb_cmp.py <a.dtb> <b.dtb>` |
| `dtb_cmp2.py` | 对比前先把 phandle 解析成节点路径，聚焦语义差异（引用属性不再误判） | `python3 dtb_cmp2.py <a.dtb> <b.dtb>` |

## 典型流程（移植一个板级 DTB）

```bash
# 1. 从官方 boot.img 提取 kernel + DTB
python3 scripts/dtb/unpack_boot.py 官方boot.img /tmp/official

# 2. 从自编 kernel Image 提取内嵌 config + DTB
python3 scripts/dtb/extract_cfg_dtb.py 自编Image /tmp/custom

# 3. 反编译两个 DTB 看结构
python3 scripts/dtb/dtb2dts.py /tmp/official/fit_fdt /tmp/custom/kernel_dtb.dtb

# 4. 对比差异（先按路径，再用 phandle→path 的语义对比）
python3 scripts/dtb/dtb_cmp.py  /tmp/official/fit_fdt /tmp/custom/kernel_dtb.dtb
python3 scripts/dtb/dtb_cmp2.py /tmp/official/fit_fdt /tmp/custom/kernel_dtb.dtb
```

对比结果的差异要按方法论分三类（见 `docs/porting/dts_porting_methodology.md` §3）：

- **BOARD_DELTA**（板级差异）→ 落盘到 override 层
- **BSP_DRIFT**（BSP 版本演进）→ 不落盘
- **ARTIFACT**（phandle 重编号等噪声）→ 忽略（`dtb_cmp2.py` 已把 phandle 解析成路径，能自动消除大部分 ARTIFACT）

## 注意

- 这些脚本是**只读分析**工具，不改任何 DTB / 配置。
- `dtb_cmp2.py` 是 `dtb_cmp.py` 的升级版（phandle→路径），优先用 `cmp2`。
- 原始数据（factory DTB、反编译产物）不在此目录，脚本只接受命令行参数，不硬编码路径。
