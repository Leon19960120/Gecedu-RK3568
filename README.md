# RK3568B2
粤嵌开发板
一、核心硬件信息
SoC: Rockchip RK3568（4 核 Cortex-A55）  
内存: 约 2GB（2078720K），可用约 1.95GB  
存储: 14.7GB eMMC（DA2016），分区表正常（p1-p9）  
内核版本: 4.19.232（编译于 2025 年 8 月 14 日）  
二、启动成功的组件  
CPU: 4 核全部成功启动，运行在 EL2 异常级别  
存储: eMMC 识别正常，根文件系统（ext4）成功挂载于 mmcblk0p6  
USB: USB 2.0 Hub 识别成功  
GPU: Mali GPU 初始化完成  
NPU: 神经网络处理器初始化完成  
音频: RK809 声卡初始化成功（耳机检测有小问题）  
触摸: Goodix 触摸屏识别成功 
救砖过程  
MiniLoaderAll.bin来源于互联网
https://img.alicdn.com/bao/uploaded/i3/O1CN01t8N4aa2FbniPtguiI~livephoto~_!!4611686018427383427-53-fleamarket.heic_790x10000Q90.jpg_.webp
