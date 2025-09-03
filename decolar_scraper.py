from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def buscar_voo():
    url = "https://www.decolar.com/shop/flights/results/roundtrip/SAO/RIO/2025-09-03/2025-09-09/1/0/0?from=SB&di=1#showModal"
    driver = webdriver.Chrome(service=ChromeService())
    driver.get(url)

    # Esperar pelo carregamento dos resultados
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".flight-result-class"))  # ajusta o seletor real
    )

    # Fechar possíveis pop-ups
    try:
        popup = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceitar')]"))
        )
        popup.click()
    except:
        pass

    # Capturar resultados
    voos = driver.find_elements(By.CSS_SELECTOR, ".flight-result-class")
    for voo in voos:
        print(voo.text)

    driver.quit()

if __name__ == "__main__":
    buscar_voo()
