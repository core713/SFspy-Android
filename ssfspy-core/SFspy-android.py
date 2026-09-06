#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Утилита SFspy-Android [The Absolute Gold Standard for Android Spyware Audit]



import os
import sys
import re
import time
import subprocess
import signal
import select
import random

class Colors:
    RESET = '\033[0m'    

    RED = '\033[31m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'

print(f"{Colors.BLUE}[+]{Colors.RESET} [INFO] The word Android is a trademark of Google LLC, we are not the copyright holder, but only write a utility for the Android OS.")

FUN_FACTS = [
    "ОС Core/713 была создана из-за ненависти к Windows обновления?",
    "автор ОС Core/713 не может выучить таблицу умножения/деление столбиком?",
    "организация Core/713 была создана для лучшей регулировки работы?",
    "ОС Android была названа в честь книги Филипа Дика «Мечтают ли андроиды об электроовцах?» а точнее роботов андройдов там?",
    "каждая версия Android до 10.0 называлась в честь десерта: Cupcake, Donut, Eclair, Froyo, Gingerbread, Honeycomb, Ice Cream Sandwich, Jelly Bean, KitKat, Lollipop, Marshmallow, Nougat, Oreo, Pie?",
    "Android - это Linux, ведь он построен на ядре линукс просто сильно модифицированный компанией Google LLC?",
    "APK расшифровывается как Android Package и является ZIP файлом?",
    "ядро Android является полностью открытым и свободным и распространяется под лицензией AOSP ( Android Open Source Project )?",
    "Core/713 была названа в честь аккаунта автора OS-AC713 в роблоксе systems713 + Core/?",
    "автор os-core713 любит троллить ( особенно корпорации )?"
]

# --- КОНФИГУРАЦИЯ ---
PACKAGE = "your_PACKAGE"
OUTPUT_FILE = "" # your file name
MAX_SIZE_MB = # insert your maximum
TIMEOUT_SECONDS =  # insert you hours/days/minutes IN SECONDS 
SIZE_CHECK_INTERVAL =     # Insert the interval at which the file will be updated.
fun_fact_index = 0
last_fact_time = time.time()
FACT_INTERVAL = 30  # Каждые 30 секунд

# --------------------


# Examples (uncomment what you need / enter your own)
# FAST TEST, 5 minutes, 10 MB

#MAX_SIZE_MB = 10
#TIMEOUT_SECONDS = 300
#SIZE_CHECK_INTERVAL = 5  

# FULL AUDIT, 24H, 2GB 

#MAX_SIZE_MB = 2000
#TIMEOUT_SECONDS = 864000
#SIZE_CHECK_INTERVAL = 30

# Medium Test, 3H, 500MB

#MAX_SIZE_MB = 500
#TIMEOUT_SECONDS = 10800
#SIZE_CHECK_INTERVAL = 20


# Данные пользователя для маскировки (заполните по желанию)
MY_USER = "your_user"
MY_HOST = "your_host"

MY_SSIDS = [
    "your_ssid",
    "your_ssid2" # you can remove this SSID 
]

# Расширенный фильтр для поиска скрытой шпионской активности
FILTER_PATTERN = re.compile(
    rf"({PACKAGE}|Location|GPS|ActivityManager|Connectivity|Telephony|ContentProvider|"
    rf"PackageManager|ACCESS_FINE_LOCATION|ACCESS_COARSE_LOCATION|READ_CONTACTS|"
    rf"READ_SMS|RECORD_AUDIO|CAMERA|INTERNET|OpenTelemetry|Watchdog|JobScheduler)", 
    re.IGNORECASE
)

# --- РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ (Тотальная маскировка без ложных срабатываний) ---
RE_IP4 = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
RE_IP6 = re.compile(r'\b(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|([0-9a-fA-F]{1,4}:){1,4}:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b')

# Исправлено: MAC-адреса с любыми разделителями (двоеточия, дефисы, точки) ИЛИ 12 hex-символов отдельно от длинных хэшей
RE_MAC = re.compile(r'(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}[:.-]){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])|(?<![0-9A-Fa-f])[0-9A-Fa-f]{12}(?![0-9A-Fa-f])')

RE_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

