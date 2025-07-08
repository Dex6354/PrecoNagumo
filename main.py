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

# Renomeada a função para ser mais consistente com o site Nagumo
def buscar_produto_nagumo(palavra_chave):
    palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
    url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}" 
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        search_words = set(palavra_chave.lower().split())
        
        # Encontra todos os blocos de produtos usando a classe principal que você forneceu
        # Ex: <div aria-label="Banana Prata" class="sc-c5cd0085-0 fWmXTW">
        all_product_blocks = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

        for product_block in all_product_blocks:
            nome_text = "Nome não encontrado"
            preco_text = "Preço não encontrado"
            descricao_text = "Descrição não encontrada"
            img_url = None
            
            # Tenta encontrar a tag <img> dentro deste bloco de produto
            img_tag = product_block.find('img') 

            # Verifica se a tag <img> existe e se o atributo 'alt' corresponde à palavra-chave
            if img_tag and 'alt' in img_tag.attrs:
                img_alt_text = img_tag['alt'].strip()
                img_alt_words = set(img_alt_text.lower().split())
                
                # Se as palavras da busca estão contidas no 'alt' da imagem, consideramos que encontramos o produto
                if search_words.issubset(img_alt_words):
                    nome_text = img_alt_text # Usa o texto do alt como o nome principal do produto
                    
                    # Pega a URL da imagem diretamente do atributo 'src'
                    img_url = img_tag.get('src')
                    
                    # Extrai o preço e a descrição do mesmo bloco do produto
                    # Classe do nome do produto (span)
                    name_span = product_block.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
                    if name_span:
                        # Se o nome do span for mais detalhado que o alt, use-o
                        if len(name_span.text.strip()) > len(nome_text):
                            nome_text = name_span.text.strip()

                    # Classe do preço
                    preco_span = product_block.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
                    preco_text = preco_span.text.strip() if preco_span else "Preço não encontrado"
                    
                    # Classe da descrição
                    descricao_span = product_block.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
                    descricao_text = descricao_span.text.strip() if descricao_span else "Descrição não encontrada"
                    
                    # Retorna todas as informações encontradas para o primeiro produto correspondente
                    return nome_text, preco_text, descricao_text, img_url
        
        # Se nenhum produto correspondente for encontrado após iterar por todos os blocos
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
