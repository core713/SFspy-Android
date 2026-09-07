#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SFspy-Android Console [Interactive Terminal Edition]

import os
import sys
import re
import time
import signal
import argparse
import random
import readline
import atexit
import subprocess
import select
import math
import tkinter as tk
from tkinter import ttk

class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'

# --- ИСТОРИЯ ---
HISTORY_FILE = os.path.expanduser("~/.sfspy_history")

def setup_history():
    readline.set_auto_history(False)
    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except:
            pass
    readline.set_history_length(1000)
    atexit.register(readline.write_history_file, HISTORY_FILE)

def add_to_history(command):
    if command:
        history_len = readline.get_current_history_length()
        if history_len == 0 or readline.get_history_item(history_len) != command:
            readline.add_history(command)

def show_history():
    length = readline.get_current_history_length()
    if length == 0:
        print(f"{Colors.YELLOW}[+]{Colors.RESET} История пуста.")
        return
    for i in range(1, length + 1):
        print(f"{Colors.CYAN}{i}{Colors.RESET}: {readline.get_history_item(i)}")

# --- СПИСОК ФАКТОВ ---
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

# --- ФУНКЦИЯ ИГРЫ ---
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

# --- ПАРСЕР ВРЕМЕНИ ---
def parse_time(time_str):
    time_str = time_str.strip().lower()
    match = re.match(r"^(\d+(?:\.\d+)?)([smhd])$", time_str)
    if not match:
        raise ValueError(f"Неверный формат времени: {time_str}")
    value = float(match.group(1))
    unit = match.group(2)
    seconds = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }[unit]
    return int(value * seconds)

# --- ПАРСЕР РАЗМЕРА ---
def parse_size(size_str):
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

# --- МАСКИРОВКА ЛИЧНЫХ ДАННЫХ ---
RE_IP4 = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
RE_MAC = re.compile(r'(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}[:.-]){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])|(?<![0-9A-Fa-f])[0-9A-Fa-f]{12}(?![0-9A-Fa-f])')
RE_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
RE_PHONE = re.compile(r'\b(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b')

def clean_line(line):
    line = RE_IP4.sub("[REDACTED]", line)
    line = RE_MAC.sub("[REDACTED]", line)
    line = RE_EMAIL.sub("[REDACTED]", line)
    line = RE_PHONE.sub("[REDACTED]", line)
    return line

# --- КЛАССИФИКАЦИЯ СОБЫТИЙ ---
BG_COLOR = "#1a1a2e"
CARD_BG = "#16213e"
TEXT_COLOR = "#e0e0e0"

EVENT_TYPES = {
    "START": "#00c853",
    "INIT": "#00bcd4",
    "NETWORK": "#2196f3",
    "CONTACTS": "#ffeb3b",
    "ERROR": "#ff9800",
    "CRITICAL": "#f44336",
    "ZOMBIE": "#9c27b0",
    "DIED": "#757575",
    "REVERT": "#e91e63",
    "WARNING": "#ff5722",
}

def classify_line(line):
    """Более точная классификация событий"""
    line_lower = line.lower()
    if "fatal" in line_lower or "crash" in line_lower or "androidruntime" in line_lower:
        return "CRITICAL"
    elif "zombie" in line_lower:
        return "ZOMBIE"
    elif "has died" in line_lower or ("process" in line_lower and "died" in line_lower):
        return "DIED"
    elif "start proc" in line_lower or "activitymanager: start" in line_lower:
        return "START"
    elif "contactsprovider" in line_lower:
        return "CONTACTS"
    elif "requestnetwork" in line_lower or "connectivityservice" in line_lower:
        return "NETWORK"
    elif "revert" in line_lower or "restart" in line_lower:
        return "REVERT"
    elif "warn" in line_lower:
        return "WARNING"
    elif "error" in line_lower or "exception" in line_lower:
        return "ERROR"
    else:
        return "INIT"

