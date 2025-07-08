from selenium import webdriver
from bs4 import BeautifulSoup

def buscar_produto_shibata_selenium(url):
    # Configurar o Selenium com Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Executar sem abrir o navegador
    driver = webdriver.Chrome(options=options)
    
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Buscar nome, preço e imagem como no exemplo anterior
    title_tag = soup.find("title")
    nome = title_tag.text.strip() if title_tag else "Nome não encontrado"
    
    preco_span = soup.find('span', class_='sc-c5cd0085-9')
    preco = preco_span.text.strip() if preco_span else "Preço não encontrado"
    
    imagem_tag = soup.find('img', class_='sc-c5cd0085-2')
    imagem_url = imagem_tag['src'] if imagem_tag and 'src' in imagem_tag.attrs else "Imagem não encontrada"

    return nome, preco, imagem_url

# URL de teste
url_shibata = "https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/banana"

nome, preco, imagem_url = buscar_produto_shibata_selenium(url_shibata)
print(f"🛍️ Produto: {nome}")
print(f"💰 Preço: {preco}")
print(f"🖼️ Imagem: {imagem_url}")
