import streamlit as st
import requests
from bs4 import BeautifulSoup

# Configuração da página
st.set_page_config(page_title="Busca de Produtos Nagumo", page_icon="🛒")

# Remover espaço superior
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

# Título menor
st.markdown("<h5>🛒 Preços Nagumo</h5>", unsafe_allow_html=True)

busca = st.text_input("Digite o nome do produto:")

def buscar_produto_nagumo(palavra_chave):
    palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
    url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        search_words = set(palavra_chave.lower().split())
        produtos = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

        for produto in produtos:
            # Nome
            nome_tag = produto.find('span', class_='sc-evZas fvrgXC sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
            if nome_tag:
                nome_text = nome_tag.text.strip()
                product_words = set(nome_text.lower().split())
                if search_words.issubset(product_words):
                    # Preço
                    preco_tag = produto.find('span', class_='sc-evZas hCYafM sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
                    preco_text = preco_tag.text.strip() if preco_tag else "Preço não encontrado"

                    # Descrição
                    descricao_tag = produto.find('span', class_='sc-evZas gzifyz sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
                    descricao_text = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"

                    # Imagem (correto agora)
                    imagem_tag = produto.find('img')
                    imagem_src = imagem_tag['src'] if imagem_tag and 'src' in imagem_tag.attrs else None

                    return nome_text, preco_text, descricao_text, imagem_src

        return "Nome não encontrado", "Preço não encontrado", "Descrição não encontrada", None

    except Exception as e:
        return f"Erro: {e}", "", "", None

if busca:
    nome, preco, descricao, imagem = buscar_produto_nagumo(busca)
    st.write(f"**Produto:** {nome}")
    st.write(f"**Preço:** {preco}")
    st.write(f"**Descrição:** {descricao}")
    if imagem:
        st.image(imagem, use_container_width=True)
        st.write(f"**Imagem URL:** {imagem}")
