#!/usr/bin/env python3
"""解包 boot.img：自动识别 U-Boot FIT 镜像 与 legacy uImage 镜像，提取内核与 DTB。

用法：
    python3 unpack_boot.py <boot.img> [outdir]

- FIT（FDT magic 0xd00dfeed）：按 /images/<name> 的 data-position 提取各子镜像，命名 fit_<name>。
- uImage（magic 0x27051956）：提取内核负载，gzip 压缩时解压为 uimage_kernel_image。
"""
import struct
import sys
import os
import gzip

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

    root = {"name": "", "props": {}, "children": []}
    stack = [root]
    pos = off_struct
    while pos < off_struct + (totalsize - off_struct):
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
        else:
            raise ValueError(f"unknown FDT tag {tag} at {pos-4:#x}")
    return root


def walk(node, path=""):
    p = f"{path}/{node['name']}" if node["name"] else path
    yield p, node
    for c in node["children"]:
        yield from walk(c, p)


def u32(v):
    return struct.unpack(">I", v)[0]


def extract_fit(data, outdir):
    root = parse_fdt(data)
    images = None
    for p, n in walk(root):
        if p == "/images":
            images = n
    assert images, "no /images node"
    out = {}
    for sub in images["children"]:
        name = sub["name"]
        props = sub["props"]
        data_pos = u32(props.get("data-position", b"\x00" * 4))
        data_size = u32(props.get("data-size", b"\x00" * 4))
        payload = data[data_pos:data_pos + data_size]
        typ = props.get("type", b"").decode()
        out[name] = {"payload": payload, "type": typ}
        fn = os.path.join(outdir, f"fit_{name}")
        open(fn, "wb").write(payload)
        print(f"  [FIT] {name}: type={typ} size={data_size} @0x{data_pos:x} -> {fn}")
    return out


def extract_uimage(data, outdir):
    magic = struct.unpack_from(">I", data, 0)[0]
    assert magic == 0x27051956, f"not uImage, magic {magic:#x}"
    size = struct.unpack_from(">I", data, 12)[0]
    load = struct.unpack_from(">I", data, 16)[0]
    ep = struct.unpack_from(">I", data, 20)[0]
    os_, arch, typ, comp = data[28], data[29], data[30], data[31]
    name = data[32:64].split(b"\0")[0].decode()
    payload = data[64:64 + size]
    os_names = {5: "linux"}
    arch_names = {22: "arm64", 2: "arm"}
    type_names = {2: "kernel", 1: "multi"}
    comp_names = {0: "none", 1: "gzip", 2: "bzip2", 3: "lzma", 4: "lzo", 5: "lz4"}
    print(f"  [uImage] name={name} size={size} load={load:#x} ep={ep:#x} "
          f"os={os_names.get(os_, os_)} arch={arch_names.get(arch, arch)} "
          f"type={type_names.get(typ, typ)} comp={comp_names.get(comp, comp)}")
    fn = os.path.join(outdir, "uimage_payload")
    open(fn, "wb").write(payload)
    if comp == 1:
        try:
            dec = gzip.decompress(payload)
            out = os.path.join(outdir, "uimage_kernel_image")
            open(out, "wb").write(dec)
            print(f"  [uImage] gzip 解压成功 -> {out} ({len(dec)} bytes)")
        except Exception as e:
            print(f"  [uImage] gzip 解压失败: {e}")
    return payload


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(outdir, exist_ok=True)
    data = open(path, "rb").read()
    magic = struct.unpack_from(">I", data, 0)[0]
    if magic == 0xD00DFEED:
        print(f"== {path} (FIT) ==")
        extract_fit(data, outdir)
    elif magic == 0x27051956:
        print(f"== {path} (uImage) ==")
        extract_uimage(data, outdir)
    else:
        print(f"无法识别镜像类型（magic {magic:#x}），既非 FIT 也非 uImage")
        sys.exit(1)
