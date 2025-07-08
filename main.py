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
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        search_words = set(palavra_chave.lower().split())
        
        found_img_tag = None
        
        # Itera por todas as tags <img> na página para encontrar a que tem o 'alt' correspondente
        for img_tag in soup.find_all('img'):
            if 'alt' in img_tag.attrs:
                img_alt_text = img_tag['alt'].strip().lower()
                # Verifica se todas as palavras da busca estão no texto 'alt' da imagem
                if all(word in img_alt_text for word in search_words):
                    found_img_tag = img_tag
                    break # Encontrou a imagem mais relevante, para de buscar

        if found_img_tag:
            img_url = found_img_tag.get('src')
            nome_text = found_img_tag.get('alt', "Nome não encontrado").strip() # Usa o alt como nome

            # Agora, tenta encontrar o bloco pai do produto para pegar preço e descrição
            # Isso assume que a tag <img> está dentro do bloco principal do produto
            product_block = found_img_tag.find_parent('div', class_='sc-c5cd0085-0 fWmXTW')

            if product_block:
                # Extrai preço e descrição do bloco do produto encontrado
                preco_tag = product_block.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
                preco_text = preco_tag.text.strip() if preco_tag else "Preço não encontrado"
                
                descricao_tag = product_block.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
                descricao_text = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"
                
                return nome_text, preco_text, descricao_text, img_url
            else:
                # Se o bloco do produto não for encontrado, retorna o que temos (URL da imagem e nome do alt)
                return nome_text, "Preço não encontrado", "Descrição não encontrada", img_url
        else:
            # Se nenhuma tag <img> com 'alt' correspondente for encontrada
            return "Nome não encontrado", "Preço não encontrado", "Descrição não encontrada", None

    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao buscar produtos: {e}")
        return "Erro na busca", "", "", None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado durante a busca: {e}")
        return "Erro na busca", "", "", None

# Exibição do Resultado no Streamlit
if busca:
    nome, preco, descricao, imagem_url = buscar_produto_nagumo(busca)
    
    st.write(f"**Produto:** {nome}")
    st.write(f"**Preço:** {preco}")
    st.write(f"**Descrição:** {descricao}")
    
    # Exibe a URL da imagem por escrito, como solicitado, para verificação
    st.write(f"**URL da Imagem:** {imagem_url if imagem_url else 'Não encontrada'}")

    # Só tenta exibir a imagem se a URL foi realmente encontrada
    if imagem_url:
        st.image(imagem_url, caption=nome, width=200)
    elif nome != "Nome não encontrado" and nome != "Erro na busca":
        # Mensagem opcional se o produto foi encontrado, mas a imagem não
        st.write("Imagem não encontrada para este produto.")
    
    if nome == "Nome não encontrado":
        st.write("Produto não encontrado.")
