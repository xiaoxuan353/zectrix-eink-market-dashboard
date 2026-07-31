# 📟 Zectrix E-Ink Market Dashboard (Zectrix 水墨屏 A股/科技板块实时看盘看板)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-brightgreen.svg" alt="Platform">
  <img src="https://img.shields.io/badge/E--Paper-Zectrix%20Note-orange.svg" alt="E-Paper">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

专为 **Zectrix 极趣云水墨屏 (Zectrix Note / E-Paper Display)** 打造的开源 A 股 / 科技板块 / 自选基金实时盘中看盘看板。

本项目解决了一般水墨屏推送图片时**文字发糊、噪点散落、排版参差不齐**的硬核难题。通过 **1-Bit Mode 1 纯单色调色板 + 云端 `dither=false` 噪点直通技术**，结合**精细宋体 (SimSun) 2-Column 像素级双列网格**，在巴掌大小的水墨屏上实现类似电子书/真纸雕刻般的黑白极高清看盘体验！

---

## ✨ 核心特性

- ⚡ **实时盘中行情抓取**：直连新浪财经官方 API，秒级解析 14 大核心科技/自选板块盘中最新涨跌幅（自动按涨跌幅降序排列）。
- 🖼️ **1-Bit 0 噪点像素直通技术**：强行过滤所有灰度抗锯齿，配合 `dither=false` 跳过云端散点抖动算法，字迹极其黑白分明、锋利无噪点。
- ✍️ **精细宋体典雅书卷感**：项目内置精细宋体 (`fonts/simsun.ttc`)，具有复古电子纸/纸质书籍般的高颜值视觉感。
- 📐 **2-Column 双列像素级网格**：400x300 掌心屏高能布局，左侧 4px 标志竖柱，涨跌 Pill 框绝对居右右对齐。
- ⏰ **交易日定时推送调度器 (Daemon)**：内置 `trading_day_scheduler.py` 守护进程，自动在周一至周五 `09:00 - 15:00` 每小时整点及 **`14:30` (尾盘决策半小时关键点)** 自动推屏。
- 🌍 **全平台开箱即用**：零额外 C 扩展库依赖，完美支持 Windows、Linux 服务器、树莓派及 Docker 容器。
- 🤖 **AI Agent 规范兼容**：完整包含标准 `SKILL.md` 规范指南，可被 Antigravity / Cursor / Claude 等 AI Agent 一键识别与调用。

---

## 📁 目录结构

```text
zectrix-eink-market-dashboard/
├── 📄 README.md                        # 项目 GitHub 主说明文档
├── 📘 SKILL.md                         # AI Agent 技能规范与排版避坑指南
├── 📄 LICENSE                          # 开源许可证 (MIT)
├── 📁 fonts/
│   └── 🔤 simsun.ttc                  # 项目独立内置精细宋体库 (跨平台开箱即用)
└── 📁 scripts/
    ├── 🐍 zectrix_push_eink.py         # 核心行情抓取、渲染与 1-Bit 直通推送脚本
    └── ⏰ trading_day_scheduler.py     # 交易日 09:00-15:00 及 14:30 尾盘定时推送调度器
```

---

## 🚀 快速开始

### 1. 克隆仓库与安装依赖

项目仅依赖 Python 官方标准库及 Pillow 图像处理库，安装极速：

```bash
git clone https://github.com/your-username/zectrix-eink-market-dashboard.git
cd zectrix-eink-market-dashboard

pip install Pillow
```

### 2. 获取 Zectrix 设备凭证

1. 登录 [Zectrix 极趣云平台](https://cloud.zectrix.com)。
2. 进入 **开放 API** 控制台，创建一个 API Key（格式如：`zt_xxxxxxxxxxxxxxxx`）。
3. 记录你水墨屏设备的 **MAC 地址**（格式如：`20:6E:F1:B4:71:F8`）。

---

## 💻 使用方法

### 方式 A：命令行传参推屏（单次刷新）

```bash
python scripts/zectrix_push_eink.py --device "你的设备MAC地址" --key "你的API_KEY"
```

### 方式 B：配置环境变量运行（推荐）

#### Windows PowerShell:
```powershell
$env:ZECTRIX_DEVICE_MAC="20:6E:F1:B4:71:F8"
$env:ZECTRIX_API_KEY="zt_xxxxxxxxxxxxxxxx"
python scripts/zectrix_push_eink.py
```

#### Linux / macOS:
```bash
export ZECTRIX_DEVICE_MAC="20:6E:F1:B4:71:F8"
export ZECTRIX_API_KEY="zt_xxxxxxxxxxxxxxxx"
python3 scripts/zectrix_push_eink.py
```

---

## ⏰ 启动交易日定时自动推送守护进程 (Daemon)

在交易日（周一至周五），无需手动干预，启动调度器脚本即可在后台自动守护看盘：

```bash
python scripts/trading_day_scheduler.py --device "你的设备MAC地址" --key "你的API_KEY"
```

### ⏰ 推送时间表
- **整点推送**：`09:00`, `10:00`, `11:00`, `12:00`, `13:00`, `14:00`, `15:00`
- **⭐ 尾盘决策关键点**：**`14:30`** (收盘半小时前，基金申赎与股票买卖决策点)

---

## 🔧 自定义你的关注板块

如需修改你关注的板块，只需编辑 `scripts/zectrix_push_eink.py` 中的 `WATCHLIST_SECTORS` 列表即可：

```python
WATCHLIST_SECTORS = [
    ("科创芯片", "sh588200"),
    ("算力芯片", "sz159819"),
    ("人工智能", "sz399971"),
    ("PCB板",    "sz159732"),
    ("5G通信",   "sz399994"),
    ("风电设备", "sz159855"),
    ("半导体",   "sz399995"),
    ("电子板块", "sz399986")
]
```

---

## 💡 技术原理与排版避坑指南

### 1. 为什么不用硬件纯文本 API (`/display/text`)？
水墨屏硬件内置字体为 **“比例字体 (Proportional Font)”**——数字、英文字母与不同中文汉字宽度不一致，且空格极窄。在纯文本中用空格对齐在硬件上会导致右侧两列数字严重参差不齐。本项目采用 2D 画布模式，为每个文字和像素框赋予固定的 X/Y 绝对物理坐标。

### 2. 什么是 1-Bit Mode 1 直通技术？
极趣云平台在处理第三方上传的 RGB 图片时，默认会执行 **Floyd-Steinberg 散点抖动算法 (Dithering)**，将边缘抗锯齿散化成黑色噪点，导致文字发糊。
本项目在 Pillow 侧使用 `Image.new("1")` 强制渲染为 **Mode 1 纯单色 PNG** (`bits=1`)，并在 API multipart 请求中携带 `dither="false"`，使云端跳过散点处理，将 1-bit 点阵字节流 **1:1 原样像素直推** 至 ESP32S3 显存，彻底解决画质问题！

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 协议开源，欢迎自由 fork、修改与二次开发！
