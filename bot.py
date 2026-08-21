#!/usr/bin/env python3
# Nexavryn Shop Bot v10.5 — С БАН-СИСТЕМОЙ

import asyncio
import logging
import json
import os
import sys
import random
import time
import hashlib
from pathlib import Path
from datetime import datetime
from telethon import TelegramClient, events, Button, errors
from telethon.errors import FloodWaitError, MessageNotModifiedError
import sqlite3

# ==========================================
# ===== КОНФИГ =====
# ==========================================

BOT_TOKEN = '8994684899:AAGIa6qYXdxim02WUcMDts81F3X6IvVesiY'
API_ID = 39735233
API_HASH = 'bc4a734cbadc233a3abe4e649dc74c8c'
ADMIN_IDS = [8089966824, 8512344364]
REFERRAL_BONUS = 0.5
ANTIBOT_ATTEMPTS = 1
ANTISPAM_DELAY = 1

BASE_DIR = Path(__file__).parent.absolute()

CATEGORIES = ['snos', 'dox', 'ddos', 'manual', 'sms']

DIRS = {
    'snos': BASE_DIR / 'snos',
    'dox': BASE_DIR / 'dox',
    'ddos': BASE_DIR / 'ddos',
    'manual': BASE_DIR / 'manual',
    'sms': BASE_DIR / 'sms',
}

for d in DIRS.values():
    d.mkdir(exist_ok=True)

# ==========================================
# ===== ЛОГГЕР =====
# ==========================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# ===== ПРОДУКТЫ =====
# ==========================================

def scan_files():
    products = {}
    
    emojis = {
        'snos': '☠️',
        'dox': '🕵️',
        'ddos': '💀',
        'manual': '📖',
        'sms': '📱'
    }
    
    names = {
        'snos': 'Sn0s€r accounts',
        'dox': 'D0x',
        'ddos': 'DDoS',
        'manual': 'Мануалы по осинту',
        'sms': 'SMS Bomber'
    }
    
    allowed_prices = {
        'snos': None,
        'dox': None,
        'ddos': [200, 250],
        'manual': [200, 250],
        'sms': [300, 350]
    }
    
    for category in CATEGORIES:
        category_path = DIRS[category]
        if not category_path.exists():
            continue
        
        price_folders = []
        for folder in category_path.iterdir():
            if folder.is_dir() and folder.name.isdigit():
                price = int(folder.name)
                
                if allowed_prices[category] is not None:
                    if price not in allowed_prices[category]:
                        continue
                
                files = list(folder.glob("*"))
                if files:
                    price_folders.append({
                        'price': price,
                        'files': files,
                        'folder': folder.name
                    })
        
        if price_folders:
            price_folders.sort(key=lambda x: x['price'])
            
            products[category] = {
                'name': f"{emojis.get(category, '📦')} {names.get(category, category)}",
                'packages': [{
                    'price': p['price'],
                    'count': len(p['files']),
                    'desc': f"{len(p['files'])} файлов",
                    'files': p['files'],
                    'folder': p['folder']
                } for p in price_folders],
                'dir': category,
                'emoji': emojis.get(category, '📦')
            }
    
    return products

# ==========================================
# ===== РАБОТА С JSON =====
# ==========================================

USERS_FILE = 'data/users.json'
PURCHASES_FILE = 'data/purchases.json'
BUTTON_DATA_FILE = 'data/button_data.json'
PROMO_FILE = 'data/promos.json'
BANS_FILE = 'data/bans.json'
os.makedirs('data', exist_ok=True)

def safe_load_json(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)
        return {}
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        logger.warning(f"Файл {file} повреждён. Создаю новый.")
        if os.path.exists(file):
            os.rename(file, f"{file}.bak")
        with open(file, 'w') as f:
            json.dump({}, f)
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_button_data(key, data):
    all_data = safe_load_json(BUTTON_DATA_FILE)
    all_data[key] = data
    save_json(BUTTON_DATA_FILE, all_data)

def get_button_data(key):
    all_data = safe_load_json(BUTTON_DATA_FILE)
    return all_data.get(key)

# ==========================================
# ===== БАН-СИСТЕМА =====
# ==========================================

def load_bans():
    return safe_load_json(BANS_FILE)

