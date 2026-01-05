from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os
from urllib.parse import urlparse

def url_image(page_url: str):
    """
    Rasmni Freepik sahifasidan yuklab oladi.
    return: folder nomi, fayllar ro'yxati
    """
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")  # serverda shart
    options.add_argument("--no-sandbox")  # server uchun kerak
    options.add_argument("--disable-dev-shm-usage")  # crash oldini oladi
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-allow-origins=*")  # yangi Chrome uchun
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
    
    # Binary path (serverda kerak bo'lishi mumkin)
    options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


    image_url = None

    try:
        driver.get(page_url)
        time.sleep(5)  # sahifa yuklanishini kutish

        img = driver.find_element(
            By.CSS_SELECTOR,
            "img.size-full.object-contain"
        )
        image_url = img.get_attribute("src")
        print("Rasm URL:", image_url)

    except Exception as e:
        print("Rasm topilmadi:", e)

    finally:
        driver.quit()

    if not image_url:
        return None, None

    # Papka yaratish
    save_dir = "rasmlar"
    os.makedirs(save_dir, exist_ok=True)

    # URLdan nom olish
    parsed = urlparse(page_url)
    name_slug = os.path.basename(parsed.path).replace(".htm", "").replace(".html", "")
    
    # Fayl nomlari
    orig_filename = os.path.join(save_dir, f"{name_slug}.jpg")  # asl rasm
    psd_filename = os.path.join(save_dir, f"{name_slug}.psd")    # PSD nusxa
    eps_filename = os.path.join(save_dir, f"{name_slug}.eps")    # EPS nusxa

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.freepik.com/"
    }

    try:
        r = requests.get(image_url, headers=headers, timeout=15)
        if r.status_code == 200:
            # Asl rasmni saqlash
            # with open(orig_filename, "wb") as f:
            #     f.write(r.content)
            # print("Asl rasm yuklandi:", orig_filename)
            
            # # PSD nusxasini yaratish
            # with open(psd_filename, "wb") as f:
            #     f.write(r.content)
            # print("PSD fayl yaratildi:", psd_filename)

            # return save_dir, [orig_filename, psd_filename]
        
            with open(orig_filename, "wb") as f:
                f.write(r.content)
            print("Asl rasm yuklandi:", orig_filename)

            # PSD nusxasini yaratish
            with open(psd_filename, "wb") as f:
                f.write(r.content)
            print("PSD fayl yaratildi:", psd_filename)

            # EPS nusxasini yaratish
            with open(eps_filename, "wb") as f:
                f.write(r.content)
            print("EPS fayl yaratildi:", eps_filename)

            # return qilinadigan fayllar ro'yxati
            return save_dir, [orig_filename, psd_filename, eps_filename]

        else:
            print("Download xato:", r.status_code)
            return None, None

    except Exception as e:
        print("Download exception:", e)
        return None, None
