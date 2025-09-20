from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
import csv
from datetime import datetime
destinos = ["REC"]
# destinos = ["REC", "POA", "FOR", "RIO", "MCZ", "BUE", "ROM", "LON", "MVD", "LIM"]

def buscar_voo(origem, destino, data_ida, data_volta):
    """
    Busca voos na Decolar.com para uma rota e datas especificadas.

    Args:
        origem (str): Código IATA do aeroporto de origem (ex: 'SAO').
        destino (str): Código IATA do aeroporto de destino (ex: 'RIO').
        data_ida (str): Data de ida no formato 'YYYY-MM-DD' (ex: '2025-09-08').
        data_volta (str): Data de volta no formato 'YYYY-MM-DD' (ex: '2025-09-13').
    """
    
    # URL reconstruída para ser idêntica à original
    url = (
        f"https://www.decolar.com/shop/flights/results/roundtrip/"
        f"{origem}/{destino}/{data_ida}/{data_volta}/1/0/0?from=SB&di=1#showModal"
    )
    
    print(f"Buscando voos em: {url}") # Adicionado para verificar a URL

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 60)

    try:
        try:
            popup = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceitar')]")))
            popup.click()
            print("Popup de cookies fechado.")
        except TimeoutException:
            print("Nenhum popup de cookies encontrado.")

        time.sleep(5)

        resultados = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cluster-container"))
        )

        
        voos_extraidos = []
        if resultados:
            print(f"Encontrados {len(resultados)} voos.")
            for voo in resultados[:5]:
                texto_voo = voo.text
                voos_extraidos.append(texto_voo)
                print("-" * 50)
                print(texto_voo)
        else:
            print("Nenhum voo encontrado no seletor.")

        if voos_extraidos:
        #     nome_arquivo_json = f"voos_{origem}_para_{destino}.json"
        #     with open(nome_arquivo_json, "w", encoding="utf-8") as f:
        #         json.dump(voos_extraidos, f, ensure_ascii=False, indent=4)
        #     print(f"\nDados salvos em {nome_arquivo_json}")
            # sigla_destino = voo.find_element(By.CSS_SELECTOR, ".different-airport").text.strip()
            # print(f"Aeroporto: {sigla_destino}")
            # cidade_destino = voo.find_element(By.CSS_SELECTOR, ".route-info-item-city-arrival span").text.strip()
            # print(f"Cidade: {cidade_destino}")
            # companhia_elem = voo.find_element(By.CSS_SELECTOR, "airline-logo img")
            # companhia = companhia_elem.get_attribute("alt").strip() if companhia_elem else "N/A"
            # print(f"Companhia: {companhia}")
            # texto_voo = voo.text.lower()
            # leave_elems = voo.find_elements(By.CSS_SELECTOR, "itinerary-element.leave .hour")
            # hora_ida = leave_elems[0].text.strip() if leave_elems else "N/A"

            # # Horário de volta
            # arrive_elems = voo.find_elements(By.CSS_SELECTOR, "itinerary-element.arrive .hour")
            # hora_volta = arrive_elems[0].text.strip() if arrive_elems else "N/A"


            # print(f"Hora Ida: {hora_ida} | Hora Volta: {hora_volta}")
            #  # Detecta escala
            # if "direto" in texto_voo:
            #     escala = "Direto"
            # elif "escala" in texto_voo:
            #     import re
            #     match = re.search(r"(\d+)\s+escala", texto_voo)
            #     escala = f"{match.group(1)} escala(s)" if match else "Escala"
            # else:
            #     escala = "N/A"

            # print("Escala:", escala)

            # precos = voo.find_elements(By.CSS_SELECTOR, ".amount.price-amount")
            # preco_por_adulto = precos[0].text if len(precos) > 0 else "N/A"
            # total_adultos = precos[1].text if len(precos) > 1 else "N/A"
            # taxas = precos[2].text if len(precos) > 2 else "N/A"
            # preco_final = precos[3].text if len(precos) > 3 else "N/A"
            # print(f"Preço por adulto: {preco_por_adulto}, Total adultos: {total_adultos}, Taxas: {taxas}, Preço final: {preco_final}")
           
            # nome_arquivo_csv = f"voos_{origem}_para_{destino}.csv"
            with open('passagens.csv', "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                #writer.writeheader()
                writer.writerow(["Dados do Voo"])
                for voo in voos_extraidos:
                    writer.writerow([voo])
                    #writer.writerow({"ida": voo[2]})
            print(f"Dados salvos em passagens.csv")
        else:
            print("Nenhum dado para salvar. Arquivos JSON e CSV não foram criados.")

    except TimeoutException:
        print("Timeout: Não foi possível capturar os resultados dentro do tempo limite.")
        print("Verifique se a URL está correta ou se os seletores CSS mudaram.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        html_content = driver.page_source
        nome_pagina_html = f"pagina_{origem}_para_{destino}.html"
        with open(nome_pagina_html, "a", encoding="utf-8") as f:
            f.write(html_content)
        
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    data_hora_atual = datetime.now()
    print("Data e hora atuais:", data_hora_atual)
    for destino in destinos:
        buscar_voo("SAO", destino, "2025-12-22", "2025-12-29") 
        #buscar_voo("SAO", destino, "2025-12-29", "2026-01-05") 