# --- BRAIN: ВИЗУАЛИЗАЦИЯ ЦЕПОЧЕК СОБЫТИЙ ---
class BrainGUI:
    def __init__(self, events, chains):
        self.events = events
        self.chains = chains

        self.window = tk.Tk()
        self.window.title("SFspy Brain - Event Chains")
        self.window.configure(bg=BG_COLOR)
        self.window.geometry("1200x700")

        self.canvas = tk.Canvas(self.window, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_scroll)

        self.drag_data = {"x": 0, "y": 0}
        self.zoom = 1.0

        self.draw_chains()
        self.create_controls()

        self.window.mainloop()

    def draw_hexagon(self, x, y, size, color, text):
        """Рисует шестиугольник с текстом"""
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.append((px, py))
        self.canvas.create_polygon(points, fill=color, outline="white", width=2)
        self.canvas.create_text(x, y, text=text, fill="white", font=("Arial", 9, "bold"))

    def draw_chains(self):
        """Рисует цепочки событий шестиугольниками"""
        y_offset = 60
        hex_size = 35

        for chain_idx, chain in enumerate(self.chains[:8]):
            x = 80
            prev_x = None
            prev_y = None

            self.canvas.create_text(50, y_offset, text=f"Chain {chain_idx+1}",
                                   fill=TEXT_COLOR, font=("Arial", 10, "bold"), anchor="e")

            for event in chain:
                color = EVENT_TYPES.get(event["type"], "#ffffff")
                self.draw_hexagon(x, y_offset, hex_size, color, event["type"])

                if prev_x is not None:
                    self.canvas.create_line(prev_x + hex_size, prev_y,
                                          x - hex_size, y_offset,
                                          fill=color, width=2, arrow="last")

                prev_x = x
                prev_y = y_offset
                x += hex_size * 2.5

            y_offset += hex_size * 2.5

        total_events = len(self.events)
        total_chains = len(self.chains)
        self.canvas.create_text(600, y_offset + 20,
                               text=f"Всего событий: {total_events} | Цепочек: {total_chains}",
                               fill=TEXT_COLOR, font=("Arial", 12, "bold"))

    def on_press(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move("all", dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release(self, event):
        pass

    def on_scroll(self, event):
        if event.delta > 0:
            self.canvas.move("all", 0, 20)
        else:
            self.canvas.move("all", 0, -20)

    def create_controls(self):
        frame = tk.Frame(self.window, bg=CARD_BG)
        frame.pack(side="bottom", fill="x")

        ttk.Button(frame, text="Zoom +", command=self.zoom_in).pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Zoom -", command=self.zoom_out).pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Reset", command=self.reset_view).pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Close", command=self.window.destroy).pack(side="right", padx=5, pady=5)

    def zoom_in(self):
        self.canvas.scale("all", 600, 300, 1.1, 1.1)

    def zoom_out(self):
        self.canvas.scale("all", 600, 300, 0.9, 0.9)

    def reset_view(self):
        self.canvas.delete("all")
        self.draw_chains()

def brain():
    """Открывает GUI с картой событий из лога"""
    output_file = None
    for f in os.listdir("."):
        if f.endswith("_report.txt"):
            if output_file is None or os.path.getmtime(f) > os.path.getmtime(output_file):
                output_file = f

    if not output_file:
        print(f"{Colors.RED}[+]{Colors.RESET} Файл отчёта не найден. Сначала запустите мониторинг.")
        return

    print(f"{Colors.CYAN}[+]{Colors.RESET} Читаю файл: {output_file}")

    events = []
    with open(output_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("---"):
                event_type = classify_line(line)
                events.append({"type": event_type, "line": line})

    if not events:
        print(f"{Colors.YELLOW}[+]{Colors.RESET} В логе нет событий.")
        return

    chains = []
    current_chain = []
    for event in events:
        if event["type"] == "START" and current_chain:
            chains.append(current_chain)
            current_chain = [event]
        else:
            current_chain.append(event)
    if current_chain:
        chains.append(current_chain)

    BrainGUI(events, chains)

# --- МОНИТОРИНГ ---
def monitoring_loop(package, timeout_seconds, max_size_mb):
    output_file = f"{package.replace('.', '_')}_report.txt"
    print(f"{Colors.CYAN}[+]{Colors.RESET} Файл отчёта: {output_file}")

    try:
        check = subprocess.run(["adb", "get-state"], capture_output=True, text=True, timeout=5)
        if check.returncode != 0:
            print(f"{Colors.RED}[+]{Colors.RESET} ADB не подключен или устройство не найдено.")
            return
    except FileNotFoundError:
        print(f"{Colors.RED}[+]{Colors.RESET} ADB не установлен. Установите android-tools.")
        return
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}[+]{Colors.RESET} Таймаут при проверке ADB.")
        return

    subprocess.run(["adb", "logcat", "-c"], capture_output=True, text=True)
    print(f"{Colors.GREEN}[+]{Colors.RESET} Мониторинг запущен для {package}. Нажмите Ctrl+C для остановки.")

    start_time = time.time()
    last_size_check = time.time()
    filter_pattern = re.compile(rf"({re.escape(package)}|Location|GPS|ActivityManager|Connectivity|Telephony|ContentProvider|PackageManager|ACCESS_FINE_LOCATION|READ_CONTACTS|READ_SMS|RECORD_AUDIO|CAMERA|INTERNET|OpenTelemetry|Watchdog|JobScheduler)", re.IGNORECASE)

    adb_process = subprocess.Popen(
        ["adb", "logcat"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        errors="replace"
    )

    try:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- Мониторинг запущен: {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.flush()

            while True:
                current_time = time.time()
                if current_time - start_time >= timeout_seconds:
                    print(f"{Colors.GREEN}[+]{Colors.RESET} Таймаут ({timeout_seconds} сек) достигнут.")
                    break

                if current_time - last_size_check >= 10:
                    last_size_check = current_time
                    if os.path.exists(output_file) and os.path.getsize(output_file) / (1024*1024) >= max_size_mb:
                        print(f"{Colors.RED}[+]{Colors.RESET} Достигнут лимит размера файла ({max_size_mb} МБ).")
                        break

                rlist, _, _ = select.select([adb_process.stdout], [], [], 1.0)
                if rlist:
                    line = adb_process.stdout.readline()
                    if not line:
                        print(f"{Colors.RED}[+]{Colors.RESET} Поток adb закрылся.")
                        break
                    if filter_pattern.search(line):
                        cleaned = clean_line(line)
                        f.write(cleaned)
                        f.flush()

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[+]{Colors.RESET} Мониторинг прерван пользователем.")
    except Exception as e:
        print(f"{Colors.RED}[+]{Colors.RESET} Ошибка во время мониторинга: {e}")
    finally:
        if adb_process and adb_process.poll() is None:
            adb_process.terminate()
            try:
                adb_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                adb_process.kill()
        print(f"{Colors.GREEN}[+]{Colors.RESET} Мониторинг завершён. Данные сохранены в {output_file}")

# --- КОМАНДА ЗАПУСКА МОНИТОРИНГА ---
def start_monitoring(package, timeout_seconds, max_size_mb):
    print(f"{Colors.GREEN}[+]{Colors.RESET} Запуск мониторинга...")
    print(f"{Colors.BLUE}[+]{Colors.RESET} Пакет: {package}")
    print(f"{Colors.BLUE}[+]{Colors.RESET} Таймаут: {timeout_seconds} сек ({timeout_seconds/3600:.2f} ч)")
    print(f"{Colors.BLUE}[+]{Colors.RESET} Максимальный размер: {max_size_mb:.1f} МБ")
    monitoring_loop(package, timeout_seconds, max_size_mb)

# --- СПРАВКА ---
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
  {Colors.CYAN}-t, --timeout{Colors.RESET} <время>      - таймаут (30h, 2d, 1.36h, 28m)
  {Colors.CYAN}-s, --size{Colors.RESET} <размер>        - макс. размер файла (500MB, 2GB)

{Colors.YELLOW}Команда brain:{Colors.RESET}
  {Colors.CYAN}brain{Colors.RESET} - визуализация цепочек событий

{Colors.YELLOW}Примеры:{Colors.RESET}
  sfspy --st -p "ru.oneme.app" -t 1.36h -s 5GB
  sfspy --st "ru.oneme.app" 30h 5GB
""")

# --- ИНТЕРАКТИВНАЯ КОНСОЛЬ ---
def interactive_console():
    setup_history()

    print(f"{Colors.GREEN}Hello to SFspy-Android utility, wait a minute, we load your konsole...{Colors.RESET}")
    time.sleep(1)
    print(f"{Colors.BLUE}[+]{Colors.RESET} Консоль готова! Введите 'help' для списка команд.\n")

    prompt = f"\001{Colors.GREEN}\002SFcns>\001{Colors.RESET}\002 "

    while True:
        try:
            command = input(prompt).strip()
            if not command:
                continue
            add_to_history(command)

            parts = command.split()
            cmd = parts[0].lower()

            if cmd == 'sfspy':
                if len(parts) < 2:
                    print(f"{Colors.YELLOW}[+]{Colors.RESET} Используйте: sfspy --действие")
                    print(f"{Colors.YELLOW}[+]{Colors.RESET} Действия: --st, --stop, --status")
                    continue
                action = parts[1].lower()

                if action in ['--st', '--start']:
                    package = None
                    timeout_seconds = 10800
                    max_size_mb = 500

                    i = 2
                    while i < len(parts):
                        if parts[i] in ['-p', '--package'] and i+1 < len(parts):
                            package = parts[i+1].strip('"').strip("'")
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
                        elif re.match(r"^\d+(?:\.\d+)?[smhd]$", parts[i], re.IGNORECASE):
                            try:
                                timeout_seconds = parse_time(parts[i])
                            except ValueError as e:
                                print(f"{Colors.RED}[+]{Colors.RESET} {e}")
                                break
                            i += 1
                        elif re.match(r"^\d+(?:\.\d+)?\s*(kb|mb|gb|tb)$", parts[i], re.IGNORECASE):
                            try:
                                max_size_mb = parse_size(parts[i])
                            except ValueError as e:
                                print(f"{Colors.RED}[+]{Colors.RESET} {e}")
                                break
                            i += 1
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

            elif cmd in ['help', '--help']:
                print(f"""
{Colors.GREEN}=== SFcns Console ==={Colors.RESET}

{Colors.YELLOW}Команды консоли:{Colors.RESET}
  {Colors.CYAN}help{Colors.RESET} - эта справка
  {Colors.CYAN}echo <текст>{Colors.RESET} - вывести текст
  {Colors.CYAN}clear{Colors.RESET} - очистить экран
  {Colors.CYAN}funfact{Colors.RESET} - случайный факт
  {Colors.CYAN}game{Colors.RESET} - мини-игра
  {Colors.CYAN}history{Colors.RESET} - показать историю
  {Colors.CYAN}brain{Colors.RESET} - карта событий
  {Colors.CYAN}exit{Colors.RESET} - выход

{Colors.YELLOW}Команды утилиты (только с sfspy):{Colors.RESET}
  {Colors.CYAN}sfspy --st "пакет" 1.36h 5GB{Colors.RESET}
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

            elif cmd == 'history':
                show_history()

            elif cmd == 'brain':
                brain()

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
