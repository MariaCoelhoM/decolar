from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def buscar_voo():
    url = "https://www.decolar.com/shop/flights/results/roundtrip/SAO/RIO/2025-09-08/2025-09-13/1/0/0?from=SB&di=1#showModal"

    # Configurações para evitar bloqueio
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # User-Agent de navegador real
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 30)

    # Fecha popups (cookies, anúncios, etc.)
    try:
        popup = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceitar')]"))
        )
        popup.click()
    except:
        pass

    # Espera os resultados carregarem
    try:
        resultados = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cluster-container"))
        )
        print(f"Encontrados {len(resultados)} voos")
        
        voos_extraidos = []
        for voo in resultados[:5]:  # pega só os 5 primeiros
            print("-" * 50)
            print(voo.text)
            voos_extraidos.append(voo.text)
    except:
        print("Não foi possível capturar resultados.")

    with open("dados_extraidos.json", "w", encoding="utf-8") as a:
        json.dump(voos_extraidos, a, ensure_ascii=False, indent=4)

    html_content = driver.page_source
    with open("pagina.html", "w", encoding="utf-8") as f:
        f.write(html_content)
   
    time.sleep(5)
    driver.quit()

if __name__ == "__main__":
    buscar_voo()
