#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zectrix 水墨屏 A 股交易日定时推送调度器 (Daemon)
推送策略:
  - 交易日 (周一至周五 Mon-Fri)
  - 09:00 到 15:00 每隔 1 小时整点 (09:00, 10:00, 11:00, 12:00, 13:00, 14:00, 15:00)
  - 14:30 尾盘决策关键窗口额外推送一次
"""

import os
import sys
import time
import argparse
from datetime import datetime

# 导入同目录下的推送与渲染函数
try:
    from zectrix_push_eink import (
        fetch_realtime_rates,
        render_eink_2column_1bit,
        push_to_zectrix,
        DEFAULT_DEVICE_MAC,
        DEFAULT_API_KEY,
        DEFAULT_PAGE_ID
    )
except ImportError:
    from scripts.zectrix_push_eink import (
        fetch_realtime_rates,
        render_eink_2column_1bit,
        push_to_zectrix,
        DEFAULT_DEVICE_MAC,
        DEFAULT_API_KEY,
        DEFAULT_PAGE_ID
    )

# 目标定时触发时刻表 (格式: HH:MM)
SCHEDULED_TIMES = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "14:30",  # 尾盘交易决策半小时窗口
    "15:00"
]

def run_single_push(device_mac, api_key, page_id, out_img="zectrix_eink_output.png"):
    """执行一次完整的行情抓取、精细宋体渲染与 1-Bit 直通推送"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 触发看盘行情自动推送...")
    try:
        sectors = fetch_realtime_rates()
        print(f"成功抓取 {len(sectors)} 个自选板块最新实时数据。")
        render_eink_2column_1bit(sectors, out_img)
        res = push_to_zectrix(device_mac, api_key, out_img, page_id)
        if res and res.get("code") == 0:
            print("Successfully pushed to Zectrix E-ink display!")
        else:
            print("Push warning/error response:", res)
    except Exception as e:
        print("Scheduled push exception:", e)


def is_trading_day(dt):
    """判断是否为周一至周五交易日 (0=Mon, 4=Fri)"""
    return dt.weekday() < 5

def start_scheduler(device_mac, api_key, page_id):
    """启动交易日守护进程，持续监听并准时触发推送"""
    print("=" * 60)
    print("🚀 Zectrix A 股交易日看盘定时调度器已启动")
    print(f"设备 MAC: {device_mac}")
    print(f"定时推送规则: 周一至周五 09:00-15:00 整点 + 14:30 尾盘决策点")
    print("=" * 60)

    last_triggered_minute = ""

    while True:
        now = datetime.now()
        current_hm = now.strftime("%H:%M")

        # 判断是否为周一至周五且到了设定的推送时刻
        if is_trading_day(now) and current_hm in SCHEDULED_TIMES:
            # 保证同一分钟内只触发一次
            if current_hm != last_triggered_minute:
                last_triggered_minute = current_hm
                run_single_push(device_mac, api_key, page_id)

        # 每 10 秒轮询检查一次
        time.sleep(10)

def main():
    parser = argparse.ArgumentParser(description="Zectrix 交易日看盘定时推送调度器")
    parser.add_argument("--device", default=DEFAULT_DEVICE_MAC, help="设备 MAC 地址")
    parser.add_argument("--key", default=DEFAULT_API_KEY, help="极趣云 API Key")
    parser.add_argument("--page", default=DEFAULT_PAGE_ID, help="页面编号 (1-5)")
    parser.add_argument("--once", action="store_true", help="立即运行一次测试推送并退出")

    args = parser.parse_args()

    if args.once:
        run_single_push(args.device, args.key, args.page)
    else:
        start_scheduler(args.device, args.key, args.page)

if __name__ == "__main__":
    main()
