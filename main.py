import streamlit as st
import requests
from bs4 import BeautifulSoup

# Configuração da página
st.set_page_config(page_title="Busca de Produtos Nagumo", page_icon="🛒")

# CSS para remover o espaço superior e rodapé
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
        }
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Título com fonte menor
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
        product_containers = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

        for container in product_containers:
            nome_tag = container.find('h1') or container.find('span')
            if nome_tag:
                nome_text = nome_tag.text.strip()
                product_words = set(nome_text.lower().split())
                if search_words.intersection(product_words):
                    preco_tag = container.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
                    preco_text = preco_tag.text.strip() if preco_tag else "Preço não encontrado"

                    descricao_tag = container.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
                    descricao_text = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"

                    # Procura no <noscript> pela imagem real
                    noscript_tag = container.find('noscript')
                    imagem_url = "Imagem não encontrada"
                    if noscript_tag:
                        nosoup = BeautifulSoup(noscript_tag.decode_contents(), 'html.parser')
                        img_tag = nosoup.find('img')
                        if img_tag and img_tag.get('src'):
                            imagem_url = img_tag['src']

                    return nome_text, preco_text, descricao_text, imagem_url

        return "Nome não encontrado", "Preço não encontrado", "Descrição não encontrada", "Imagem não encontrada"

    except Exception as e:
        return "Erro na busca", "", "", str(e)

if busca:
    nome, preco, descricao, imagem = buscar_produto_nagumo(busca)
    st.write(f"**Produto:** {nome}")
    st.write(f"**Preço:** {preco}")
    st.write(f"**Descrição:** {descricao}")
    if imagem != "Imagem não encontrada":
        st.image(imagem, width=200)
    else:
        st.write(f"**Imagem:** {imagem}")
