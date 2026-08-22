#!/usr/bin/env python3
"""将两个 DTB 的 phandle 解析为节点路径后对比，聚焦语义差异（引用属性不再误判为纯数值不同）。

用法：
    python3 dtb_cmp2.py a.dtb b.dtb
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


def walk(node, path="", m=None, ph2path=None):
    if m is None:
        m = {}
        ph2path = {}
    p = f"{path}/{node['name']}" if node["name"] else path or "/"
    m[p] = node["props"]
    if "phandle" in node["props"]:
        ph = struct.unpack(">I", node["props"]["phandle"])[0]
        ph2path[ph] = p
    if "linux,phandle" in node["props"]:
        ph = struct.unpack(">I", node["props"]["linux,phandle"])[0]
        ph2path[ph] = p
    for c in node["children"]:
        walk(c, p, m, ph2path)
    return m, ph2path


REF_PROPS = ("bus-supply", "cpu-supply", "gpu-supply", "npu-supply", "sram-supply",
             "power-supply", "vccio-supply", "vdd-supply", "ldo1-supply", "dram-supply",
             "operating-points-v2", "power-domains", "clock-parents", "assigned-clock-parents",
             "interrupt-parent", "pmu", "rockchip,pmu", "cpu", "clocks", "resets",
             "rockchip,grf", "rockchip,pmugrf", "rockchip,pipe-grf", "rockchip,pipe-phy-grf")


def fmt_val(v, ph2path, clock_style=False):
    if not v:
        return "(empty)"
    if v[-1] == 0 and all(0x20 <= c < 0x7f for c in v.rstrip(b"\0")):
        return "|".join(p.decode("ascii", "replace") for p in v.rstrip(b"\0").split(b"\0"))
    if len(v) % 4 == 0:
        vals = struct.unpack(f">{len(v)//4}I", v)
        out = []
        for i, x in enumerate(vals):
            if clock_style:
                if i % 2 == 0 and x in ph2path:
                    out.append(f"@{ph2path[x]}")
                elif i % 2 == 0:
                    out.append(f"ph:{x:#x}")
                else:
                    out.append(f"{x:#x}")
            elif x in ph2path:
                out.append(f"@{ph2path[x]}")
            else:
                out.append(f"{x:#x}")
        if len(out) <= 8:
            return "<" + " ".join(out) + ">"
        return f"<{len(out)} words>"
    return v.hex()


def render(d, m, ph2path):
    out = {}
    for p, props in m.items():
        rp = {}
        for k, v in props.items():
            if k == "phandle" or k == "linux,phandle":
                continue
            if k in ("clocks", "resets", "assigned-clocks", "assigned-clock-parents",
                     "clock-names", "reset-names"):
                rp[k] = fmt_val(v, ph2path, clock_style=True)
            elif k in REF_PROPS or k.startswith("clocks"):
                rp[k] = fmt_val(v, ph2path)
            else:
                rp[k] = fmt_val(v, {})  # 非引用属性不解析 phandle
        out[p] = rp
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    a = parse_fdt(open(sys.argv[1], "rb").read())
    b = parse_fdt(open(sys.argv[2], "rb").read())
    ma, pha = walk(a)
    mb, phb = walk(b)
    ra = render(a, ma, pha)
    rb = render(b, mb, phb)

    only_a = sorted(set(ra) - set(rb))
    only_b = sorted(set(rb) - set(ra))
    common = sorted(set(ra) & set(rb))
    print(f"节点: 官方={len(ra)} gec={len(rb)} 共有={len(common)} 仅官方={len(only_a)} 仅gec={len(only_b)}")

    print("\n===== 语义属性差异（引用已解析为路径）=====")
    n = 0
    for p in common:
        pa, pb = ra[p], rb[p]
        diff = {}
        for k in set(pa) | set(pb):
            if pa.get(k) != pb.get(k):
                diff[k] = (pa.get(k), pb.get(k))
        if not diff:
            continue
        n += 1
        print(f"\n[{p}]")
        for k, (va, vb) in sorted(diff.items()):
            if va is None:
                print(f"  +gec有: {k} = {vb}")
            elif vb is None:
                print(f"  -官有: {k} = {va}")
            else:
                print(f"  ~ {k}: 官={va} | gec={vb}")
    print(f"\n共 {n} 个共有节点存在语义差异")
