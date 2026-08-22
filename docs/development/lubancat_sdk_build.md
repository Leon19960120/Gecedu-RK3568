# 野火鲁班猫 LubanCat SDK 主机环境搭建与构建参考

> 来源：野火官方《嵌入式Linux镜像构建与部署》指南摘录 + 实操整理。
> 适用：RK3568（鲁班猫2 系列）等，使用**通用 SDK**（manifest: `lubancat_linux_generic_20260729.xml`）。

## 1. 主机环境（Ubuntu LTS）

装编译依赖：

```bash
sudo apt install git ssh make gcc libssl-dev liblz4-tool u-boot-tools curl \
expect g++ patchelf chrpath gawk texinfo bison flex fakeroot cmake \
gcc-multilib g++-multilib unzip device-tree-compiler python-pip \
libncurses5-dev python3-pyelftools dpkg-dev
```

装 `repo`：

```bash
mkdir ~/bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo
echo PATH=~/bin:$PATH >> ~/.bashrc
source ~/.bashrc
repo --version   # 验证
```

切 Python（确保 `python` 指向 python3）：

```bash
ls /usr/bin/python*
sudo ln -sf /usr/bin/python3 /usr/bin/python
python -V
```

## 2. 拉取源码：通用 SDK vs 专用 SDK

| 维度 | 专用 SDK | 通用 SDK（2024.7 起主推） |
|---|---|---|
| 覆盖 | 一个 SoC 一份 | 一份编多 SoC（rk3562/3566/3568/3576/3588…） |
| 稳定性 | 旧、更稳 | 内核更新、新特性多 |
| 空间 | 多份重复 | 省空间 |
| 维护 | 预存档期 | 长期维护 |

- 通用 SDK 拉取：
  ```bash
  repo --trace init --depth=1 -u https://github.com/LubanCat/manifests.git -b linux -m lubancat_linux_generic.xml
  ```
- 卡 `clone.bundle` 时加 `--repo-url https://mirrors.tuna.tsinghua.edu.cn/git/git-repo`
- 专用 SDK（rk356x 例）：`-m rk356x_linux_release.xml`

## 3. 更新同步

```bash
.repo/repo/repo sync -c -j4
# 浅克隆只拉最新一次提交，要全量历史：
cd kernel && git fetch --unshallow
```

## 4. 构建镜像

一键流程（交互菜单）：

```bash
./build.sh chip     # 选处理器系列
./build.sh lunch    # 选板卡配置（输入序号）
./build.sh          # 一键全编
```

单步编译（推荐，避免 rootfs 全编失败卡住）：

```bash
./build.sh uboot     # 只编 U-Boot（同时打包 BL31+OP-TEE 到 uboot.img）
./build.sh kernel    # 只编内核 + DTB → boot.img
./build.sh debian    # 编 Debian rootfs
./build.sh updateimg # 打包 update.img，产物在 rockdev/
```

> 关键点：U-Boot / Kernel 各系统通用，**仅 rootfs 因系统而异**；镜像在 `rockdev/`。

## 5. 常见坑：浅克隆导致无法更新

报错 `无效的上游 xxx^1` 或 `合并冲突于 xxx_linux_release.xml`（源于 `--depth=1`）：

1. 删 `.repo/manifests.git/.repo_config.json` 里的：
   ```
   "repo.depth": ["1"]
   ```
2. 冲突类再进 `.repo/manifests` 执行 `git rebase --abort`
3. 重新 `.repo/repo/repo sync -c`

## 6. 本仓库实操记录（GEC-RK3568 项目）

- `./build.sh u-boot` 已成功产出：`uboot.img`（含 ATF/OP-TEE/U-Boot FIT）+ `rk356x_spl_loader_v1.23.114.bin`（SPL+DDR）
- `./build.sh kernel` 已成功产出 `output/firmware/boot.img`（5.10.209 + EVB1 DTB）
- rootfs 全编失败根因：**开发机 GNU Make 4.4.1 太新**，被 `check-host-make.sh` 拒绝（非依赖缺失）。解决：装 make 4.2/4.3 放 PATH 最前，或 `./build.sh` 只编 uboot/kernel 跳过 rootfs。
- 注意：`build.sh` **带参数=静默直编，不带参数=弹交互菜单**。之前「进终端自动编译」是 `.bashrc` 里误加了 `./build.sh`（无参→弹菜单阻塞），删掉该行即恢复。
