#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SFspy-Android Console [Interactive Terminal Edition]

import os
import sys
import re
import time
import signal
import argparse

class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'

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
    print(f"{Colors.BLUE}[+]{Colors.RESET} Консоль готова! Введите 'help' или '--help'.\n")
    
    while True:
        try:
            command = input(f"{Colors.GREEN}SFspy>{Colors.RESET} ").strip()
            
            if not command:
                continue
                
            # Парсим команду
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd in ['--st', '--start']:
                # Простой парсинг аргументов
                package = None
                timeout_seconds = 10800  # default 3h
                max_size_mb = 500  # default 500MB
                
                i = 1
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
                    
            elif cmd in ['--help', 'help']:
                help_command()
            elif cmd == '--stop':
                print(f"{Colors.RED}[+]{Colors.RESET} Мониторинг остановлен")
            elif cmd == '--status':
                print(f"{Colors.YELLOW}[+]{Colors.RESET} Статус: не запущено")
            elif cmd == '--clear':
                os.system('clear' if os.name == 'posix' else 'cls')
            elif cmd == '--exit':
                print(f"{Colors.RED}[+] Завершение работы...{Colors.RESET}")
                sys.exit(0)
            else:
                print(f"{Colors.RED}[+]{Colors.RESET} Неизвестная команда: {cmd}")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[+]{Colors.RESET} Введите '--exit' для выхода")
        except EOFError:
            sys.exit(0)

if __name__ == "__main__":
    interactive_console()
