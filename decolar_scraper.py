import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import os
from datetime import datetime

destinos = ["RIO", "MCZ", "BUE", "ROM", "LON", "MVD", "LIM"]
#destinos = ["REC", "POA", "FOR", "RIO", "MCZ", "BUE", "ROM", "LON", "MVD", "LIM"]

def buscar_voo(origem, destino, data_ida, data_volta):
    """
    Busca voos na Decolar.com para uma rota e datas especificadas e salva em CSV.

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
    
    print(f"Buscando voos em: {url}")

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
            # Tenta fechar o popup de cookies
            # popup = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceitar')]")))
            popup = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Agora não')]")))
            popup.click()
            print("Popup de cookies fechado.")
        except TimeoutException:
            print("Nenhum popup de cookies encontrado.")

        # Espera um pouco para a página carregar
        time.sleep(5)

        # Encontra todos os elementos de voo na página
        resultados = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cluster-container"))
        )
        
        voos_dados = []
        if resultados:
            print(f"Encontrados {len(resultados)} voos.")
            for voo in resultados[:5]: # Limita a 5 resultados para teste
                dados_voo = {}
                texto_voo = voo.text.lower()
                
                # Extração de preços
                try:
                    precos = voo.find_elements(By.CSS_SELECTOR, ".amount.price-amount")

                     # AGORA basta verificar se existe pelo menos 1 preço
                    if len(precos) >= 1:
                        preco_final = precos[0].text.strip()
                        dados_voo["Preco_Por_Adulto"] = "N/A"   # não existe mais no HTML
                        dados_voo["Total_Adultos"] = "N/A"      # não existe mais
                        dados_voo["Taxas"] = "N/A"              # não existe mais
                        dados_voo["Preco_Final"] = preco_final  # único valor válido

                    else:
                        print("Aviso: Nenhum preço foi encontrado.")
                        dados_voo["Preco_Por_Adulto"] = "N/A"
                        dados_voo["Total_Adultos"] = "N/A"
                        dados_voo["Taxas"] = "N/A"
                        dados_voo["Preco_Final"] = "N/A"
                except NoSuchElementException:
                    dados_voo["Preco_Por_Adulto"] = "N/A"
                    dados_voo["Total_Adultos"] = "N/A"
                    dados_voo["Taxas"] = "N/A"
                    dados_voo["Preco_Final"] = "N/A"
                    print("Erro: Preços não encontrados.")


                try:
                    companhia_elem = voo.find_element(By.CSS_SELECTOR, "airline-logo img")
                    dados_voo["Companhia_Aerea"] = companhia_elem.get_attribute("alt").strip()
                except NoSuchElementException:
                    dados_voo["Companhia_Aerea"] = "N/A"
                    print("Erro: Companhia Aérea não encontrada.")
                
                # Lógica de detecção de Escalas baseada em texto
                if "direto" in texto_voo:
                    dados_voo["Escalas"] = "Direto"
                elif "escala" in texto_voo:
                    match = re.search(r"(\d+)\s+escala", texto_voo)
                    dados_voo["Escalas"] = f"{match.group(1)} escala(s)" if match else "Escala"
                else:
                    dados_voo["Escalas"] = "N/A"
                
                try:
                    hora_ida_elem = voo.find_element(By.CSS_SELECTOR, "itinerary-element.leave .hour")
                    dados_voo["Hora_Ida"] = hora_ida_elem.text.strip()
                except NoSuchElementException:
                    dados_voo["Hora_Ida"] = "N/A"
                    print("Erro: Hora de ida não encontrada.")

                try:
                    hora_volta_elem = voo.find_element(By.CSS_SELECTOR, "itinerary-element.arrive .hour")
                    dados_voo["Hora_Volta"] = hora_volta_elem.text.strip()
                except NoSuchElementException:
                    dados_voo["Hora_Volta"] = "N/A"
                    print("Erro: Hora de volta não encontrada.")

                # Extração das siglas dos aeroportos de ida e volta
                # Extração das siglas dos aeroportos de ida e volta
                try:
                    aeroportos_elem = voo.find_elements(By.CSS_SELECTOR, 'span[tooltip-id="popup-airport"]')
                    
                    if len(aeroportos_elem) >= 2:
                        dados_voo["Aeroporto_Ida"] = aeroportos_elem[0].text.strip()
                        dados_voo["Aeroporto_Destino"] = aeroportos_elem[1].text.strip()
                    else:
                        dados_voo["Aeroporto_Ida"] = "N/A"
                        dados_voo["Aeroporto_Destino"] = "N/A"
                        print("Aviso: Não foram encontrados 2 aeroportos para esta opção de voo.")
                except NoSuchElementException:
                    dados_voo["Aeroporto_Ida"] = "N/A"
                    dados_voo["Aeroporto_Destino"] = "N/A"
                    print("Erro: Aeroportos não encontrados.")

                
                # Adiciona as informações fixas da busca
                dados_voo["Origem"] = origem
                dados_voo["Destino"] = destino
                dados_voo["Data_Ida"] = data_ida
                dados_voo["Data_Volta"] = data_volta
                dados_voo["Data_Extracao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print("-" * 50)
                print(f"Dados extraídos: {dados_voo}")

                voos_dados.append(dados_voo)
        
        else:
            print("Nenhum voo encontrado no seletor.")

        if voos_dados:
            nome_arquivo_csv = "passagens.csv"
            # Nomes das colunas fixos para evitar erros
            fieldnames = ["Preco_Por_Adulto", "Total_Adultos", "Taxas", "Preco_Final", "Companhia_Aerea", "Escalas", "Hora_Ida", "Hora_Volta", "Aeroporto_Ida", "Aeroporto_Destino", "Origem", "Destino", "Data_Ida", "Data_Volta", "Data_Extracao"]

            with open(nome_arquivo_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not os.path.isfile(nome_arquivo_csv) or os.stat(nome_arquivo_csv).st_size == 0:
                    writer.writeheader()
                writer.writerows(voos_dados)
            
            print(f"Dados estruturados salvos em {nome_arquivo_csv}")
        else:
            print("Nenhum dado para salvar. O arquivo CSV não foi atualizado.")

    except TimeoutException:
        print("Timeout: Não foi possível capturar os resultados dentro do tempo limite.")
        print("Verifique se a URL está correta ou se os seletores CSS mudaram.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        # Bloco finally para garantir que o HTML seja salvo e o navegador seja fechado
        html_content = driver.page_source
        nome_pagina_html = f"pagina_{origem}_para_{destino}.html"
        with open(nome_pagina_html, "a", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Página HTML salva em {nome_pagina_html}")
        driver.quit()

if __name__ == "__main__":
    data_hora_atual = datetime.now()
    print("Iniciando a busca de voos. Data e hora atuais:", data_hora_atual)
    for destino in destinos:
        buscar_voo("SAO", destino, "2025-12-22", "2025-12-29")
        buscar_voo("SAO", destino, "2025-12-29", "2026-01-05") 
        time.sleep(10) # Pausa entre as buscas para evitar ser bloqueado
