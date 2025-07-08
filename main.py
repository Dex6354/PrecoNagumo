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
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        search_words = set(palavra_chave.lower().split())
        
        # Procura por todos os contêineres de produto que parecem ser o bloco principal
        # Ex: <div aria-label="Banana Prata" class="sc-c5cd0085-0 fWmXTW">
        all_product_blocks = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

        for product_block in all_product_blocks:
            nome_text = "Nome não encontrado"
            preco_text = "Preço não encontrado"
            descricao_text = "Descrição não encontrada"
            img_url = None
            product_identified = False

            # Tenta identificar o produto pelo 'alt' da imagem primeiro
            img_tag = product_block.find('img')
            if img_tag and 'alt' in img_tag.attrs:
                img_alt_text = img_tag['alt'].strip()
                img_alt_words = set(img_alt_text.lower().split())
                if search_words.issubset(img_alt_words):
                    nome_text = img_alt_text
                    product_identified = True
            
            # Se não identificado pela imagem, tenta pelo span de nome
            if not product_identified:
                nome_tag = product_block.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
                if nome_tag:
                    span_name_text = nome_tag.text.strip()
                    span_name_words = set(span_name_text.lower().split())
                    if search_words.issubset(span_name_words):
                        nome_text = span_name_text
                        product_identified = True

            # Se o produto foi identificado por qualquer um dos métodos
            if product_identified:
                # Extrai preço e descrição
                preco_tag = product_block.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
                preco_text = preco_tag.text.strip() if preco_tag else "Preço não encontrado"
                
                descricao_tag = product_block.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
                descricao_text = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"
                
                # --- Lógica para encontrar a URL da imagem exatamente como está no 'src' ---
                # Procura a tag <img> dentro do bloco do produto (já buscada acima)
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src'] # Pega o 'src' diretamente, sem edições
                
                return nome_text, preco_text, descricao_text, img_url
        
        # Se nenhum produto correspondente for encontrado
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
    
    # Verifica se img_url tem um valor antes de tentar exibir a imagem
    if img_url:
        st.image(img_url, caption=nome, width=200)
    else:
        # Mensagem opcional se a imagem não for encontrada, mas o produto sim
        if nome != "Nome não encontrado" and nome != "Erro na busca":
            st.write("Imagem não encontrada para este produto.")
    
    if nome == "Nome não encontrado":
        st.write("Produto não encontrado.")
