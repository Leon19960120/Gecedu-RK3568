#!/usr/bin/env python3
"""从 arm64 kernel Image 中提取 IKCONFIG 的 config（gzip）与嵌入 DTB。

用法：
    python3 extract_cfg_dtb.py <kernel_image> [outdir]

默认 outdir = 当前目录。输出：<outdir>/kernel_config.txt 与 <outdir>/kernel_dtb.dtb。
"""
import sys
import os
import struct
import gzip

IKCFG_ST = b"IKCFG_ST"
IKCFG_ED = b"IKCFG_ED"


def extract_config(image_bytes, outpath):
    st = image_bytes.find(IKCFG_ST)
    if st < 0:
        print("  未找到 IKCFG_ST，无内嵌 config")
        return False
    ed = image_bytes.find(IKCFG_ED, st)
    if ed < 0:
        print("  未找到 IKCFG_ED")
        return False
    payload = image_bytes[st + len(IKCFG_ST):ed]
    cfg = None
    for i in range(len(payload)):
        try:
            cfg = gzip.decompress(payload[i:])
            break
        except Exception:
            continue
    if cfg is None:
        print("  config.gz 解压失败")
        return False
    open(outpath, "wb").write(cfg)
    print(f"  提取 config: {len(cfg)} bytes -> {outpath}")
    return True


def find_embedded_dtb(image_bytes, outpath):
    """arm64 Image 中 DTB 以 d00dfeed 开头，返回多个候选中的有效 FDT。"""
    found = []
    off = 0
    while True:
        off = image_bytes.find(b"\xd0\x0d\xfe\xed", off)
        if off < 0:
            break
        found.append(off)
        off += 4
    candidates = []
    for off in found:
        if off + 40 > len(image_bytes):
            continue
        magic, totalsize = struct.unpack_from(">II", image_bytes, off)
        if magic == 0xD00DFEED and 0 < totalsize < 0x400000 and off + totalsize <= len(image_bytes):
            candidates.append((off, totalsize))
    if not candidates:
        print("  未找到有效嵌入 DTB")
        return False
    off, size = max(candidates, key=lambda c: c[1])  # 取最大的 FDT
    open(outpath, "wb").write(image_bytes[off:off + size])
    print(f"  提取嵌入 DTB: {size} bytes @0x{off:x} -> {outpath} (共 {len(candidates)} 个候选)")
    return True


def kernel_version(image_bytes):
    v = image_bytes.find(b"Linux version ")
    if v < 0:
        return "?"
    end = image_bytes.find(b"\n", v)
    return image_bytes[v:end].decode("ascii", "replace").strip()


def check_image(img_path):
    data = open(img_path, "rb").read()
    magic = struct.unpack_from("<I", data, 0)[0]
    print(f"  magic={magic:#x} ({'ARM64 Image' if magic == 0x644d5241 else 'OTHER'})")
    print(f"  Linux version: {kernel_version(data)}")
    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    img_path = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(outdir, exist_ok=True)
    data = check_image(img_path)
    extract_config(data, os.path.join(outdir, "kernel_config.txt"))
    find_embedded_dtb(data, os.path.join(outdir, "kernel_dtb.dtb"))
