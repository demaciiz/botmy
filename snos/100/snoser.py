import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from colored import cprint
import os
from pystyle import Colors, Colorate

# ========== АККАУНТЫ ОТПРАВИТЕЛЕЙ ==========
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
    'sms@telegram.org',
    'dmca@telegram.org', 
    'abuse@telegram.org',
    'sticker@telegram.org',
    'support@telegram.org',
    'security@telegram.org',
    'complaints@telegram.org'
]

# ========== СТАТИСТИКА ==========
stats = {
    'sent': 0,
    'failed': 0,
    'lock': threading.Lock()
}

# ========== БАННЕР ==========
banner = '''

███████╗███╗   ██╗ ██████╗ ███████╗███████╗██████╗ 
██╔════╝████╗  ██║██╔═══██╗██╔════╝██╔════╝██╔══██╗
███████╗██╔██╗ ██║██║   ██║███████╗█████╗  ██████╔╝
╚════██║██║╚██╗██║██║   ██║╚════██║██╔══╝  ██╔══██╗
███████║██║ ╚████║╚██████╔╝███████║███████╗██║  ██║
╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

            Creator: AttackVeter 

╔================================================╗
║                                                ║
║              [1] СНОС АККАУНТОВ                ║
║                                                ║
║              [2] СНОС СЕССИЙ                   ║
║                                                ║
║              [3] ВЫХОД                         ║
║           платный софт лучше                   ║
╚================================================╝
'''

alignment = "{:>50}".format(banner)
banner = Colorate.Horizontal(Colors.blue_to_red, alignment)
print(banner)

