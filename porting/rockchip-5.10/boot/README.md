# BSP 5.10 启动说明

BSP 5.10 的 boot image 由 LubanCat SDK 生成。生成出的 `boot.img` 不应提交到本目录。

每次都要验证：

```text
source DTS
→ built DTB/FIT
→ running DTB model and compatible strings
```

期望运行时 model：

```text
Rockchip RK3568 GEC DDR4 V10 Board
```
