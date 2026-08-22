#!/usr/bin/env python3
"""结构化对比两个 DTB：按节点路径对比属性，输出差异摘要。

用法：
    python3 dtb_cmp.py a.dtb b.dtb

（a=官方基线，b=GEC 板级 DTB；输出「仅官方 / 仅 gec / 属性差异」，最后聚焦 npu/iommu/busnpu/gec 相关节点。）
"""
import struct
import sys

FDT_BEGIN_NODE = 1
FDT_END_NODE = 2
FDT_PROP = 3
FDT_NOP = 4
FDT_END = 9


def parse_fdt(data):
    magic = struct.unpack_from(">I", data, 0)[0]
    assert magic == 0xD00DFEED
    totalsize = struct.unpack_from(">I", data, 4)[0]
    off_struct = struct.unpack_from(">I", data, 8)[0]
    off_strings = struct.unpack_from(">I", data, 12)[0]
    size_strings = struct.unpack_from(">I", data, 32)[0]
    strings = data[off_strings:off_strings + size_strings]

    def get_string(off):
        end = strings.find(b"\0", off)
        return strings[off:end].decode("ascii", "replace")

    root = {"name": "", "props": {}, "children": []}
    stack = [root]
    pos = off_struct
    end_limit = off_struct + (totalsize - off_struct)
    while pos < end_limit:
        tag = struct.unpack_from(">I", data, pos)[0]
        pos += 4
        if tag == FDT_BEGIN_NODE:
            end = data.find(b"\0", pos)
            name = data[pos:end].decode("ascii", "replace")
            node = {"name": name, "props": {}, "children": []}
            stack[-1]["children"].append(node)
            stack.append(node)
            pos = (end + 1 + 3) & ~3
        elif tag == FDT_END_NODE:
            stack.pop()
        elif tag == FDT_PROP:
            plen, nameoff = struct.unpack_from(">II", data, pos)
            pos += 8
            value = data[pos:pos + plen]
            pos = (pos + plen + 3) & ~3
            stack[-1]["props"][get_string(nameoff)] = value
        elif tag == FDT_NOP:
            pass
        elif tag == FDT_END:
            break
    return root


def build_map(node, path="", m=None):
    if m is None:
        m = {}
    p = f"{path}/{node['name']}" if node["name"] else path or "/"
    m[p] = node["props"]
    for c in node["children"]:
        build_map(c, p, m)
    return m


def fmt(v):
    if not v:
        return "(empty)"
    if v[-1] == 0 and all(0x20 <= c < 0x7f for c in v.rstrip(b"\0")):
        return ",".join(p.decode("ascii", "replace") for p in v.rstrip(b"\0").split(b"\0"))
    if len(v) % 4 == 0:
        vals = struct.unpack(f">{len(v)//4}I", v)
        if len(v) <= 16:
            return "<" + " ".join(f"0x{x:x}" for x in vals) + ">"
        return f"<{len(vals)} words>"
    return v.hex()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    a = build_map(parse_fdt(open(sys.argv[1], "rb").read()))
    b = build_map(parse_fdt(open(sys.argv[2], "rb").read()))

    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    common = sorted(set(a) & set(b))

    print(f"== 节点统计: 官方={len(a)}  gec={len(b)} 共有={len(common)}")
    print(f"仅官方有: {len(only_a)}  仅gec有: {len(only_b)}")
    print()

    print("===== 仅官方有的节点 (前 60) =====")
    for p in only_a[:60]:
        print(" +", p)
    if len(only_a) > 60:
        print(f" ... 共 {len(only_a)} 个")
    print()

    print("===== 仅 gec 有的节点 (全部) =====")
    for p in only_b:
        print(" +", p)
    print()

    print("===== 共有节点中属性不同的 (前 80) =====")
    cnt = 0
    for p in common:
        pa, pb = a[p], b[p]
        if pa == pb:
            continue
        only_ak = sorted(set(pa) - set(pb))
        only_bk = sorted(set(pb) - set(pa))
        diff_k = sorted(k for k in set(pa) & set(pb) if pa[k] != pb[k])
        if cnt >= 80:
            continue
        cnt += 1
        print(f"[{p}]")
        for k in only_ak:
            print(f"   -官: {k} = {fmt(pa[k])}")
        for k in only_bk:
            print(f"   +gec: {k} = {fmt(pb[k])}")
        for k in diff_k:
            print(f"   ~ {k}: 官={fmt(pa[k])}  gec={fmt(pb[k])}")
    print()
    print("===== 涉及 npu/iommu/busnpu/gec 的节点差异 =====")
    for p in sorted(set(only_a) | set(only_b)):
        if any(k in p.lower() for k in ("npu", "iommu", "bus", "gec")):
            tag = "仅官方" if p in only_a else "仅gec"
            print(f"  [{tag}] {p}")
    for p in common:
        pa, pb = a[p], b[p]
        if pa == pb:
            continue
        if any(k in p.lower() for k in ("npu", "iommu", "bus", "gec")):
            print(f"  [属性差异] {p}")
            for k in sorted(set(pa) ^ set(pb)):
                if k in pa and k not in pb:
                    print(f"     -官: {k} = {fmt(pa[k])}")
                elif k in pb and k not in pa:
                    print(f"     +gec: {k} = {fmt(pb[k])}")
            for k in sorted(set(pa) & set(pb)):
                if pa[k] != pb[k]:
                    print(f"     ~ {k}: 官={fmt(pa[k])} | gec={fmt(pb[k])}")
