#!/usr/bin/env python3
"""DTB -> 可读 DTS 文本（用于对比），输出节点树 + 属性。
属性值智能识别：字符串 / 字符串数组 / u32 数组 / 字节。

用法：
    python3 dtb2dts.py foo.dtb [bar.dtb ...]
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
    assert magic == 0xD00DFEED, f"bad FDT magic {magic:#x}"
    totalsize = struct.unpack_from(">I", data, 4)[0]
    off_struct = struct.unpack_from(">I", data, 8)[0]
    off_strings = struct.unpack_from(">I", data, 12)[0]
    size_strings = struct.unpack_from(">I", data, 32)[0]
    strings = data[off_strings:off_strings + size_strings]

    def get_string(off):
        end = strings.find(b"\0", off)
        return strings[off:end].decode("ascii", "replace")

    root = {"name": "", "props": [], "children": []}
    stack = [root]
    pos = off_struct
    end_limit = off_struct + (totalsize - off_struct)
    while pos < end_limit:
        tag = struct.unpack_from(">I", data, pos)[0]
        pos += 4
        if tag == FDT_BEGIN_NODE:
            end = data.find(b"\0", pos)
            name = data[pos:end].decode("ascii", "replace")
            node = {"name": name, "props": [], "children": []}
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
            stack[-1]["props"].append((get_string(nameoff), value))
        elif tag == FDT_NOP:
            pass
        elif tag == FDT_END:
            break
        else:
            raise ValueError(f"unknown tag {tag}")
    return root


def fmt_prop_value(v):
    if not v:
        return ""
    # 字符串数组
    if v[-1] == 0:
        parts = []
        s = b""
        for b in v:
            if b == 0:
                if s:
                    parts.append(s)
                s = b""
            else:
                s += bytes([b])
        if all(all(0x20 <= c < 0x7f for c in p) for p in parts) and parts:
            out = []
            for p in parts:
                if len(p) == 0:
                    continue
                txt = p.decode("ascii")
                if any(c in txt for c in '",\\'):
                    txt = txt.replace("\\", "\\\\").replace('"', '\\"')
                out.append(f'"{txt}"')
            if out and not any(b == 0 for b in v) is False:
                return "".join(out) if len(out) == 1 else " ".join(out)
    # u32 数组（长度 4 的倍数且都合理）
    if len(v) % 4 == 0:
        vals = struct.unpack(f">{len(v)//4}I", v)
        if all(x < 0x100000000 for x in vals):
            return "<" + " ".join(f"0x{x:08x}" if x > 0xFF else f"{x}" for x in vals) + ">"
    # 字节
    return "[" + " ".join(f"{b:02x}" for b in v) + "]"


def fmt_strings(v):
    """显式字符串数组"""
    parts = [p for p in v.split(b"\0") if p]
    out = []
    for p in parts:
        txt = p.decode("ascii", "replace")
        txt = txt.replace("\\", "\\\\").replace('"', '\\"')
        out.append(f'"{txt}"')
    return " ".join(out)


def dumps(root, indent=0, out=None):
    if out is None:
        out = []
    pad = "  " * indent
    name = root["name"]
    out.append(f"{pad}{name} {{")
    for pname, pval in root["props"]:
        if pname in ("compatible", "model", "status", "name", "label", "type") or (
                pval and pval[-1] == 0 and all(0x20 <= c < 0x7f for c in pval.rstrip(b"\0"))):
            if pname in ("compatible", "rockchip,grf") or (pval and pval[-1] == 0):
                if pval.count(b"\0") > 1:
                    val = fmt_strings(pval)
                else:
                    txt = pval.rstrip(b"\0").decode("ascii", "replace")
                    txt = txt.replace("\\", "\\\\").replace('"', '\\"')
                    val = f'"{txt}"'
            else:
                val = fmt_prop_value(pval)
        else:
            val = fmt_prop_value(pval)
        out.append(f"{pad}  {pname} = {val};")
    for c in root["children"]:
        dumps(c, indent + 1, out)
    out.append(f"{pad}}};")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for path in sys.argv[1:]:
        data = open(path, "rb").read()
        root = parse_fdt(data)
        lines = dumps(root)
        print(f"// ==== {path} ====")
        print("\n".join(lines))