# Исправлено: ловит телефоны с любыми разделителями, пробелами и скобками
RE_PHONE = re.compile(r'\b(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b')

# Исправлено: Расширено для JSON структур типа "latitude": "55.12345" или 'lat' : 37.12
RE_GEO = re.compile(r'(?i)(lat|lng|latitude|longitude|coord|geo|loc)["\']?\s*[:=]\s*["\']?(-?\d{1,3}\.\d{4,8})\b')

RE_TOKENS = re.compile(r'(?i)(token|auth|session|jwt|bearer|key|secret)[^\w\n]{1,5}([A-Za-z0-9-_=]{32,})')
RE_SYS_IDS = re.compile(r'(?i)(android_id|imei|meid|serial|sn|hardware_id|device_id)[^\w\n]{1,5}([a-zA-Z0-9-]{8,20})')

# Исправлено: Сужено до реальных MCC кодов (РФ, СНГ, США, Европа), чтобы не затирать ID транзакций
RE_IMSI = re.compile(r'\b(250|255|401|434|436|437|438|400|204|234|235|262|208|310|311|312|313|314|315|316)\d{12}\b')
RE_ICCID = re.compile(r'\b89\d{17,18}\b')
RE_UUID = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')

RE_CARD_CANDIDATE = re.compile(r'\b(?:\d[ -]*?){13,19}\b')
RE_B64_CANDIDATE = re.compile(r'\b[A-Za-z0-9+/=]{40,}\b')

adb_process = None
is_exiting = False