# ========== ФУНКЦИЯ ОТПРАВКИ ==========
def send_email(receiver, sender_email, sender_password, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if 'gmail.com' in sender_email:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
        elif 'rambler.ru' in sender_email:
            smtp_server = 'smtp.rambler.ru'
            smtp_port = 587
        elif 'mail.ru' in sender_email:
            smtp_server = 'smtp.mail.ru'
            smtp_port = 587
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
    except Exception as e:
        with stats['lock']:
            stats['failed'] += 1
        return False

# ========== ОТПРАВКА В ПОТОКАХ ==========
def send_to_all(sender_email, sender_password, subject, body, delay=2):
    for receiver in receivers:
        send_email(receiver, sender_email, sender_password, subject, body)
        time.sleep(delay)

def mass_send(subject, body, threads=5):
    all_senders = list(senders.items())
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for i, (sender_email, sender_password) in enumerate(all_senders):
            futures.append(executor.submit(send_to_all, sender_email, sender_password, subject, body, random.uniform(1, 3)))
        for f in futures:
            f.result()

# ========== СНОС АККАУНТОВ ==========
def snos_accounts():
    print("\n" + "="*50)
    print("СНОС АККАУНТОВ")
    print("="*50)
    print("1. ЗА СПАМ, РЕКЛАМУ")
    print("2. ЗА ДОКСИНГ")
    print("3. ЗА ТРОЛЛИНГ (ОСК)")
    print("4. ПРОДАЖА/РЕКЛАМА НАРКОТЫ")
    print("5. КУРАТОРСТВО В НАРКОШОПЕ")
    print("6. ПРОДАЖА ЦП")
    print("7. ВЫМОГАТЕЛЬСТВО ИНТИМНЫХ ФОТО")
    print("8. УГНЕТЕНИЕ НАЦИИ")
    print("9. УГНЕТЕНИЕ РЕЛИГИИ")
    print("10. РАСПРОСТРАНЕНИЕ РАСЧЛЕНЕНКИ")
    print("11. РАСПРОСТРАНЕНИЕ ЖИВОДЕРКИ")
    print("12. РАСПРОСТРАНЕНИЕ ПОРНУХИ")
    print("13. СУТЕНЕРСТВО")
    print("14. ПРИЗЫВ К САМОУБИЙСТВУ")
    print("15. ПРИЗЫВ К ТЕРРОРУ")
    print("16. УГРОЗЫ СВАТА")
    print("17. УГРОЗЫ РАСПРАВЫ")
    print("="*50)
    
    comp_choice = input("Выбор пункта > ")
    
    if comp_choice not in [str(i) for i in range(1, 18)]:
        print("Неверный выбор!")
        return
    
    print("\n[!] Введите данные:")
    username = input("USERNAME: ").strip()
    user_id = input("TG ID: ").strip()
    chat_link = input("Ссылка на чат: ").strip()
    violation_link = input("Ссылка на нарушение: ").strip()
    
    texts = {
        "1": f"Здравствуйте, уважаемая поддержка. На вашей платформе я нашел пользователя который отправляет много ненужных сообщений - СПАМ. Его юзернейм - {username}, его айди - {user_id}, ссылка на чат - {chat_link}, ссылка на нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю.",
        "2": f"Здравствуйте, уважаемая поддержка. На вашей платформе я нашел пользователя, который распространяет чужие данные без их согласия. Username - {username}, ID - {user_id}, ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "3": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) открыто выражается нецензурной лексикой и оскорбляет людей. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу принять меры.",
        "4": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) продает и рекламирует наркотические вещества. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "5": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) привлекает людей в наркобизнес. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "6": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) распространяет порнографию с участием несовершеннолетних. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "7": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) вымогает интимные фото у несовершеннолетних. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "8": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) разжигает межнациональные конфликты. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "9": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) оскорбляет религиозные чувства верующих. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "10": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) распространяет видеозаписи убийств и расчлененки. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "11": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) распространяет жестокое обращение с животными. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "12": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) распространяет порнографию. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "13": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) занимается сутенерством. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "14": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) призывает к суициду. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "15": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) призывает к терроризму. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "16": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) угрожает раскрытием личной информации. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
        "17": f"Здравствуйте, уважаемая поддержка. Пользователь {username} ({user_id}) угрожает физической расправой. Ссылка на чат - {chat_link}, нарушение - {violation_link}. Прошу заблокировать аккаунт.",
    }
    
    body = texts.get(comp_choice, texts["1"])
    subject = "Жалоба на аккаунт Telegram"
    
    print("\n[!] НАЧАЛО АТАКИ...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for sender_email, sender_password in list(senders.items())[:15]:
            for receiver in receivers:
                futures.append(executor.submit(send_email, receiver, sender_email, sender_password, subject, body))
                time.sleep(0.5)
        
        for f in futures:
            f.result()
    
    print(f"\n[✓] АТАКА ЗАВЕРШЕНА")
    print(f"[✓] Отправлено писем: {stats['sent']}")
    print(f"[✗] Ошибок: {stats['failed']}")

# ========== СНОС СЕССИЙ ==========
def snos_sessions():
    print("\n" + "="*50)
    print("СНОС СЕССИЙ")
    print("="*50)
    print("[!] Жалоба на утерю доступа к аккаунту")
    print("    (Telegram сбросит все активные сессии)")
    print("="*50)
    
    username = input("USERNAME: ").strip()
    user_id = input("TG ID: ").strip()
    
    body = f"""Здравствуйте, уважаемая поддержка Telegram.

Я случайно перешел по фишинговой ссылке и потерял доступ к своему аккаунту. 
Мои данные для входа были скомпрометированы.

Username: {username}
ID: {user_id}

Прошу вас сбросить все активные сессии моего аккаунта или временно заблокировать его до восстановления доступа.

Заранее спасибо за понимание."""
    
    subject = "Утеря доступа к аккаунту Telegram / сброс сессий"
    
    print("\n[!] НАЧАЛО АТАКИ...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for sender_email, sender_password in list(senders.items())[:15]:
            for receiver in receivers:
                futures.append(executor.submit(send_email, receiver, sender_email, sender_password, subject, body))
                time.sleep(0.5)
        
        for f in futures:
            f.result()
    
    print(f"\n[✓] АТАКА ЗАВЕРШЕНА")
    print(f"[✓] Отправлено писем: {stats['sent']}")
    print(f"[✗] Ошибок: {stats['failed']}")
    print("\n[!] После этой жалобы у жертвы будут сброшены все сессии")
    print("    Потребуется повторный вход во все устройства.")

# ========== MAIN ==========
def main():
    while True:
        choice = input(f'\n\033[36m[root]\033[01m Выбор пункта >\033[93m ')
        
        if choice == '1':
            snos_accounts()
            input("\nНажмите Enter для продолжения...")
            stats['sent'] = 0
            stats['failed'] = 0
            
        elif choice == '2':
            snos_sessions()
            input("\nНажмите Enter для продолжения...")
            stats['sent'] = 0
            stats['failed'] = 0
            
        elif choice == '3':
            print("\n[!] Выход...")
            break
        
        else:
            print("[!] Неверный выбор!")

if __name__ == "__main__":
    main()