import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Busca Imagem Nagumo", page_icon="🛒")
st.markdown("<h5>🛒 Buscar Imagem Produto</h5>", unsafe_allow_html=True)

busca = st.text_input("Digite o nome do produto:")

def buscar_imagem(palavra_chave):
    palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
    url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        produtos = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

        for produto in produtos:
            img_tag = produto.find('img')
            if img_tag and img_tag.has_attr('alt') and palavra_chave.lower() in img_tag['alt'].lower():
                return img_tag['src']
        
        return None

    except Exception as e:
        return f"Erro: {e}"

if busca:
    imagem_url = buscar_imagem(busca)
    if imagem_url:
        st.write(f"**Imagem encontrada:** {imagem_url}")
    else:
        st.write("Imagem não encontrada.")
