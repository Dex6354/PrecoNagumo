import streamlit as st
import requests
from bs4 import BeautifulSoup

# Configuração da página
st.set_page_config(page_title="Busca de Produtos Nagumo", page_icon="🛒")

# CSS para remover o espaço superior
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

# Título com fonte menor
st.markdown("<h5>🛒Preços Nagumo</h5>", unsafe_allow_html=True)

busca = st.text_input("Digite o nome do produto:")

def buscar_produto_nagumo(palavra_chave):
    palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
    url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
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
                    
                    # Imagem: Find the container with the image
                    imagem_container = container.find('div', class_='sc-c5cd0085-2')
                    if imagem_container:
                        # Try to find the <img> in the <noscript> tag
                        noscript_tag = imagem_container.find('noscript')
                        if noscript_tag:
                            # Parse the <noscript> content as HTML
                            noscript_soup = BeautifulSoup(noscript_tag.text, 'html.parser')
                            imagem_tag = noscript_soup.find('img')
                            imagem_url = imagem_tag.get('src', 'Imagem não encontrada') if imagem_tag else 'Imagem não encontrada'
                        else:
                            # Fallback to main <img> tag
                            imagem_tag = imagem_container.find('img')
                            imagem_url = imagem_tag.get('src', '') if imagem_tag else 'Imagem não encontrada'
                            if imagem_url.startswith('data:image'):
                                imagem_url = imagem_tag.get('data-src', 'Imagem não encontrada')
                        if not imagem_url or imagem_url == 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7':
                            imagem_url = 'Imagem não encontrada'
                    else:
                        imagem_url = 'Imagem não encontrada'
                    
                    return nome_text, preco_text, descricao_text, imagem_url
        return "Nome não encontrado", "Preço não encontrado", "Descrição não encontrada", "Imagem não encontrada"

    except Exception as e:
        print(f"Erro na busca: {e}")
        return "Erro na busca", "Preço não encontrado", "Descrição não encontrada", "Imagem não encontrada"

if busca:
    nome, preco, descricao, imagem_url = buscar_produto_nagumo(busca)
    st.write(f"**Produto:** {nome}")
    st.write(f"**Preço:** {preco}")
    st.write(f"**Descrição:** {descricao}")
    if imagem_url != "Imagem não encontrada":
        st.image(imagem_url, caption="Imagem do produto", width=300)
    else:
        st.write("🖼️ **Imagem não encontrada**")