def save_ban(user_id, admin_id, until_date, reason):
    bans = load_bans()
    bans[str(user_id)] = {
        'admin': str(admin_id),
        'until': until_date,
        'reason': reason,
        'banned_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_json(BANS_FILE, bans)

def remove_ban(user_id):
    bans = load_bans()
    if str(user_id) in bans:
        del bans[str(user_id)]
        save_json(BANS_FILE, bans)
        return True
    return False

def is_banned(user_id):
    bans = load_bans()
    user_id = str(user_id)
    
    if user_id not in bans:
        return None
    
    ban_data = bans[user_id]
    
    # Проверяем, не истёк ли бан
    try:
        until = datetime.strptime(ban_data['until'], '%d.%m.%Y')
        if until < datetime.now():
            # Бан истёк — удаляем
            remove_ban(user_id)
            return None
    except:
        pass
    
    return ban_data

def parse_date(date_str):
    """Парсит дату в формате ДД.ММ.ГГГГ"""
    try:
        return datetime.strptime(date_str, '%d.%m.%Y')
    except ValueError:
        return None

# ==========================================
# ===== ПРОМОКОДЫ =====
# ==========================================

def load_promos():
    return safe_load_json(PROMO_FILE)

def save_promo(promo_name, data):
    promos = load_promos()
    promos[promo_name.upper()] = data
    save_json(PROMO_FILE, promos)

def use_promo(promo_name, user_id):
    promos = load_promos()
    promo = promos.get(promo_name.upper())
    
    if not promo:
        return {'error': 'Промокод не найден'}
    
    if promo['uses'] <= 0:
        return {'error': 'Промокод уже использован'}
    
    if user_id in promo.get('used_by', []):
        return {'error': 'Вы уже использовали этот промокод'}
    
    promo['uses'] -= 1
    if 'used_by' not in promo:
        promo['used_by'] = []
    promo['used_by'].append(user_id)
    
    promos[promo_name.upper()] = promo
    save_json(PROMO_FILE, promos)
    
    return {'stars': promo['stars']}

# ==========================================
# ===== АНТИБОТ =====
# ==========================================

ANTIBOT_CACHE = {}

def generate_antibot():
    correct = random.randint(0, 999999)
    correct_str = f"{correct:06d}"
    
    options = [correct_str]
    while len(options) < 6:
        fake = f"{random.randint(0, 999999):06d}"
        if fake not in options:
            options.append(fake)
    
    random.shuffle(options)
    
    return {
        'correct': correct_str,
        'options': options
    }

def get_antibot_key(user_id):
    return hashlib.md5(f"antibot_{user_id}_{time.time()}".encode()).hexdigest()[:8]

# ==========================================
# ===== АНТИСПАМ =====
# ==========================================

def check_antispam(user_id):
    users = safe_load_json(USERS_FILE)
    if user_id not in users:
        users[user_id] = {
            'balance': 0,
            'purchases': [],
            'referrals': 0,
            'referred_by': None,
            'antibot_passed': False,
            'antibot_attempts': 0,
            'antibot_blocked_until': 0,
            'last_action': 0
        }
        save_json(USERS_FILE, users)
        return True
    
    last_action = users[user_id].get('last_action', 0)
    current_time = time.time()
    
    if current_time - last_action < ANTISPAM_DELAY:
        return False
    
    users[user_id]['last_action'] = current_time
    save_json(USERS_FILE, users)
    return True

# ==========================================
# ===== СОЗДАНИЕ БОТА =====
# ==========================================

session_file = 'soft_bot.session'
if os.path.exists(session_file):
    try:
        conn = sqlite3.connect(session_file, timeout=5)
        conn.close()
    except sqlite3.OperationalError:
        logger.warning("База данных заблокирована. Удаляем старый файл сессии.")
        os.remove(session_file)

bot = TelegramClient('soft_bot', API_ID, API_HASH)

# ==========================================
# ===== БЕЗОПАСНАЯ ОТПРАВКА =====
# ==========================================

async def safe_send(event, msg, parse_mode=None, buttons=None, file=None):
    try:
        if file:
            await bot.send_file(event.chat_id, file, caption=msg, parse_mode=parse_mode, buttons=buttons)
        else:
            await event.respond(msg, parse_mode=parse_mode, buttons=buttons)
    except FloodWaitError as e:
        logger.warning(f"FloodWait: {e.seconds} сек")
        await asyncio.sleep(e.seconds + 1)
        if file:
            await bot.send_file(event.chat_id, file, caption=msg, parse_mode=parse_mode, buttons=buttons)
        else:
            await event.respond(msg, parse_mode=parse_mode, buttons=buttons)
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")

async def safe_edit(event, msg, parse_mode=None, buttons=None):
    try:
        await event.edit(msg, parse_mode=parse_mode, buttons=buttons)
    except MessageNotModifiedError:
        pass
    except Exception as e:
        logger.error(f"Ошибка редактирования: {e}")
        await event.respond(msg, parse_mode=parse_mode, buttons=buttons)

# ==========================================
# ===== КНОПКИ =====
# ==========================================

def get_products():
    return scan_files()

def main_menu_buttons():
    products = get_products()
    buttons = []
    for key, p in products.items():
        buttons.append([Button.inline(f"{p['emoji']} {p['name']}", f"product_{key}")])
    buttons.append([Button.inline("💰 Баланс", "balance")])
    buttons.append([Button.inline("🔄 Обновить", "refresh")])
    buttons.append([Button.inline("👥 Рефералы", "referral")])
    buttons.append([Button.inline("🎁 Промокод", "promo")])
    buttons.append([Button.inline("📜 Правила", "rules")])
    return buttons

def referral_menu_buttons():
    return [
        [Button.inline("📋 Мои рефералы", "my_referrals")],
        [Button.inline("🔗 Реферальная ссылка", "referral_link")],
        [Button.inline("🔙 Назад", "back_main")]
    ]

def product_buttons(product_key):
    products = get_products()
    product = products.get(product_key)
    if not product:
        return []
    
    buttons = []
    for pkg in product['packages']:
        price = pkg['price']
        desc = pkg['desc']
        buttons.append([Button.inline(f"⭐ {price} - {desc}", f"buy_pkg_{product_key}_{price}")])
    
    buttons.append([Button.inline("🔙 Назад", "back_main")])
    return buttons

def file_select_buttons(product_key, price, files, purchase_key):
    buttons = []
    for f in files:
        key = f"sf_{int(time.time())}_{random.randint(100, 999)}"
        save_button_data(key, {
            'product_key': product_key,
            'price': price,
            'filename': f.name,
            'purchase_key': purchase_key
        })
        buttons.append([Button.inline(f"📄 {f.name}", f"select_file_{key}")])
    buttons.append([Button.inline("🔙 Отмена", f"cancel_purchase_{purchase_key}")])
    return buttons

def antibot_buttons(antibot_key, options):
    buttons = []
    for option in options:
        buttons.append([Button.inline(f"{option}", f"antibot_{antibot_key}_{option}")])
    return buttons

def admin_buttons():
    return [
        [Button.inline("📊 Статистика", "admin_stats")],
        [Button.inline("🔄 Обновить товары", "admin_update")],
        [Button.inline("📋 Список товаров", "admin_list")],
        [Button.inline("⭐ Начислить звёзды", "admin_give")],
        [Button.inline("🎁 Создать промокод", "admin_promo")],
        [Button.inline("📨 Рассылка", "admin_print")],
        [Button.inline("🚫 Баны", "admin_bans")],
        [Button.inline("📥 Логи", "admin_logs")],
        [Button.inline("🔙 Назад", "back_main")]
    ]

# ==========================================
# ===== КОМАНДЫ =====
# ==========================================

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = str(event.sender_id)
    
    # Проверяем бан
    ban_data = is_banned(user_id)
    if ban_data:
        await safe_send(event, f"""
🚫 **ВЫ ЗАБАНЕНЫ!**

📅 Забанен: {ban_data['banned_at']}
⏳ До: {ban_data['until']}
👮 Админ: {ban_data['admin']}
📝 Причина: {ban_data['reason']}

❌ Доступ к боту закрыт!
""")
        return
    
    users = safe_load_json(USERS_FILE)
    
    if not check_antispam(user_id):
        await safe_send(event, "⏳ Подождите 1 секунду между действиями!")
        return
    
    args = event.raw_text.split()
    ref_id = None
    if len(args) > 1 and args[1].startswith('ref_'):
        ref_id = args[1].replace('ref_', '')
    
    if user_id not in users:
        users[user_id] = {
            'balance': 0,
            'purchases': [],
            'referrals': 0,
            'referred_by': ref_id,
            'antibot_passed': False,
            'antibot_attempts': 0,
            'antibot_blocked_until': 0,
            'last_action': time.time()
        }
        save_json(USERS_FILE, users)
        
        if ref_id and ref_id in users and ref_id != user_id:
            users[ref_id]['balance'] += REFERRAL_BONUS
            users[ref_id]['referrals'] += 1
            save_json(USERS_FILE, users)
            
            try:
                await bot.send_message(ref_id, f"""
👥 **Новый реферал!**

Пользователь: {user_id}
🎁 Бонус: +{REFERRAL_BONUS}⭐

Всего рефералов: {users[ref_id]['referrals']}
Баланс: {users[ref_id]['balance']}⭐
""")
            except:
                pass
            
            await event.respond(f"""
🎉 **Вы пришли по реферальной ссылке!**

Пригласивший получил +{REFERRAL_BONUS}⭐

Добро пожаловать!
""")
    
    # Проверяем антибот
    if not users[user_id].get('antibot_passed', False):
        blocked_until = users[user_id].get('antibot_blocked_until', 0)
        if time.time() < blocked_until:
            remaining = int((blocked_until - time.time()) / 60) + 1
            await safe_send(event, f"""
🚫 **Вы заблокированы!**

Слишком много попыток.
Попробуйте через {remaining} минут.
""")
            return
        
        antibot_data = generate_antibot()
        antibot_key = get_antibot_key(user_id)
        ANTIBOT_CACHE[antibot_key] = antibot_data
        
        msg = f"""
🤖 **Проверка на бота**

🎯 Правильный код: `{antibot_data['correct']}`

Выберите правильное число из списка:
"""
        
        await safe_send(event, msg, parse_mode='markdown', buttons=antibot_buttons(antibot_key, antibot_data['options']))
        return
    
    # Главное меню
    msg = f"""🛡 **Nexavryn shop**

👋 Добро пожаловать!
💰 Ваш баланс: {users[user_id]['balance']}⭐
👥 Рефералов: {users[user_id].get('referrals', 0)}

💳 Пополнить баланс - @thefergod

📦 Выберите товар:"""
    
    await safe_send(event, msg, parse_mode='markdown', buttons=main_menu_buttons())

# ==========================================
# ===== ОБРАБОТЧИК АНТИБОТ =====
# ==========================================

@bot.on(events.CallbackQuery)
async def antibot_handler(event):
    data = event.data.decode('utf-8')
    if not data.startswith("antibot_"):
        return
    
    user_id = str(event.sender_id)
    
    # Проверяем бан
    ban_data = is_banned(user_id)
    if ban_data:
        await event.answer("🚫 Вы забанены!", alert=True)
        return
    
    users = safe_load_json(USERS_FILE)
    
    if not check_antispam(user_id):
        await event.answer("⏳ Подождите 1 секунду!", alert=True)
        return
    
    parts = data.split("_")
    if len(parts) < 3:
        await event.answer("❌ Ошибка", alert=True)
        return
    
    antibot_key = parts[1]
    selected = parts[2]
    
    if user_id not in users:
        users[user_id] = {
            'balance': 0,
            'purchases': [],
            'referrals': 0,
            'referred_by': None,
            'antibot_passed': False,
            'antibot_attempts': 0,
            'antibot_blocked_until': 0,
            'last_action': time.time()
        }
        save_json(USERS_FILE, users)
    
    antibot_data = ANTIBOT_CACHE.get(antibot_key)
    if not antibot_data:
        await event.answer("❌ Проверка устарела. Напишите /start заново.", alert=True)
        return
    
    correct = antibot_data['correct']
    
    if selected == correct:
        users[user_id]['antibot_passed'] = True
        users[user_id]['antibot_attempts'] = 0
        save_json(USERS_FILE, users)
        
        await event.answer("✅ Правильно!", alert=True)
        
        msg = f"""🛡 **Nexavryn shop**

👋 Добро пожаловать!
💰 Ваш баланс: {users[user_id]['balance']}⭐
👥 Рефералов: {users[user_id].get('referrals', 0)}

💳 Пополнить баланс - @thefergod

📦 Выберите товар:"""
        
        await safe_edit(event, msg, parse_mode='markdown', buttons=main_menu_buttons())
        return
    else:
        attempts = users[user_id].get('antibot_attempts', 0) + 1
        users[user_id]['antibot_attempts'] = attempts
        save_json(USERS_FILE, users)
        
        if attempts >= ANTIBOT_ATTEMPTS:
            blocked_until = time.time() + 600
            users[user_id]['antibot_blocked_until'] = blocked_until
            save_json(USERS_FILE, users)
            
            await event.answer(f"❌ Неверно! {attempts}/{ANTIBOT_ATTEMPTS} попыток. Вы заблокированы на 10 минут.", alert=True)
            
            await safe_edit(event, f"""
🚫 **Вы заблокированы!**

Попробуйте через 10 минут.
""")
            return
        
        await event.answer(f"❌ Неверно! Осталось попыток: {ANTIBOT_ATTEMPTS - attempts}", alert=True)
        
        antibot_data = generate_antibot()
        ANTIBOT_CACHE[antibot_key] = antibot_data
        
        msg = f"""
🤖 **Проверка на бота**

❌ Неверно! Осталось попыток: {ANTIBOT_ATTEMPTS - attempts}

🎯 Правильный код: `{antibot_data['correct']}`

Выберите правильное число:
"""
        
        await safe_edit(event, msg, parse_mode='markdown', buttons=antibot_buttons(antibot_key, antibot_data['options']))
        return

# ==========================================
# ===== ПРОМОКОДЫ (ОБРАБОТЧИК) =====
# ==========================================

@bot.on(events.NewMessage(pattern='/promo'))
async def promo_handler(event):
    user_id = str(event.sender_id)
    
    # Проверяем бан
    ban_data = is_banned(user_id)
    if ban_data:
        await safe_send(event, "🚫 Вы забанены!")
        return
    
    if not check_antispam(user_id):
        await safe_send(event, "⏳ Подождите 1 секунду между действиями!")
        return
    
    parts = event.raw_text.split()
    if len(parts) < 2:
        await safe_send(event, "❌ Формат: `/promo НАЗВАНИЕ_ПРОМОКОДА`")
        return
    
    promo_name = parts[1].strip()
    users = safe_load_json(USERS_FILE)
    
    if user_id not in users:
        users[user_id] = {
            'balance': 0,
            'purchases': [],
            'referrals': 0,
            'referred_by': None,
            'antibot_passed': True,
            'antibot_attempts': 0,
            'antibot_blocked_until': 0,
            'last_action': time.time()
        }
        save_json(USERS_FILE, users)
    
    result = use_promo(promo_name, user_id)
    
    if 'error' in result:
        await safe_send(event, f"❌ {result['error']}")
        return
    
    users[user_id]['balance'] += result['stars']
    save_json(USERS_FILE, users)
    
    await safe_send(event, f"""
✅ **Промокод активирован!**

🎁 Вы получили +{result['stars']}⭐
💰 Ваш баланс: {users[user_id]['balance']}⭐
""")

@bot.on(events.NewMessage(pattern='/add_promo'))
async def add_promo_handler(event):
    user_id = str(event.sender_id)
    
    if event.sender_id not in ADMIN_IDS:
        await safe_send(event, "🚫 У вас нет доступа.")
        return
    
    parts = event.raw_text.split()
    if len(parts) < 4:
        await safe_send(event, "❌ Формат: `/add_promo НАЗВАНИЕ КОЛИЧЕСТВО_ИСПОЛЬЗОВАНИЙ КОЛИЧЕСТВО_ЗВЁЗД`")
        await safe_send(event, "📌 Пример: `/add_promo TEST 10 50`")
        return
    
    promo_name = parts[1].strip()
    try:
        uses = int(parts[2].strip())
        stars = int(parts[3].strip())
        if uses < 1 or stars < 1:
            raise ValueError
    except ValueError:
        await safe_send(event, "❌ Количество использований и звёзд должны быть положительными числами")
        return
    
    save_promo(promo_name, {
        'uses': uses,
        'stars': stars,
        'used_by': []
    })
    
    await safe_send(event, f"""
✅ **Промокод создан!**

🎫 Название: `{promo_name.upper()}`
📊 Доступно использований: {uses}
⭐ Звёзд за активацию: {stars}
""")

# ==========================================
# ===== БАН-КОМАНДЫ =====
# ==========================================

@bot.on(events.NewMessage(pattern='/ban'))
async def ban_handler(event):
    if event.sender_id not in ADMIN_IDS:
        await safe_send(event, "🚫 У вас нет доступа.")
        return
    
    parts = event.raw_text.split(maxsplit=3)
    if len(parts) < 4:
        await safe_send(event, """❌ **Формат:** `/ban ID_ИЛИ_USERNAME ДАТА ПРИЧИНА`

📌 **Примеры:**
`/ban 123456789 21.08.2026 Спам`
`/ban @username 25.12.2026 Нарушение правил`

📅 **Формат даты:** ДД.ММ.ГГГГ
""")
        return
    
    target = parts[1].strip()
    date_str = parts[2].strip()
    reason = parts[3].strip()
    
    # Парсим дату
    ban_date = parse_date(date_str)
    if not ban_date:
        await safe_send(event, f"❌ Неверный формат даты: `{date_str}`\nИспользуйте: `ДД.ММ.ГГГГ`")
        return
    
    # Определяем ID пользователя
    target_user_id = None
    username = None
    
    if target.startswith('@'):
        username = target
        try:
            entity = await bot.get_entity(target)
            target_user_id = str(entity.id)
        except Exception as e:
            await safe_send(event, f"❌ Пользователь {target} не найден: {e}")
            return
    else:
        target_user_id = target
        try:
            entity = await bot.get_entity(int(target))
            if hasattr(entity, 'username') and entity.username:
                username = f"@{entity.username}"
        except:
            pass
    
    # Проверяем, не пытается ли админ забанить себя
    if target_user_id == str(event.sender_id):
        await safe_send(event, "❌ Вы не можете забанить самого себя!")
        return
    
    # Проверяем, не админ ли это
    if target_user_id and int(target_user_id) in ADMIN_IDS:
        await safe_send(event, "❌ Вы не можете забанить другого админа!")
        return
    
    # Сохраняем бан
    save_ban(target_user_id, str(event.sender_id), date_str, reason)
    
    admin_name = f"@{event.sender.username}" if hasattr(event.sender, 'username') and event.sender.username else str(event.sender_id)
    
    await safe_send(event, f"""
✅ **Пользователь забанен!**

👤 Пользователь: {username or target_user_id}
📅 До: {date_str}
👮 Админ: {admin_name}
📝 Причина: {reason}

📌 Для разбана используйте `/unban {target_user_id}`
""")
    
    # Пробуем уведомить пользователя о бане
    if target_user_id:
        try:
            await bot.send_message(
                int(target_user_id),
                f"""
🚫 **ВЫ БЫЛИ ЗАБАНЕНЫ В БОТЕ!**

👮 Админ: {admin_name}
📅 Бан до: {date_str}
📝 Причина: {reason}

❌ Доступ к боту закрыт до указанной даты!
"""
            )
        except:
            pass

@bot.on(events.NewMessage(pattern='/unban'))
async def unban_handler(event):
    if event.sender_id not in ADMIN_IDS:
        await safe_send(event, "🚫 У вас нет доступа.")
        return
    
    parts = event.raw_text.split()
    if len(parts) < 2:
        await safe_send(event, "❌ Формат: `/unban ID_ИЛИ_USERNAME`")
        await safe_send(event, "📌 Пример: `/unban 123456789` или `/unban @username`")
        return
    
    target = parts[1].strip()
    
    # Определяем ID пользователя
    target_user_id = None
    username = None
    
    if target.startswith('@'):
        username = target
        try:
            entity = await bot.get_entity(target)
            target_user_id = str(entity.id)
        except Exception as e:
            await safe_send(event, f"❌ Пользователь {target} не найден: {e}")
            return
    else:
        target_user_id = target
        try:
            entity = await bot.get_entity(int(target))
            if hasattr(entity, 'username') and entity.username:
                username = f"@{entity.username}"
        except:
            pass
    
    if remove_ban(target_user_id):
        await safe_send(event, f"""
✅ **Пользователь разбанен!**

👤 Пользователь: {username or target_user_id}
📌 Теперь у него есть доступ к боту.
""")
        
        # Пробуем уведомить пользователя
        if target_user_id:
            try:
                await bot.send_message(
                    int(target_user_id),
                    f"""
✅ **ВАС РАЗБАНИЛИ В БОТЕ!**

Теперь у вас снова есть доступ.
Напишите /start для входа.
"""
                )
            except:
                pass
    else:
        await safe_send(event, f"❌ Пользователь {target} не найден в списке забаненных.")

@bot.on(events.NewMessage(pattern='/bans'))
async def bans_list_handler(event):
    if event.sender_id not in ADMIN_IDS:
        await safe_send(event, "🚫 У вас нет доступа.")
        return
    
    bans = load_bans()
    
    if not bans:
        await safe_send(event, "📋 **Список забаненных пуст.**")
        return
    
    msg = "🚫 **Список забаненных пользователей:**\n\n"
    
    for user_id, data in bans.items():
        msg += f"👤 ID: `{user_id}`\n"
        msg += f"📅 До: {data['until']}\n"
        msg += f"📝 Причина: {data['reason']}\n"
        msg += f"👮 Админ: {data['admin']}\n"
        msg += f"📅 Забанен: {data['banned_at']}\n"
        msg += "─" * 20 + "\n"
    
    await safe_send(event, msg)

# ==========================================
# ===== РАССЫЛКА =====
# ==========================================

@bot.on(events.NewMessage(pattern='/print'))
async def print_handler(event):
    if event.sender_id not in ADMIN_IDS:
        await safe_send(event, "🚫 У вас нет доступа.")
        return
    
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) < 2:
        await safe_send(event, "❌ Формат: `/print ТЕКСТ_СООБЩЕНИЯ`")
        await safe_send(event, "📌 Пример: `/print Всем привет! У нас новый товар!`")
        return
    
    message_text = parts[1].strip()
    users = safe_load_json(USERS_FILE)
    
    if not users:
        await safe_send(event, "❌ Нет пользователей для рассылки.")
        return
    
    await safe_send(event, f"📨 Начинаю рассылку {len(users)} пользователям...")
    
    success_count = 0
    fail_count = 0
    
    for user_id in users.keys():
        # Пропускаем забаненных
        if is_banned(user_id):
            fail_count += 1
            continue
            
        try:
            await bot.send_message(
                int(user_id),
                f"📢 **ОБЪЯВЛЕНИЕ ОТ АДМИНА**\n\n{message_text}",
                parse_mode='markdown'
            )
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            fail_count += 1
            logger.warning(f"Не удалось отправить пользователю {user_id}: {e}")
    
    await safe_send(event, f"""
✅ **Рассылка завершена!**

📨 Отправлено: {success_count}
❌ Не отправлено (бан/ошибка): {fail_count}
👥 Всего пользователей: {len(users)}
""")

