import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse # Importa para analisar URLs

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
        
        found_product_info = {
            "nome": "Nome não encontrado",
            "preco": "Preço não encontrado",
            "descricao": "Descrição não encontrada",
            "imagem_url": None
        }
        
        # Encontra todos os blocos de produtos usando a classe principal
        all_product_blocks = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

        for product_block in all_product_blocks:
            img_tag = product_block.find('img') 
            
            if img_tag and 'alt' in img_tag.attrs:
                img_alt_text = img_tag['alt'].strip().lower()
                
                # Verifica se todas as palavras da busca estão no texto 'alt' da imagem
                if all(word in img_alt_text for word in search_words):
                    found_product_info["nome"] = img_tag.get('alt', "Nome não encontrado").strip()
                    
                    # --- Lógica para extrair a URL real da imagem ---
                    current_src = img_tag.get('src')
                    
                    # Prioriza o 'src' se não for o placeholder base64
                    if current_src and not current_src.startswith('data:image/gif'):
                        found_product_info["imagem_url"] = current_src
                    else:
                        # Se o 'src' for placeholder, tenta o 'srcset'
                        srcset = img_tag.get('srcset')
                        if srcset:
                            # Pega a primeira URL do srcset (ex: "url 1x, url2 2x")
                            first_src_entry = srcset.split(',')[0].strip()
                            potential_url = first_src_entry.split(' ')[0] # Extrai apenas a parte da URL
                            
                            # Verifica se é uma URL de proxy do Next.js (ex: /_next/image?url=...)
                            if "/_next/image" in potential_url:
                                try:
                                    parsed_proxy_url = urllib.parse.urlparse(potential_url)
                                    query_params = urllib.parse.parse_qs(parsed_proxy_url.query)
                                    
                                    if 'url' in query_params:
                                        actual_image_path = query_params['url'][0]
                                        actual_image_path_decoded = urllib.parse.unquote(actual_image_path)
                                        
                                        # Assume que imagens de produtos do iFood vêm de static-images.ifood.com.br
                                        if actual_image_path_decoded.startswith('/image/upload'):
                                            found_product_info["imagem_url"] = f"https://static-images.ifood.com.br{actual_image_path_decoded}"
                                        else:
                                            # Caso contrário, assume que é um caminho relativo ao domínio do Nagumo
                                            found_product_info["imagem_url"] = f"https://www.nagumo.com.br{actual_image_path_decoded}"
                                except Exception as e:
                                    print(f"Erro ao analisar URL de proxy do Next.js: {e}")
                                    found_product_info["imagem_url"] = None 
                            elif potential_url.startswith('/'):
                                # Se for uma URL relativa padrão, prefixa com o domínio do Nagumo
                                found_product_info["imagem_url"] = f"https://www.nagumo.com.br{potential_url}"
                            else:
                                found_product_info["imagem_url"] = potential_url # Assume que já é uma URL absoluta
                    
                    # Extrai preço e descrição do mesmo bloco do produto
                    preco_tag = product_block.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
                    found_product_info["preco"] = preco_tag.text.strip() if preco_tag else "Preço não encontrado"
                    
                    descricao_tag = product_block.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
                    found_product_info["descricao"] = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"
                    
                    return found_product_info["nome"], found_product_info["preco"], found_product_info["descricao"], found_product_info["imagem_url"]
        
        # Se nenhuma tag <img> com 'alt' correspondente for encontrada
        return found_product_info["nome"], found_product_info["preco"], found_product_info["descricao"], found_product_info["imagem_url"]

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
