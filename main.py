from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Configurações do Chrome sem abrir janela (headless)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Iniciar o navegador
driver = webdriver.Chrome(options=chrome_options)

# URL da busca
palavra_chave = "banana nanica"
palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}"

driver.get(url)

# Espera o JavaScript carregar (aumente se a internet for lenta)
time.sleep(5)

# Pega o HTML depois do carregamento
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Procura pela imagem real
imagens = soup.find_all('img')
for img in imagens:
    src = img.get('src', '')
    if 'ifood' in src or 'static-images' in src:
        print("Imagem encontrada:", src)
        break

driver.quit()
