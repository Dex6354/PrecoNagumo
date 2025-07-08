import requests
from bs4 import BeautifulSoup

def buscar_produto_nagumo(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        # Print part of the HTML for debugging (optional)
        print(response.text[:3000])  # Reduced to 3000 chars for brevity

        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar nome do produto
        title_tag = soup.find("title")
        nome = title_tag.text.strip() if title_tag else "Nome não encontrado"

        # Buscar o preço usando a classe do Streamlit code
        preco_span = soup.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
        preco = preco_span.text.strip() if preco_span else "Preço não encontrado"

        # Buscar a imagem usando a classe do Streamlit code
        imagem_tag = soup.find('img', class_='sc-c5cd0085-2')
        imagem_url = imagem_tag['src'] if imagem_tag and 'src' in imagem_tag.attrs else "Imagem não encontrada"

        return nome, preco, imagem_url
    except Exception as e:
        print(f"Erro na busca: {e}")
        return "Erro na busca", "Preço não encontrado", "Imagem não encontrada"

# URL de teste
url_nagumo = "https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/banana"

nome, preco, imagem_url = buscar_produto_nagumo(url_nagumo)
print(f"\n🛍️ Produto: {nome}")
print(f"💰 Preço: {preco}")
print(f"🖼️ Imagem: {imagem_url}")
