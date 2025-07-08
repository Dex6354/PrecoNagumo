import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Busca de Produtos Nagumo", page_icon="🛒")

st.markdown("<h3>🛒 Buscador de Preços Nagumo</h3>", unsafe_allow_html=True)

busca = st.text_input("Digite o nome do produto:")

def buscar_produto_nagumo(palavra_chave):
    palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
    url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        search_words = set(palavra_chave.lower().split())
        product_containers = soup.find_all('div', class_='sc-bczRLJ sc-f719e9b0-0 sc-c5cd0085-5 hJJyHP dbeope kekHxB')

        for container in product_containers:
            nome_tag = container.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
            if nome_tag:
                nome_text = nome_tag.text.strip()
                product_words = set(nome_text.lower().split())
                if search_words.issubset(product_words):
                    preco_tag = container.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
                    preco_text = preco_tag.text.strip() if preco_tag else "Preço não encontrado"
                    descricao_tag = container.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
                    descricao_text = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"
                    return nome_text, preco_text, descricao_text
        return "Nome não encontrado", "Preço não encontrado", "Descrição não encontrada"

    except:
        return "Erro na busca", "", ""

if busca:
    nome, preco, descricao = buscar_produto_nagumo(busca)
    st.write(f"**Produto:** {nome}")
    st.write(f"**Preço:** {preco}")
    st.write(f"**Descrição:** {descricao}")
