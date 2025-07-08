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
        
        # Procura por todos os contêineres de produto usando o atributo aria-label
        # Ex: <div aria-label="Banana Prata" ...>
        all_product_blocks = soup.find_all('div', attrs={'aria-label': True})

        for product_block in all_product_blocks:
            aria_label_text = product_block['aria-label'].strip()
            aria_label_words = set(aria_label_text.lower().split())
            
            # Verifica se as palavras da busca estão contidas no aria-label
            if search_words.issubset(aria_label_words):
                # Se o aria-label corresponde, então este é o bloco do produto.
                # Agora, extraímos as informações e a URL da imagem.

                # Tenta encontrar o nome do produto no span, caso o aria-label não seja o nome de exibição completo
                nome_tag = product_block.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
                nome_text = nome_tag.text.strip() if nome_tag else aria_label_text # Prioriza span, senão usa aria-label

                preco_tag = product_block.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
                preco_text = preco_tag.text.strip() if preco_tag else "Preço não encontrado"
                
                descricao_tag = product_block.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
                descricao_text = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"
                
                # Procura a tag <img> diretamente dentro deste bloco de produto correspondente
                img_tag = product_block.find('img')
                img_url = img_tag.get('src') if img_tag else None # Pega o 'src' diretamente ou None
                
                # Para lidar com os placeholders do Next.js se o src for data:image/gif
                if img_url and img_url.startswith('data:image/gif'):
                    srcset = img_tag.get('srcset')
                    if srcset:
                        # Pega a primeira URL do srcset
                        first_src_entry = srcset.split(',')[0].strip()
                        potential_url = first_src_entry.split(' ')[0] # Extrai a URL
                        
                        # Se for um caminho relativo ou um proxy do Next.js
                        if potential_url.startswith('/'):
                            # Assumimos que o proxy do Next.js pode levar a imagens do ifood ou do próprio Nagumo
                            if '/_next/image?url=' in potential_url:
                                try:
                                    parsed_proxy_url = urllib.parse.urlparse(potential_url)
                                    query_params = urllib.parse.parse_qs(parsed_proxy_url.query)
                                    if 'url' in query_params:
                                        actual_image_path = urllib.parse.unquote(query_params['url'][0])
                                        if actual_image_path.startswith('/image/upload'):
                                            img_url = f"https://static-images.ifood.com.br{actual_image_path}"
                                        else:
                                            img_url = f"https://www.nagumo.com.br{actual_image_path}"
                                except Exception:
                                    img_url = None # Em caso de erro na análise do proxy
                            else:
                                img_url = f"https://www.nagumo.com.br{potential_url}"
                
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
    
    # Chama st.image diretamente. Se imagem_url for None ou inválida, não exibirá a imagem.
    st.image(imagem_url, caption=nome, width=200)
    
    if nome == "Nome não encontrado":
        st.write("Produto não encontrado.")
