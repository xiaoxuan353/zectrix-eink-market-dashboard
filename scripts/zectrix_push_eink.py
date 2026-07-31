#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zectrix 水墨屏行情看板自动化推送脚本 (通用开源脱敏版)
版本: 2.2.0 (1-Bit 像素直通 + 14大自选板块双列无噪点版)
"""

import os
import sys
import re
import json
import argparse
import urllib.request
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 从环境变量获取密钥与 MAC 地址，若未设置则使用默认占位符
DEFAULT_DEVICE_MAC = os.environ.get("ZECTRIX_DEVICE_MAC", "YOUR_DEVICE_MAC_HERE")
DEFAULT_API_KEY = os.environ.get("ZECTRIX_API_KEY", "zt_YOUR_API_KEY_HERE")
DEFAULT_PAGE_ID = os.environ.get("ZECTRIX_PAGE_ID", "1")

# 用户关注的 14 大核心板块及对应的权威证券/ETF指数代码
WATCHLIST_SECTORS = [
    ("科创芯片", "sh588200"),
    ("算力芯片", "sz159819"),
    ("人工智能", "sz399971"),
    ("PCB板",    "sz159732"),
    ("5G通信",   "sz399994"),
    ("风电设备", "sz159855"),
    ("稀有金属", "sz159608"),
    ("有色金属", "sz159871"),
    ("光伏设备", "sz399808"),
    ("新能源电池", "sz399976"),
    ("半导体",   "sz399995"),
    ("稀土永磁", "sz159830"),
    ("红利指数", "sh000015"),
    ("电子板块", "sz399986")
]

def fetch_realtime_rates():
    """从新浪财经 API 获取 14 大自选板块实时盘中涨跌幅"""
    headers = {
        "Referer": "https://finance.sina.com.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    unique_syms = list(set([s[1] for s in WATCHLIST_SECTORS]))
    url = "http://hq.sinajs.cn/list=" + ",".join(unique_syms)

    sym_rates = {}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            text = resp.read().decode("gbk", errors="ignore")
            for line in text.strip().split("\n"):
                m = re.search(r'var hq_str_(\w+)="([^"]+)";', line)
                if m:
                    sym = m.group(1)
                    parts = m.group(2).split(",")
                    if len(parts) > 5:
                        c = float(parts[3])
                        p = float(parts[2])
                        r = ((c - p) / p) * 100 if p else 0
                        sym_rates[sym] = r
    except Exception as e:
        print("Sina API fetch error:", e)

    results = []
    for name, sym in WATCHLIST_SECTORS:
        rate = sym_rates.get(sym, 0.0)
        results.append({"title": name, "code": sym, "rate": rate})

    # 按照实时涨跌幅降序排列 (从高到低)
    results.sort(key=lambda x: x["rate"], reverse=True)
    return results[:14]

def render_eink_2column_1bit(display_sectors, output_file):
    """生成 400x300 1-Bit Mode 1 调色板单色 PNG 图像，彻底防止云端抖动模糊"""
    width, height = 400, 300
    # Mode 1: 1-Bit 纯黑白 (1=White, 0=Black)
    img = Image.new("1", (width, height), 1)
    draw = ImageDraw.Draw(img)

    # 跨平台字体自动检测 (优先加载项目内 simsun.ttc 字体)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_candidates = [
        os.path.join(base_dir, "..", "fonts", "simsun.ttc"),
        "C:/Windows/Fonts/simsun.ttc",
        "/usr/share/fonts/truetype/simsun.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "C:/Windows/Fonts/msyh.ttc"
    ]

    font_path_selected = None
    for fp in font_candidates:
        if os.path.exists(fp):
            font_path_selected = fp
            break

    try:
        if font_path_selected:
            font_time = ImageFont.truetype(font_path_selected, 14)
            font_sec = ImageFont.truetype(font_path_selected, 15)
            font_rate = ImageFont.truetype(font_path_selected, 16)
        else:
            font_time = font_sec = font_rate = ImageFont.load_default()
    except Exception:
        font_time = font_sec = font_rate = ImageFont.load_default()

    # ----------------- 顶部：无标题，仅保留精确时间 -----------------
    draw.rectangle([0, 0, width, 26], fill=0)
    now = datetime.now()
    now_str = f"{now.month}月{now.day}日 {now.strftime('%H:%M:%S')}"
    draw.text((10, 4), f"行情获取时间: {now_str}", fill=1, font=font_time)

    # ----------------- 2-Column 双列像素网格 (14大板块) -----------------
    col_w = 188
    y_start = 31
    row_h = 35
    gap_y = 3

    for i, sec in enumerate(display_sectors):
        col = i % 2          # 0 = 左列, 1 = 右列
        row = i // 2         # 0 .. 6
        
        x = 8 if col == 0 else 204
        y = y_start + row * (row_h + gap_y)
        
        # 单元格细边框
        draw.rectangle([x, y, x + col_w, y + row_h], fill=1, outline=0, width=1)
        # 左侧 4px 黑色标识竖柱
        draw.rectangle([x, y, x + 5, y + row_h], fill=0)
        
        # 板块名称
        draw.text((x + 10, y + 7), sec["title"], fill=0, font=font_sec)
        
        # 涨跌幅数值框
        rate = sec["rate"]
        rate_str = f"{rate:+.2f}%"
        box_w = 78
        box_x = x + col_w - box_w - 4
        
        if rate >= 0:
            draw.rectangle([box_x, y + 4, x + col_w - 4, y + row_h - 4], fill=0)
            draw.text((box_x + 6, y + 7), rate_str, fill=1, font=font_rate)
        else:
            draw.rectangle([box_x, y + 4, x + col_w - 4, y + row_h - 4], fill=1, outline=0, width=2)
            draw.text((box_x + 6, y + 7), rate_str, fill=0, font=font_rate)

    # 保存为 Mode 1 PNG 单色调色板格式
    img.save(output_file, "PNG", bits=1)
    print(f"1-Bit Mode 1 Direct Pass PNG saved: {output_file}")

def push_to_zectrix(device_mac, api_key, image_path, page_id="1"):
    """使用 Zectrix 开放 API 推送 1-Bit 图像，必须传递 dither=false 实现 0 噪点像素直通"""
    if not device_mac or device_mac == "YOUR_DEVICE_MAC_HERE":
        print("错误: 请先配置环境变量 ZECTRIX_DEVICE_MAC 或传入 --device 参数！")
        return None
    if not api_key or api_key == "zt_YOUR_API_KEY_HERE":
        print("错误: 请先配置环境变量 ZECTRIX_API_KEY 或传入 --key 参数！")
        return None

    push_url = f"https://cloud.zectrix.com/open/v1/devices/{device_mac}/display/image"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    body = []
    body.append(f"--{boundary}".encode("utf-8"))
    body.append(b'Content-Disposition: form-data; name="pageId"')
    body.append(b"")
    body.append(str(page_id).encode("utf-8"))

    # dither=false (关闭云端 Floyd-Steinberg 抖动噪点算法)
    body.append(f"--{boundary}".encode("utf-8"))
    body.append(b'Content-Disposition: form-data; name="dither"')
    body.append(b"")
    body.append(b"false")

    body.append(f"--{boundary}".encode("utf-8"))
    body.append(b'Content-Disposition: form-data; name="images"; filename="direct_1bit_dashboard.png"')
    body.append(b"Content-Type: image/png")
    body.append(b"")
    body.append(img_bytes)

    body.append(f"--{boundary}--".encode("utf-8"))
    body.append(b"")

    payload = b"\r\n".join(body)

    headers_push = {
        "X-API-Key": api_key,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(payload))
    }

    req_push = urllib.request.Request(push_url, data=payload, headers=headers_push, method="POST")
    try:
        with urllib.request.urlopen(req_push, timeout=10) as resp:
            res_str = resp.read().decode("utf-8")
            print("Zectrix Push Result:", res_str)
            return json.loads(res_str)
    except Exception as e:
        print("Zectrix Push Error:", e)
        return None

def main():
    parser = argparse.ArgumentParser(description="Zectrix 水墨屏自选板块双列直通推送工具 (开源脱敏版)")
    parser.add_argument("--device", default=DEFAULT_DEVICE_MAC, help="设备 MAC 地址")
    parser.add_argument("--key", default=DEFAULT_API_KEY, help="极趣云 API Key")
    parser.add_argument("--page", default=DEFAULT_PAGE_ID, help="页面编号 (1-5)")
    parser.add_argument("--out", default="zectrix_eink_output.png", help="输出图片文件名")
    
    args = parser.parse_args()

    print("Fetching realtime market rates for user watchlist...")
    sectors = fetch_realtime_rates()
    for s in sectors:
        print(f"  - [{s['title']}]: {s['rate']:+.2f}%")

    print("Rendering 1-Bit 2-column image...")
    render_eink_2column_1bit(sectors, args.out)

    print("Pushing to Zectrix device with dither=false...")
    push_to_zectrix(args.device, args.key, args.out, args.page)

if __name__ == "__main__":
    main()
