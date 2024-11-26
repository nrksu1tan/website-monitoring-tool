import os
import time
import hashlib
import pickle
import requests
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from PIL import Image, ImageChops
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from tqdm import tqdm  # Полоска загрузки
from selenium.webdriver.common.action_chains import ActionChains
from colorama import init, Fore, Style
import tkinter as tk
from tkinter import ttk
import ctypes
from tkinter.messagebox import showinfo

init(autoreset=True)

URL = "https://gaming.lenovo.com/human-fall-flat"
CHECK_INTERVAL = 7200  
CHROMEDRIVER_PATH = "C:\\chromedriver-win64\\chromedriver.exe"  #chromedriver
COOKIE_ACCEPT_BUTTON_XPATH = "//button[contains(text(), 'Принять') or contains(text(), 'Accept')]"


options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Работать без отображения браузера
options.add_argument("--disable-cache")
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

#cookies
def save_cookies(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookies(driver, path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

#hash
def create_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

#fullscreensot
def capture_screenshot(driver, path):
    try:

        screenshot_data = driver.execute_cdp_cmd("Page.captureScreenshot", {"captureBeyondViewport": True, "fromSurface": True})
        screenshot = base64.b64decode(screenshot_data['data'])
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        screenshot = driver.get_screenshot_as_png()
    with open(path, "wb") as f:
        f.write(screenshot)


def compare_screenshots(old_path, new_path):
    if not os.path.exists(old_path):
        return False  # Если старого скриншота нет, считаем, что изменения есть
    old_img = Image.open(old_path)
    new_img = Image.open(new_path)
    diff = ImageChops.difference(old_img, new_img)
    return diff.getbbox() is None  # True, если изображения идентичны


# 1HTML BeautifulSoup
def compare_html_structure(old_html, new_html):
    old_soup = BeautifulSoup(old_html, "html.parser")
    new_soup = BeautifulSoup(new_html, "html.parser")
    return old_soup == new_soup  # Сравниваем объекты BeautifulSoup

# 2. dom
def compare_dom_elements(driver, old_elements):
    new_elements = driver.find_elements(By.XPATH, "//*")  # Выборка всех элементов DOM
    return len(old_elements) == len(new_elements) and all(oe == ne.text for oe, ne in zip(old_elements, new_elements))

# 3.h1 h2
def check_key_headers(html):
    soup = BeautifulSoup(html, "html.parser")
    headers = [header.get_text(strip=True) for header in soup.find_all(["h1", "h2"])]
    return headers

# 4. css
def compare_css_files(old_css, new_css):
    return old_css == new_css

def monitor_site(manual=False):
    driver.get(URL)
    
    #cookies
    if os.path.exists('cookies.pkl'):
        load_cookies(driver, 'cookies.pkl')
        driver.refresh()
    else:
        # apply cookies
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, COOKIE_ACCEPT_BUTTON_XPATH))
            )
            accept_button.click()
            # save choice
            save_cookies(driver, 'cookies.pkl')
        except Exception as e:
            print(f"Не удалось принять куки | Failed to accept cookies: {e}")
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    #waiting for the correct site view
    for _ in tqdm(range(10), desc="wait for true fersion кароч", unit="сек"):
        time.sleep(1)


    html_content = driver.page_source

    # 1. HTML hash compare
    html_hash = create_hash(html_content)
    if not os.path.exists("html_hash.txt"):
        with open("html_hash.txt", "w", encoding="utf-8") as f:
            f.write("")  # Создание пустого файла
    with open("html_hash.txt", "r+", encoding="utf-8") as f:
        old_html_hash = f.read().strip()
        f.seek(0)
        f.write(html_hash)
        f.truncate()
    if html_hash == old_html_hash:
        html_status = f"{Fore.GREEN}Без изменений | Without changes"
    else:
        html_status = f"{Fore.RED}Изменения обнаружены | Changes detected"

    # 2. HTML compare str
    if os.path.exists("old_html_content.html"):
        with open("old_html_content.html", "r", encoding="utf-8") as f:
            old_html_content = f.read()
        if compare_html_structure(old_html_content, html_content):
            structure_status = f"{Fore.GREEN}Без изменений | Without changes"
        else:
            structure_status = f"{Fore.RED}Изменения обнаружены | Changes detected"
    else:
        structure_status = f"{Fore.YELLOW}Первая проверка (нет данных для сравнения)"
    with open("old_html_content.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # 3. DOM
    try:
        with open("old_dom_elements.pkl", "rb") as f:
            old_dom_elements = pickle.load(f)
        if compare_dom_elements(driver, old_dom_elements):
            dom_status = f"{Fore.GREEN}Без изменений | Without changes"
        else:
            dom_status = f"{Fore.RED}Изменения обнаружены | Changes detected"
    except (EOFError, FileNotFoundError, pickle.UnpicklingError):
        dom_status = f"{Fore.YELLOW}Первая проверка (нет данных для сравнения)"
        old_dom_elements = []
    
    old_dom_elements = [element.text for element in driver.find_elements(By.XPATH, "//*")]
    with open("old_dom_elements.pkl", "wb") as f:
        pickle.dump(old_dom_elements, f)

    # 4. h1 h2
    headers = check_key_headers(html_content)
    if headers:
        headers_status = f"{Fore.GREEN}Найдены заголовки | Headers found: {', '.join(headers)}"
    else:
        headers_status = f"{Fore.RED}Заголовки не найдены | The headers were not found"

    # 5. save and compare screeshots
    screenshot_path = "current_screenshot.png"
    old_screenshot_path = "old_screenshot.png"
    capture_screenshot(driver, screenshot_path)
    if os.path.exists(old_screenshot_path):
        if compare_screenshots(old_screenshot_path, screenshot_path):
            screenshot_status = f"{Fore.GREEN}Скриншоты идентичны"
        else:
            screenshot_status = f"{Fore.RED}Изменения на скриншоте обнаружены | Changes have been detected in the screenshot"
    else:
        screenshot_status = f"{Fore.YELLOW}Первая проверка (нет скриншота для сравнения) | First check (no screenshot for comparison)"
    # newshot
    os.replace(screenshot_path, old_screenshot_path)

    # 6. CSS compare
    css_links = driver.find_elements(By.XPATH, "//link[@rel='stylesheet']")
    css_content = ""
    for link in css_links:
        href = link.get_attribute("href")
        if href:
            response = requests.get(href)
            css_content += response.text

    css_hash = create_hash(css_content)
    if not os.path.exists("css_hash.txt"):
        with open("css_hash.txt", "w", encoding="utf-8") as f:
            f.write("")
    with open("css_hash.txt", "r+", encoding="utf-8") as f:
        old_css_hash = f.read().strip()
        f.seek(0)
        f.write(css_hash)
        f.truncate()
    if css_hash == old_css_hash:
        css_status = f"{Fore.GREEN}CSS без изменений | CSS unchanged"
    else:
        css_status = f"{Fore.RED}Изменения в CSS обнаружены | CSS changes detected"

    # Вывод результатов с улучшенным форматированием
    print(f"\nПроверка сайта: {URL}\n")
    print(f"{Style.BRIGHT}Сравнение HTML-хеша | HTML Hash Comparison ---------------- {html_status}")
    print(f"{Style.BRIGHT}Сравнение HTML-структуры | HTML Structure Comparison ------ {structure_status}")
    print(f"{Style.BRIGHT}Проверка DOM-элементов | DOM Elements Check ---------------- {dom_status}")
    print(f"{Style.BRIGHT}Проверка заголовков | Headers Check ----------------------- {headers_status}")
    print(f"{Style.BRIGHT}Сравнение скриншотов | Screenshot Comparison -------------- {screenshot_status}")
    print(f"{Style.BRIGHT}Сравнение CSS | CSS Comparison --------------------------- {css_status}")

    if manual:
        print("\nРучная проверка завершена | The manual check is completed.\n")

# Основная функция
def main():
    print("Парсер запущен. Для ручной проверки введите 'check' или нажмите Ctrl+C для выхода.")
    print("The parser is running. To manually check, type 'check' or press Ctrl+C to exit")
    try:
        while True:
            user_input = input(">> ").strip().lower()
            if user_input == "check":
                monitor_site(manual=True)
            else:
                print("Неизвестная команда. Используйте 'check' для проверки или завершите программу.")
                print("Unknown command. Use 'check' to check or terminate the program.")
    except KeyboardInterrupt:
        print("\nМониторинг остановлен | Monitoring stopped.")
    finally:
        driver.quit()

        

# Запуск программы
if __name__ == "__main__":
    main()