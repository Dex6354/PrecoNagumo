import streamlit as st
import requests
from bs4 import BeautifulSoup

# Configuração da página
st.set_page_config(page_title="Busca de Produtos Nagumo", page_icon="🛒")

# CSS para remover o espaço superior
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem; /* diminua esse valor para reduzir ou coloque 0 para remover totalmente */
        }
    </style>
""", unsafe_allow_html=True)

# Título com fonte menor
st.markdown("<h5>🛒Preços Nagumo</h5>", unsafe_allow_html=True)

busca = st.text_input("Digite o nome do produto:")

def buscar_produto_nagumo(palavra_chave):
    palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
    url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}" 
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        search_words = set(palavra_chave.lower().split())
        
        # Procura por todos os contêineres de produto que parecem ser o bloco principal
        # Baseado nos exemplos fornecidos, a classe 'sc-c5cd0085-0' com 'fWmXTW' parece ser o contêiner de cada item.
        all_product_blocks = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

        for product_block in all_product_blocks:
            # Tenta encontrar o nome do produto dentro deste bloco
            nome_tag = product_block.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
            
            if nome_tag:
                nome_text = nome_tag.text.strip()
                product_words = set(nome_text.lower().split())
                
                # Verifica se as palavras da busca estão contidas no nome do produto encontrado
                if search_words.issubset(product_words):
                    # Se o nome corresponde, extrai as outras informações dentro do mesmo bloco
                    preco_tag = product_block.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
                    preco_text = preco_tag.text.strip() if preco_tag else "Preço não encontrado"
                    
                    descricao_tag = product_block.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
                    descricao_text = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"
                    
                    # Procura a tag <img> diretamente dentro deste bloco de produto
                    img_tag = product_block.find('img')
                    img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
                    
                    return nome_text, preco_text, descricao_text, img_url
        
        # Se nenhum produto correspondente for encontrado após iterar por todos os blocos
        return "Nome não encontrado", "Preço não encontrado", "Descrição não encontrada", None

    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao buscar produtos: {e}")
        return "Erro na busca", "", "", None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado durante a busca: {e}")
        return "Erro na busca", "", "", None

if busca:
    nome, preco, descricao, imagem_url = buscar_produto_nagumo(busca)
    st.write(f"**Produto:** {nome}")
    st.write(f"**Preço:** {preco}")
    st.write(f"**Descrição:** {descricao}")
    
    if imagem_url:
        st.image(imagem_url, caption=nome, width=200)
    elif nome != "Nome não encontrado" and nome != "Erro na busca": 
        st.write("Imagem não encontrada para este produto.")
    elif nome == "Nome não encontrado":
        st.write("Produto não encontrado.")