def is_luhn_valid(card_number):
    digits = [int(c) for c in card_number if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19: return False
    checksum = 0
    for i, digit in enumerate(digits[::-1]):
        if i % 2 == 1:
            digit *= 2
            if digit > 9: digit -= 9
        checksum += digit
    return checksum % 10 == 0

def mask_cards(match):
    raw_str = match.group(0)
    if is_luhn_valid("".join(c for c in raw_str if c.isdigit())):
        return "[REDACTED_CARD]"
    return raw_str

def mask_base64(match):
    """Исправлено на 100% с эвристикой энтропии против ложных срабатываний на путях и словах"""
    raw_str = match.group(0)
    
    # Эвристика: Base64 — это хаос из заглавных, строчных букв и цифр. Обычные слова однородны.
    has_upper = bool(re.search(r'[A-Z]', raw_str))
    has_lower = bool(re.search(r'[a-z]', raw_str))
    has_digit = bool(re.search(r'[0-9]', raw_str))
    
    # Строка должна содержать хотя бы 2 типа символов из 3, иначе это просто длинное слово/путь
    if sum([has_upper, has_lower, has_digit]) < 2:
        return raw_str

    if re.search(r'[A-Za-z0-9+/=]{40,}', raw_str):
        if '?' in raw_str or '&' in raw_str:
            # Вырезаем только скрытый токен, сохраняя структуру URL-адреса для пруфов в статье
            return re.sub(r'[A-Za-z0-9+/=]{40,}', '[REDACTED_BASE64]', raw_str)
        return "[REDACTED_BASE64]"
    return raw_str

def clean_line(line):
    # Маскируем пользователя и хост
    line = line.replace(f"/home/{MY_USER}", "/home/[REDACTED]")
    line = line.replace(f"{MY_USER}@{MY_HOST}", "[REDACTED]")
    line = line.replace(MY_USER, "[REDACTED]")
    line = line.replace(MY_HOST, "[REDACTED]")
    
    # Маскируем все SSID из списка
    for ssid in MY_SSIDS:
        if ssid:  # Пропускаем пустые строки
            line = line.replace(ssid, "[REDACTED]")
    
    line = RE_IP4.sub("[REDACTED]", line)
    line = RE_IP6.sub("[REDACTED]", line)
    line = RE_MAC.sub("[REDACTED]", line)
    line = RE_EMAIL.sub("[REDACTED]", line)
    line = RE_PHONE.sub("[REDACTED]", line)
    line = RE_UUID.sub("[REDACTED]", line)
    line = RE_IMSI.sub("[REDACTED]", line)
    line = RE_ICCID.sub("[REDACTED]", line)
    
    line = RE_CARD_CANDIDATE.sub(mask_cards, line)
    line = RE_B64_CANDIDATE.sub(mask_base64, line)
    
    line = RE_GEO.sub(r"\1=[REDACTED]", line)
    line = RE_TOKENS.sub(r"\1=[REDACTED]", line)
    line = RE_SYS_IDS.sub(r"\1=[REDACTED]", line)
    return line

def cleanup_and_exit(signum=None, frame=None):
    global adb_process, is_exiting
    if is_exiting: return
    is_exiting = True
    
    print("\n[SF-Spy_SC] Финал теста. Корректно завершаем сессию adb...")
    if adb_process and adb_process.poll() is None:
        adb_process.terminate()
        try:
            adb_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}[+]{Colors.RESET} [SF-safety] ADB завис. Принудительное уничтожение (SIGKILL)...")
            adb_process.kill()
            adb_process.wait()
    print("[SF-Spy] Робот в полной безопасности. Логи зачищены и сохранены.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)



def print_fun_fuct():
    fact = random.choice(FUN_FACTS)
    print(f"А ты знал что {fact}")

def main():
    print(f"{Colors.GREEN}[+]{Colors.RESET} === Утилита SFspy-Android v1.0 — Официальный релиз ===")
    global adb_process, last_fact_time
    
    # ... проверка ADB, очистка буфера ...
    
    start_time = time.time()
    last_size_check = time.time()
    logcat_cmd = ["adb", "logcat"]
    
    try:
        adb_process = subprocess.Popen(
            logcat_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, 
            text=True, bufsize=1, errors="replace"
        )
        
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- ГЛОБАЛЬНЫЙ МОНИТОРИНГ ЗАПУЩЕН V7.6: {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.flush()
            

            while True:
                current_time = time.time()
                

                if current_time - last_fact_time >= FACT_INTERVAL:
                    print_fun_fuct()
                    last_fact_time = current_time

                
                if current_time - start_time >= TIMEOUT_SECONDS:
                    print(f"{Colors.GREEN}[+]{Colors.RESET} [+] Время теста ({TIMEOUT_SECONDS}) вышло. Сбор данных окончен.")
                    break
                    
                if current_time - last_size_check >= SIZE_CHECK_INTERVAL:
                    last_size_check = current_time
                    if os.path.exists(OUTPUT_FILE):
                        if (os.path.getsize(OUTPUT_FILE) / (1024 * 1024)) >= MAX_SIZE_MB:
                            print(f"{Colors.RED}[+]{Colors.RESET} [!] СТОП: Превышен безопасный лимит диска ({MAX_SIZE_MB} МБ/ГБ/ТБ).")
                            break

                rlist, _, _ = select.select([adb_process.stdout], [], [], 1.0)
                
                if rlist:
                    line = adb_process.stdout.readline()
                    if not line:
                        print(f"{Colors.RED}[+]{Colors.RESET} [!] Поток adb закрылся.")
                        break
                        
                    if FILTER_PATTERN.search(line):
                        f.write(clean_line(line))
                        f.flush()

        
    except PermissionError:
        print(f"{Colors.RED}[+]{Colors.RESET} [!] Ошибка: Нет прав на запись в файл {OUTPUT_FILE}!")
    except Exception as e:
        print(f"{Colors.RED}[+]{Colors.RESET} [!] Системный сбой во время мониторинга: {e}")
    finally:
        cleanup_and_exit()


print("пока мы собираем данные, давай поиграем в игру")

def get_number():
    first = int(input("Введи первое число: "))
    second = int(input("Введи второе число: "))
    target = int(input("Какое число хочешь выбить? "))
    return first, second, target

def play():
    first, second, target = get_number()
    attempts = 0
    
    while True:
        attempts += 1
        result = random.randint(first, second)
        print(f"Попытка {attempts}: выпало {result}")
        
        if result == target:
            print(f"Поздравляю! Число {target} выбито с {attempts} попытки!")
            break

# Запускаем игру
while True:
    play()
    again = input("Играть ещё? (y/n): ").lower()
    if again != 'y':
        print("Всё, хватит! Чтобы остановить — Ctrl+C")
        break

if __name__ == "__main__":
    main()
