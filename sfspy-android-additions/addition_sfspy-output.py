#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os
from datetime import datetime

# КОНФИГУРАЦИЯ
INPUT_FILE = ""   # your name file
OUTPUT_FILE = "" # your output name file
PACKAGE = "" # your name package

# Расширенный фильтр для повторной зачистки (добавил новые паттерны)
EXTRA_REDACT = [
    (r'(?i)(uuid|token|auth|session|jwt|bearer|key|secret)[^\w\n]{1,5}([A-Za-z0-9-_=]{16,})', r'\1=[REDACTED]'),
    (r'(?i)(android_id|imei|meid|serial|sn|hardware_id|device_id)[^\w\n]{1,5}([A-Za-z0-9-]{6,20})', r'\1=[REDACTED]'),
    (r'(?i)(lat|lng|latitude|longitude|coord|geo|loc)["\']?\s*[:=]\s*["\']?(-?\d{1,3}\.\d{4,8})', r'\1=[REDACTED]'),
]

def clean_line(line):
    # 1. Прямые замены
    line = line.replace(PACKAGE, "[PACKAGE]")
    # 2. Убираем явные PID и UID (чтобы не было возможности связать логи)
    line = re.sub(r'pid\s*=\s*\d+', 'pid=[REDACTED]', line, flags=re.I)
    line = re.sub(r'uid\s*=\s*\d+', 'uid=[REDACTED]', line, flags=re.I)
    # 3. Дополнительные фильтры
    for pattern, repl in EXTRA_REDACT:
        line = re.sub(pattern, repl, line, flags=re.I)
    return line

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[!] Файл {INPUT_FILE} не найден!")
        return

    print(f"[+] Читаю {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"[+] Найдено {len(lines)} строк. Ищем {PACKAGE}...")
    filtered = []
    for line in lines:
        if PACKAGE in line:
            filtered.append(clean_line(line))

    if not filtered:
        print("[!] Ничего не найдено.")
        return

    print(f"[+] Найдено {len(filtered)} строк с {PACKAGE}.")

    # Дополнительно: группируем по типу события (можно потом раскомментировать)
    # categories = {"START": [], "ERROR": [], "PERMISSION": [], "OTHER": []}
    # for line in filtered:
    #     if "ActivityManager" in line and "Start proc" in line:
    #         categories["START"].append(line)
    #     elif "Error" in line or "FATAL" in line:
    #         categories["ERROR"].append(line)
    #     elif "Permission" in line or "Denial" in line:
    #         categories["PERMISSION"].append(line)
    #     else:
    #         categories["OTHER"].append(line)

    # Сохраняем в файл
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"--- ОТЧЁТ ПО {PACKAGE} ---\n")
        f.write(f"Создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Всего строк: {len(filtered)}\n")
        f.write("-" * 60 + "\n")
        f.write("\n".join(filtered))

    print(f"[+] Готово! Отчёт сохранён в {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
