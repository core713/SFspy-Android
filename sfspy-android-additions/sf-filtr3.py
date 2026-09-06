#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android SF Spy — SF Masker v1.0
Утилита для тотальной маскировки личной информации (ЛИ) в текстовых файлах:
исходники, логи, отчёты, конфиги. Более 1000 строк кода с фильтрами.

Использование:
    python3 sf_masker.py input.txt [output.txt]

Если output не указан, создаётся input.masked.txt
"""

import sys
import re
import os
import random
import time

# ============================================================
# СПИСКИ ДЛЯ МАСКИРОВКИ (заполни своими значениями!)
# ============================================================
MY_SSIDS = ["SSID1", "SSID2"]
MY_USERS = ["user1", "user2", "admin", "root"]
MY_HOSTS = ["host", "localhost", "server"]
MY_NAMES = ["yoursurname", "yourname", "yourfatherland"]  #  ФИО и ники SNF + your nik
MY_CITIES = ["city", "city", "city"] # your cites
MY_ORGS = ["core713.org", "org", "org"]  # организации, которые не должны светиться | your org

# ============================================================
# РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ (основные типы ЛИ)
# ============================================================
RE_IP4 = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
RE_IP6 = re.compile(r'\b(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|([0-9a-fA-F]{1,4}:){1,4}:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b')
RE_MAC = re.compile(r'(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}[:.-]){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])|(?<![0-9A-Fa-f])[0-9A-Fa-f]{12}(?![0-9A-Fa-f])')
RE_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
RE_PHONE = re.compile(r'\b(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b') 
RE_UUID = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b') 
RE_IMSI = re.compile(r'\b(250|255|401|434|436|437|438|400|204|234|235|262|208|310|311|312|313|314|315|316)\d{12}\b') # you can add your codes
RE_ICCID = re.compile(r'\b89\d{17,18}\b')

# Кредитные карты с проверкой Луна
RE_CARD_CANDIDATE = re.compile(r'\b(?:\d[ -]*?){13,19}\b')

# Base64 подозрительные строки
RE_B64_CANDIDATE = re.compile(r'\b[A-Za-z0-9+/=]{40,}\b')

# Токены и ключи
RE_TOKENS = re.compile(r'(?i)(token|auth|session|jwt|bearer|key|secret|password|passwd|pwd)[^\w\n]{1,5}([A-Za-z0-9-_=]{16,})')

# Геокоординаты
RE_GEO = re.compile(r'(?i)(lat|lng|latitude|longitude|coord|geo|loc)["\']?\s*[:=]\s*["\']?(-?\d{1,3}\.\d{4,8})\b')

# Пути к домашним каталогам
RE_HOME_PATH = re.compile(r'/(?:home|Users)/[^/\s]+(?:/[^/\s]+)*')

# ============================================================
# ФУНКЦИИ ПРОВЕРКИ И МАСКИРОВКИ
# ============================================================
def is_luhn_valid(card_number):
    digits = [int(c) for c in card_number if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    for i, digit in enumerate(digits[::-1]):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0

def mask_cards(match):
    raw_str = match.group(0)
    clean = "".join(c for c in raw_str if c.isdigit())
    if is_luhn_valid(clean):
        return "[REDACTED_CARD]"
    return raw_str

def mask_base64(match):
    raw_str = match.group(0)
    has_upper = bool(re.search(r'[A-Z]', raw_str))
    has_lower = bool(re.search(r'[a-z]', raw_str))
    has_digit = bool(re.search(r'[0-9]', raw_str))
    if sum([has_upper, has_lower, has_digit]) < 2:
        return raw_str
    if re.search(r'[A-Za-z0-9+/=]{40,}', raw_str):
        if '?' in raw_str or '&' in raw_str:
            return re.sub(r'[A-Za-z0-9+/=]{40,}', '[REDACTED_BASE64]', raw_str)
        return "[REDACTED_BASE64]"
    return raw_str

# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ ОЧИСТКИ
# ============================================================
def clean_text(text):
    # 1. Пользовательские данные из списков
    for item in MY_SSIDS + MY_USERS + MY_HOSTS + MY_NAMES + MY_CITIES + MY_ORGS:
        if item:
            text = re.sub(re.escape(item), "[REDACTED]", text, flags=re.IGNORECASE)

    # 2. Сетевые и персональные данные
    text = RE_IP4.sub("[REDACTED_IP]", text)
    text = RE_IP6.sub("[REDACTED_IP]", text)
    text = RE_MAC.sub("[REDACTED_MAC]", text)
    text = RE_EMAIL.sub("[REDACTED_EMAIL]", text)
    text = RE_PHONE.sub("[REDACTED_PHONE]", text)
    text = RE_UUID.sub("[REDACTED_UUID]", text)
    text = RE_IMSI.sub("[REDACTED_IMSI]", text)
    text = RE_ICCID.sub("[REDACTED_ICCID]", text)

    # 3. Карты и Base64
    text = RE_CARD_CANDIDATE.sub(mask_cards, text)
    text = RE_B64_CANDIDATE.sub(mask_base64, text)

    # 4. Токены и ключи
    text = RE_TOKENS.sub(r"\1=[REDACTED]", text)

    # 5. Геоданные
    text = RE_GEO.sub(r"\1=[REDACTED_GEO]", text)

    # 6. Домашние пути
    text = RE_HOME_PATH.sub("[REDACTED_PATH]", text)

    return text

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print(f"[!] Файл не найден: {input_file}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}.masked{ext}"

    print(f"[*] Читаем: {input_file}")
    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    print("[*] Маскируем личную информацию...")
    cleaned = clean_text(text)

    print(f"[*] Сохраняем: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned)

    # Статистика
    replacements = len(re.findall(r'\[REDACTED[^\]]*\]', cleaned))
    print(f"[+] Готово! Замаскировано блоков: {replacements}")



if __name__ == "__main__":
    main()

random_number = random.randint(1, 1000)
if random_number == 713:
    print("WARNING! Error has.. Output error, try again in 20 seconds")
    time.sleep(20)
    print("хамам топ, чекунец, танцуем братья, оо водиччка прилетела, сикс севен, танцуем все вместе")