# ==========================================
# ===== АДМИН КОМАНДЫ =====
# ==========================================

@bot.on(events.NewMessage(pattern='/admq'))
async def admin_panel_handler(event):
    user_id = str(event.sender_id)
    if not check_antispam(user_id):
        await safe_send(event, "⏳ Подождите 1 секунду между действиями!")
        return
    
    if event.sender_id not in ADMIN_IDS:
        await safe_send(event, "🚫 У вас нет доступа к админ-панели.")
        return
    
    await safe_send(event,
        "👑 **АДМИН-ПАНЕЛЬ**\n\nВыберите действие:",
        parse_mode='markdown',
        buttons=admin_buttons()
    )

@bot.on(events.NewMessage(pattern='/give'))
async def give_stars_handler(event):
    user_id = str(event.sender_id)
    if not check_antispam(user_id):
        await safe_send(event, "⏳ Подождите 1 секунду между действиями!")
        return
    
    if event.sender_id not in ADMIN_IDS:
        await safe_send(event, "🚫 У вас нет доступа.")
        return
    
    parts = event.raw_text.split()
    if len(parts) < 3:
        await safe_send(event, "❌ Формат: `/give user_id количество`")
        return
    
    target_user = parts[1].strip()
    try:
        amount = int(parts[2].strip())
        if amount < 1:
            raise ValueError
    except ValueError:
        await safe_send(event, "❌ Количество должно быть положительным числом")
        return
    
    users = safe_load_json(USERS_FILE)
    if target_user not in users:
        users[target_user] = {'balance': 0, 'purchases': [], 'referrals': 0, 'referred_by': None, 'antibot_passed': True, 'antibot_attempts': 0, 'antibot_blocked_until': 0, 'last_action': time.time()}
    
    users[target_user]['balance'] += amount
    save_json(USERS_FILE, users)
    await safe_send(event, f"✅ Пользователю `{target_user}` начислено {amount}⭐")

