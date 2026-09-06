
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SFspy-Android Console [Interactive Terminal Edition]

import os
import sys
import re
import time
import signal
import argparse
import random  # <-- ДОБАВИЛ

class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'

# --- ДОБАВИЛ СПИСОК ФАКТОВ ---
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

# --- ДОБАВИЛ ФУНКЦИЮ ИГРЫ ---
def play_game():
    print("\nПока мы собираем данные, давай поиграем в игру!")
    while True:
        try:
            first = int(input("Введи первое число: "))
            second = int(input("Введи второе число: "))
            target = int(input("Какое число хочешь выбить? "))
            
            if second <= first:
                print("Ошибка: второе число должно быть больше первого!")
                print("Засыпаем на 40 секунд, чтобы ты осознал...")
                time.sleep(40)
                continue
                
            if target < first or target > second:
                print(f"Ошибка: число {target} не входит в диапазон {first}–{second}!")
                print("Засыпаем на 40 секунд, чтобы ты подумал...")
                time.sleep(40)
                continue
                
            attempts = 0
            while True:
                attempts += 1
                result = random.randint(first, second)
                print(f"Попытка {attempts}: выпало {result}")
                if result == target:
                    print(f"Поздравляю! Число {target} выбито с {attempts} попытки!")
                    break
                    
            again = input("Играть ещё? (y/n): ").lower()
            if again != 'y':
                print("Всё, хватит! Чтобы остановить — Ctrl+C")
                break
                
        except ValueError:
            print("Ошибка: нужно вводить только числа, а не буквы!")
            print("Засыпаем на 40 секунд, чтобы ты отдохнул...")
            time.sleep(40)

# --- ПАРСЕР ВРЕМЕНИ (30h, 5m, 2d, 1h30m) ---
def parse_time(time_str):
    """Конвертирует строку времени в секунды"""
    time_regex = re.compile(r'(\d+)([smhd])')
    matches = time_regex.findall(time_str.lower())
    
    if not matches:
        raise ValueError(f"Неверный формат времени: {time_str}")
    
    total_seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit == 's':
            total_seconds += value
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 'h':
            total_seconds += value * 3600
        elif unit == 'd':
            total_seconds += value * 86400
    
    return total_seconds

# --- ПАРСЕР РАЗМЕРА (500MB, 2GB, 1TB) ---
def parse_size(size_str):
    """Конвертирует строку размера в мегабайты"""
    size_regex = re.compile(r'(\d+(?:\.\d+)?)\s*(kb|mb|gb|tb)?', re.IGNORECASE)
    match = size_regex.match(size_str.strip())
    
    if not match:
        raise ValueError(f"Неверный формат размера: {size_str}")
    
    value = float(match.group(1))
    unit = match.group(2).lower() if match.group(2) else 'mb'
    
    multipliers = {
        'kb': 1/1024,
        'mb': 1,
        'gb': 1024,
        'tb': 1024*1024
    }
    
    return value * multipliers[unit]

# --- ОСНОВНЫЕ ФУНКЦИИ КОМАНД ---
def start_monitoring(package, timeout_seconds, max_size_mb):
    print(f"{Colors.GREEN}[+]{Colors.RESET} Запуск мониторинга...")
    print(f"{Colors.BLUE}[+]{Colors.RESET} Пакет: {package}")
    print(f"{Colors.BLUE}[+]{Colors.RESET} Таймаут: {timeout_seconds} сек ({timeout_seconds/3600:.1f} ч)")
    print(f"{Colors.BLUE}[+]{Colors.RESET} Максимальный размер: {max_size_mb:.1f} МБ")
    # Здесь будет вызов основной функции мониторинга

def help_command():
    print(f"""
{Colors.GREEN}=== SFspy-Android Console ==={Colors.RESET}

{Colors.YELLOW}Краткие команды:{Colors.RESET}
  {Colors.CYAN}sfspy --st{Colors.RESET} - запустить мониторинг
  {Colors.CYAN}sfspy --help{Colors.RESET} - справка
  {Colors.CYAN}sfspy --stop{Colors.RESET} - остановить
  {Colors.CYAN}sfspy --status{Colors.RESET} - статус
  {Colors.CYAN}sfspy --clear{Colors.RESET} - очистить экран
  {Colors.CYAN}sfspy --exit{Colors.RESET} - выход

{Colors.YELLOW}Опции для --st:{Colors.RESET}
  {Colors.CYAN}-p, --package{Colors.RESET} <имя_пакета>  - целевой пакет
  {Colors.CYAN}-t, --timeout{Colors.RESET} <время>      - таймаут (30h, 2d, 1h30m)
  {Colors.CYAN}-s, --size{Colors.RESET} <размер>        - макс. размер файла (500MB, 2GB)

{Colors.YELLOW}Пример:{Colors.RESET}
  sfspy --st -p "ru.oneme.app" -t 30h -s 5GB
""")

# --- ИНТЕРАКТИВНАЯ КОНСОЛЬ ---
def interactive_console():
    print(f"{Colors.GREEN}Hello to SFspy-Android utility, wait a minute, we load your konsole...{Colors.RESET}")
    time.sleep(1)
    print(f"{Colors.BLUE}[+]{Colors.RESET} Консоль готова! Введите 'help' для списка команд.\n")
    
    while True:
        try:
            command = input(f"{Colors.GREEN}SFcns>{Colors.RESET} ").strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            # --- Команды утилиты (с префиксом sfspy) ---
            if cmd == 'sfspy':
                if len(parts) < 2:
                    print(f"{Colors.YELLOW}[+]{Colors.RESET} Используйте: sfspy --действие")
                    print(f"{Colors.YELLOW}[+]{Colors.RESET} Действия: --st, --stop, --status")
                    continue
                    
                action = parts[1].lower()
                
                if action in ['--st', '--start']:
                    # Парсим аргументы
                    package = None
                    timeout_seconds = 10800
                    max_size_mb = 500
                    
                    i = 2
                    while i < len(parts):
                        if parts[i] in ['-p', '--package'] and i+1 < len(parts):
                            package = parts[i+1]
                            i += 2
                        elif parts[i] in ['-t', '--timeout'] and i+1 < len(parts):
                            try:
                                timeout_seconds = parse_time(parts[i+1])
                            except ValueError as e:
                                print(f"{Colors.RED}[+]{Colors.RESET} {e}")
                                break
                            i += 2
                        elif parts[i] in ['-s', '--size'] and i+1 < len(parts):
                            try:
                                max_size_mb = parse_size(parts[i+1])
                            except ValueError as e:
                                print(f"{Colors.RED}[+]{Colors.RESET} {e}")
                                break
                            i += 2
                        else:
                            print(f"{Colors.RED}[+]{Colors.RESET} Неизвестный аргумент: {parts[i]}")
                            i += 1
                    
                    if package:
                        start_monitoring(package, timeout_seconds, max_size_mb)
                    else:
                        print(f"{Colors.YELLOW}[+]{Colors.RESET} Укажите пакет: -p <имя_пакета>")
                        
                elif action == '--stop':
                    print(f"{Colors.RED}[+]{Colors.RESET} Мониторинг остановлен")
                    
                elif action == '--status':
                    print(f"{Colors.GREEN}SFspy*{Colors.RESET} {Colors.YELLOW}Active{Colors.RESET}")
                    
                elif action == '--help':
                    print(f"""
{Colors.GREEN}=== Действия утилиты SFspy ==={Colors.RESET}
  {Colors.CYAN}sfspy --st{Colors.RESET} - запустить мониторинг
  {Colors.CYAN}sfspy --stop{Colors.RESET} - остановить
  {Colors.CYAN}sfspy --status{Colors.RESET} - статус
  {Colors.CYAN}sfspy --help{Colors.RESET} - это сообщение
""")
                else:
                    print(f"{Colors.RED}[+]{Colors.RESET} Неизвестное действие: {action}")
                    print(f"{Colors.YELLOW}[+]{Colors.RESET} Доступные: --st, --stop, --status, --help")
            
            # --- Команды консоли (без префикса) ---
            elif cmd in ['help', '--help']:
                print(f"""
{Colors.GREEN}=== SFcns Console ==={Colors.RESET}

{Colors.YELLOW}Команды консоли:{Colors.RESET}
  {Colors.CYAN}help{Colors.RESET} - эта справка
  {Colors.CYAN}echo <текст>{Colors.RESET} - вывести текст
  {Colors.CYAN}clear{Colors.RESET} - очистить экран
  {Colors.CYAN}funfact{Colors.RESET} - случайный факт
  {Colors.CYAN}game{Colors.RESET} - мини-игра
  {Colors.CYAN}exit{Colors.RESET} - выход

{Colors.YELLOW}Команды утилиты (только с sfspy):{Colors.RESET}
  {Colors.CYAN}sfspy --st -p "пакет" -t 30h -s 5GB{Colors.RESET}
  {Colors.CYAN}sfspy --status{Colors.RESET}
  {Colors.CYAN}sfspy --stop{Colors.RESET}
""")
                
            elif cmd == 'echo':
                echo_text = ' '.join(parts[1:])
                if echo_text:
                    print(echo_text)
                else:
                    print(f"{Colors.YELLOW}[+]{Colors.RESET} Используйте: echo <текст>")
                    
            elif cmd == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                
            elif cmd == 'funfact':
                fact = random.choice(FUN_FACTS)
                print(f"{Colors.YELLOW}[FACT]{Colors.RESET} {fact}")
                
            elif cmd == 'game':
                print(f"{Colors.MAGENTA}[+]{Colors.RESET} Запускаю игру...")
                play_game()
                
            elif cmd == 'exit':
                print(f"{Colors.RED}[+]{Colors.RESET} Завершение работы...")
                sys.exit(0)
                
            else:
                print(f"{Colors.RED}[+]{Colors.RESET} Неизвестная команда: {cmd}")
                print(f"{Colors.YELLOW}[+]{Colors.RESET} Введите 'help' для списка команд.")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[+]{Colors.RESET} Нажмите 'exit' для выхода")
        except EOFError:
            sys.exit(0)

# --- ВЫЗОВ КОНСОЛИ ---
if __name__ == "__main__":
    interactive_console()