@bot.on(events.NewMessage(pattern='/update'))
async def update_handler(event):
    user_id = str(event.sender_id)
    if not check_antispam(user_id):
        await safe_send(event, "⏳ Подождите 1 секунду между действиями!")
        return
    
    if event.sender_id not in ADMIN_IDS:
        await safe_send(event, "🚫 У вас нет доступа.")
        return
    
    products = get_products()
    await safe_send(event, f"✅ Товары обновлены! Найдено: {len(products)} категорий")

# ==========================================
# ===== ОБРАБОТЧИКИ КНОПОК =====
# ==========================================

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode('utf-8')
    
    if data.startswith("antibot_"):
        return
    
    user_id = str(event.sender_id)
    
    # Проверяем бан
    ban_data = is_banned(user_id)
    if ban_data:
        await event.answer("🚫 Вы забанены!", alert=True)
        return
    
    users = safe_load_json(USERS_FILE)
    
    if not check_antispam(user_id):
        await event.answer("⏳ Подождите 1 секунду между действиями!", alert=True)
        return
    
    if user_id not in users:
        users[user_id] = {
            'balance': 0,
            'purchases': [],
            'referrals': 0,
            'referred_by': None,
            'antibot_passed': False,
            'antibot_attempts': 0,
            'antibot_blocked_until': 0,
            'last_action': time.time()
        }
        save_json(USERS_FILE, users)
    
    if not users[user_id].get('antibot_passed', False):
        await event.answer("❌ Сначала пройдите проверку на бота!", alert=True)
        return
    
    # ===== ПРАВИЛА =====
    if data == "rules":
        rules_text = """
📜 **ПРАВИЛА И ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ**

⚠️ **ВНИМАНИЕ!**

1. ВСЕ МАТЕРИАЛЫ ПРЕДОСТАВЛЯЮТСЯ «КАК ЕСТЬ» (AS-IS)
2. АДМИНИСТРАЦИЯ НЕ НЕСЁТ ОТВЕТСТВЕННОСТИ ЗА:
   - Любые последствия использования
   - Блокировку аккаунтов
   - Потерю данных
   - Действия третьих лиц
   - Несовместимость с вашим ПО
   - Юридические последствия в вашей стране

3. ПОЛЬЗОВАТЕЛЬ ОБЯЗУЕТСЯ:
   - Использовать материалы в образовательных целях
   - Не нарушать законы своей страны
   - Самостоятельно нести ответственность

4. МЫ НЕ ГАРАНТИРУЕМ:
   - Работоспособность на всех версиях
   - Отсутствие ошибок
   - Безопасность от обнаружения

5. ВСЕ ПРАВА ПРИНАДЛЕЖАТ ИХ ВЛАДЕЛЬЦАМ

6. ПРИ ИСПОЛЬЗОВАНИИ ВЫ ПРИНИМАЕТЕ ЭТИ УСЛОВИЯ

📌 Для связи: @thefergod
"""
        await safe_edit(event, rules_text, parse_mode='markdown', buttons=[[Button.inline("🔙 Назад", "back_main")]])
        await event.answer()
        return
    
    # ===== ГЛАВНОЕ МЕНЮ =====
    if data == "back_main":
        await safe_edit(event,
            f"🛡 **Nexavryn shop**\n\n"
            f"💰 Ваш баланс: {users[user_id]['balance']}⭐\n"
            f"👥 Рефералов: {users[user_id].get('referrals', 0)}\n\n"
            f"💳 Пополнить баланс - @thefergod\n\n"
            f"📦 Выберите товар:",
            parse_mode='markdown',
            buttons=main_menu_buttons()
        )
        await event.answer()
        return
    
    if data == "refresh":
        await safe_edit(event,
            f"🛡 **Nexavryn shop**\n\n"
            f"🔄 Товары обновлены!\n"
            f"💰 Ваш баланс: {users[user_id]['balance']}⭐\n"
            f"👥 Рефералов: {users[user_id].get('referrals', 0)}\n\n"
            f"💳 Пополнить баланс - @thefergod\n\n"
            f"📦 Выберите товар:",
            parse_mode='markdown',
            buttons=main_menu_buttons()
        )
        await event.answer("🔄 Обновлено!")
        return
    
    if data == "balance":
        await event.answer(f"💰 Баланс: {users[user_id]['balance']}⭐", alert=True)
        return
    
    # ===== ПРОМОКОД (КНОПКА) =====
    if data == "promo":
        await safe_edit(event,
            "🎁 **Активация промокода**\n\n"
            "Отправьте команду:\n"
            "`/promo НАЗВАНИЕ_ПРОМОКОДА`\n\n"
            "📌 Пример: `/promo TEST`",
            parse_mode='markdown',
            buttons=[[Button.inline("🔙 Назад", "back_main")]]
        )
        await event.answer()
        return
    
    # ===== РЕФЕРАЛЫ =====
    if data == "referral":
        try:
            me = await bot.get_me()
            username = me.username if me.username else BOT_TOKEN.split(':')[0]
            ref_link = f"https://t.me/{username}?start=ref_{user_id}"
        except:
            ref_link = f"https://t.me/nexavryn_shop_bot?start=ref_{user_id}"
        
        await safe_edit(event,
            "👥 **Реферальная система**\n\n"
            f"💰 За каждого приглашённого вы получаете +{REFERRAL_BONUS}⭐\n"
            f"👥 Ваших рефералов: {users[user_id].get('referrals', 0)}\n\n"
            f"📋 Ваша ссылка:\n"
            f"`{ref_link}`",
            parse_mode='markdown',
            buttons=referral_menu_buttons()
        )
        await event.answer()
        return
    
    if data == "my_referrals":
        referrals = users[user_id].get('referrals', 0)
        await event.answer(f"👥 Ваших рефералов: {referrals}", alert=True)
        return
    
    if data == "referral_link":
        try:
            me = await bot.get_me()
            username = me.username if me.username else BOT_TOKEN.split(':')[0]
            ref_link = f"https://t.me/{username}?start=ref_{user_id}"
        except:
            ref_link = f"https://t.me/nexavryn_shop_bot?start=ref_{user_id}"
        await event.answer(f"📋 Ваша ссылка: {ref_link}", alert=True)
        return
    
    # ===== НАЗАД К ТОВАРУ =====
    if data.startswith("back_to_"):
        product_key = data.replace("back_to_", "")
        products = get_products()
        product = products.get(product_key)
        if not product:
            await safe_edit(event, "❌ Товар не найден", buttons=main_menu_buttons())
            return
        
        msg = f"""
{product['name']}

💳 **Выберите цену:**"""
        
        await safe_edit(event, msg, parse_mode='markdown', buttons=product_buttons(product_key))
        await event.answer()
        return
    
    # ===== АДМИН =====
    if data == "admin":
        if event.sender_id not in ADMIN_IDS:
            await event.answer("🚫 У вас нет доступа!", alert=True)
            return
        await safe_edit(event,
            "👑 **АДМИН-ПАНЕЛЬ**\n\nВыберите действие:",
            parse_mode='markdown',
            buttons=admin_buttons()
        )
        await event.answer()
        return
    
    if data == "admin_stats":
        if event.sender_id not in ADMIN_IDS:
            await event.answer("🚫 У вас нет доступа!", alert=True)
            return
        purchases = safe_load_json(PURCHASES_FILE)
        total_users = len(users)
        total_balance = sum(u.get('balance', 0) for u in users.values())
        total_purchases = sum(len(p) for p in purchases.values() if isinstance(p, list))
        products = get_products()
        promos = load_promos()
        bans = load_bans()
        
        files_count = {}
        for name, d in DIRS.items():
            files_count[name] = len(list(d.glob("*")))
        
        total_referrals = sum(u.get('referrals', 0) for u in users.values())
        
        msg = f"""
📊 **Статистика:**
├─ Пользователей: {total_users}
├─ Общий баланс: {total_balance}⭐
├─ Всего покупок: {total_purchases}
├─ Всего рефералов: {total_referrals}
├─ Товаров: {len(products)}
├─ Промокодов: {len(promos)}
├─ Забаненных: {len(bans)}
├─ Файлов:
│  ├─ snos: {files_count.get('snos', 0)}
│  ├─ dox: {files_count.get('dox', 0)}
│  ├─ ddos: {files_count.get('ddos', 0)}
│  ├─ manual: {files_count.get('manual', 0)}
│  └─ sms: {files_count.get('sms', 0)}
"""
        await safe_edit(event, msg, parse_mode='markdown', buttons=admin_buttons())
        await event.answer()
        return
    
    if data == "admin_update":
        if event.sender_id not in ADMIN_IDS:
            await event.answer("🚫 У вас нет доступа!", alert=True)
            return
        await safe_edit(event, "✅ Товары обновлены!", buttons=admin_buttons())
        await event.answer("✅ Обновлено!")
        return
    
    if data == "admin_list":
        if event.sender_id not in ADMIN_IDS:
            await event.answer("🚫 У вас нет доступа!", alert=True)
            return
        products = get_products()
        if not products:
            await safe_edit(event, "📋 Список товаров пуст.", buttons=admin_buttons())
            return
        msg = "📋 **Список товаров:**\n\n"
        for key, p in products.items():
            packages = len(p['packages'])
            msg += f"`{key}` — {p['name']} — {packages} цен\n"
        await safe_edit(event, msg, parse_mode='markdown', buttons=admin_buttons())
        await event.answer()
        return
    
    if data == "admin_promo":
        if event.sender_id not in ADMIN_IDS:
            await event.answer("🚫 У вас нет доступа!", alert=True)
            return
        await safe_edit(event,
            "🎁 **Создание промокода**\n\n"
            "Отправьте команду:\n"
            "`/add_promo НАЗВАНИЕ КОЛИЧЕСТВО_ИСПОЛЬЗОВАНИЙ КОЛИЧЕСТВО_ЗВЁЗД`\n\n"
            "📌 Пример: `/add_promo TEST 10 50`",
            parse_mode='markdown',
            buttons=admin_buttons()
        )
        await event.answer()
        return
    
    if data == "admin_print":
        if event.sender_id not in ADMIN_IDS:
            await event.answer("🚫 У вас нет доступа!", alert=True)
            return
        await safe_edit(event,
            "📨 **Рассылка**\n\n"
            "Отправьте команду:\n"
            "`/print ТЕКСТ_СООБЩЕНИЯ`\n\n"
            "📌 Пример: `/print Всем привет! Новый товар!`",
            parse_mode='markdown',
            buttons=admin_buttons()
        )
        await event.answer()
        return
    
    if data == "admin_bans":
        if event.sender_id not in ADMIN_IDS:
            await event.answer("🚫 У вас нет доступа!", alert=True)
            return
        await safe_edit(event,
            "🚫 **Управление банами**\n\n"
            "**Команды:**\n"
            "`/ban ID_ИЛИ_USERNAME ДАТА ПРИЧИНА` — забанить\n"
            "`/unban ID_ИЛИ_USERNAME` — разбанить\n"
            "`/bans` — список забаненных\n\n"
            "📌 **Примеры:**\n"
            "`/ban 123456789 21.08.2026 Спам`\n"
            "`/ban @username 25.12.2026 Нарушение`\n"
            "`/unban 123456789`",
            parse_mode='markdown',
            buttons=admin_buttons()
        )
        await event.answer()
        return
    
    if data == "admin_logs":
        if event.sender_id not in ADMIN_IDS:
            await event.answer("🚫 У вас нет доступа!", alert=True)
            return
        log_file = 'data/logs.txt'
        with open(log_file, 'w') as f:
            f.write("=== Логи бота ===\n")
            products = get_products()
            f.write(f"Товаров: {len(products)}\n")
            f.write(f"Папки:\n")
            for name, d in DIRS.items():
                files = list(d.glob("*"))
                f.write(f"  {name}: {len(files)} файлов\n")
            purchases = safe_load_json(PURCHASES_FILE)
            for uid, items in purchases.items():
                f.write(f"{uid}: {len(items)} покупок\n")
            bans = load_bans()
            f.write(f"\n=== Забаненные ===\n")
            for uid, data in bans.items():
                f.write(f"{uid}: {data['reason']} (до {data['until']})\n")
        
        await bot.send_file(event.chat_id, log_file, caption="📥 Логи")
        await event.answer("📥 Логи отправлены!")
        return
    
    if data == "admin_give":
        if event.sender_id not in ADMIN_IDS:
            await event.answer("🚫 У вас нет доступа!", alert=True)
            return
        await event.answer("ℹ️ Используйте команду: /give user_id количество", alert=True)
        return
    
    # ===== ТОВАРЫ =====
    if data.startswith("product_"):
        product_key = data.replace("product_", "")
        products = get_products()
        product = products.get(product_key)
        if not product:
            await event.answer("❌ Товар не найден", alert=True)
            return
        
        msg = f"""
{product['name']}

💳 **Выберите цену:**"""
        
        await safe_edit(event, msg, parse_mode='markdown', buttons=product_buttons(product_key))
        await event.answer()
        return
    
    # ===== ПОКУПКА =====
    if data.startswith("buy_pkg_"):
        parts = data.split("_")
        if len(parts) < 4:
            await event.answer("❌ Ошибка", alert=True)
            return
        
        product_key = parts[2]
        price = int(parts[3])
        products = get_products()
        product = products.get(product_key)
        
        if not product:
            await event.answer("❌ Товар не найден", alert=True)
            return
        
        selected_pkg = None
        for pkg in product['packages']:
            if pkg['price'] == price:
                selected_pkg = pkg
                break
        
        if not selected_pkg:
            await event.answer("❌ Цена не найдена", alert=True)
            return
        
        if users[user_id].get('balance', 0) < price:
            await event.answer(f"❌ Недостаточно звёзд! Нужно: {price}⭐", alert=True)
            return
        
        users[user_id]['balance'] -= price
        save_json(USERS_FILE, users)
        
        purchase_key = f"pkg_{int(time.time())}_{random.randint(1000, 9999)}"
        save_button_data(purchase_key, {
            'product_key': product_key,
            'price': price,
            'files': [f.name for f in selected_pkg['files']]
        })
        
        msg = f"""
✅ Оплачено! {price}⭐ списано.

📦 {product['name']}
📁 Выберите ОДИН файл:
"""
        
        await safe_edit(event, msg, parse_mode='markdown', buttons=file_select_buttons(product_key, price, selected_pkg['files'], purchase_key))
        await event.answer(f"✅ {price}⭐ списано! Выберите файл.")
        return
    
    # ===== ВЫБОР ФАЙЛА =====
    if data.startswith("select_file_"):
        key = data.replace("select_file_", "")
        file_data = get_button_data(key)
        
        if not file_data:
            await event.answer("❌ Данные устарели. Попробуйте снова.", alert=True)
            return
        
        product_key = file_data['product_key']
        price = file_data['price']
        filename = file_data['filename']
        purchase_key = file_data['purchase_key']
        
        products = get_products()
        product = products.get(product_key)
        
        if not product:
            await event.answer("❌ Товар не найден", alert=True)
            return
        
        file_path = None
        for pkg in product['packages']:
            if pkg['price'] == price:
                for f in pkg['files']:
                    if f.name == filename:
                        file_path = f
                        break
                break
        
        if not file_path or not file_path.exists():
            await event.answer("❌ Файл не найден", alert=True)
            return
        
        purchases = safe_load_json(PURCHASES_FILE)
        if user_id not in purchases:
            purchases[user_id] = []
        purchases[user_id].append(f"{product_key}:{price}:{filename}")
        save_json(PURCHASES_FILE, purchases)
        
        try:
            await bot.send_file(
                event.chat_id,
                str(file_path),
                caption=f"📁 {filename}\n\n📦 {product['name']}"
            )
            
            msg = f"""🛡 **Nexavryn shop**

✅ Файл отправлен!
💰 Ваш баланс: {users[user_id]['balance']}⭐
👥 Рефералов: {users[user_id].get('referrals', 0)}

💳 Пополнить баланс - @thefergod

📦 Выберите товар:"""
            
            await safe_edit(event, msg, parse_mode='markdown', buttons=main_menu_buttons())
            await event.answer("✅ Файл отправлен!")
            
        except Exception as e:
            logger.error(f"Ошибка отправки файла: {e}")
            await event.answer("❌ Ошибка отправки файла", alert=True)
        return
    
    # ===== ОТМЕНА =====
    if data.startswith("cancel_purchase_"):
        purchase_key = data.replace("cancel_purchase_", "")
        
        msg = f"""🛡 **Nexavryn shop**

❌ Выбор отменён.
💰 Ваш баланс: {users[user_id]['balance']}⭐

📦 Выберите товар:"""
        
        await safe_edit(event, msg, parse_mode='markdown', buttons=main_menu_buttons())
        await event.answer("❌ Выбор отменён. Деньги не возвращаются.", alert=True)
        return

# ==========================================
# ===== ЗАПУСК =====
# ==========================================

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    products = get_products()
    
    logger.info("✅ Nexavryn Shop Bot v10.5 запущен!")
    logger.info(f"📁 Папки: {', '.join(DIRS.keys())}")
    logger.info(f"📦 Товаров: {len(products)}")
    logger.info(f"👑 Админы: {ADMIN_IDS}")
    logger.info(f"🎁 Реферальный бонус: +{REFERRAL_BONUS}⭐")
    logger.info(f"⏳ Антиспам: {ANTISPAM_DELAY} сек")
    
    try:
        await bot.run_until_disconnected()
    except asyncio.CancelledError:
        logger.info("⏹️ Бот остановлен")
    finally:
        await bot.disconnect()

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        try:
            loop.close()
        except:
            pass