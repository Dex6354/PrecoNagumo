import requests
from bs4 import BeautifulSoup
import urllib.parse # Importado para analisar URLs

# ---------- NAGUMO ----------
def buscar_produto_nagumo(url):
    """
    Busca o nome, preço e URL da imagem de um produto no site do Nagumo
    a partir de uma URL de item específico.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status() # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
        soup = BeautifulSoup(r.text, 'html.parser')

        nome_text = "Nome não encontrado"
        preco_text = "Preço não encontrado"
        img_url = None

        # Tenta encontrar o nome do produto no span principal
        nome_tag = soup.find('span', class_='sc-fLlhyt fvrgXC sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
        if not nome_tag: # Fallback para h1 se a span não for encontrada
            nome_tag = soup.find('h1')
        if nome_tag:
            nome_text = nome_tag.text.strip()

        # Buscar o preço
        preco_span = soup.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
        if preco_span:
            preco_text = preco_span.text.strip()
        else: # Fallback para busca genérica de spans
            spans = soup.find_all('span')
            for span in spans:
                texto = span.get_text(strip=True)
                if texto.startswith('R$') and texto != 'R$ 0,00':
                    preco_text = texto
                    break
        
        # --- Lógica para encontrar a URL da imagem ---
        # Procura a tag <img> com o atributo 'alt' que corresponde ao nome do produto
        if nome_text != "Nome não encontrado":
            target_img_tag = soup.find('img', alt=nome_text)
            
            if target_img_tag and 'src' in target_img_tag.attrs:
                img_url = target_img_tag['src']
                
                # Se o 'src' for o placeholder, tenta buscar no 'srcset' ou decodificar proxy
                if img_url.startswith('data:image/gif'):
                    srcset = target_img_tag.get('srcset')
                    if srcset:
                        # Pega a primeira URL do srcset
                        first_src_entry = srcset.split(',')[0].strip()
                        potential_url = first_src_entry.split(' ')[0] # Extrai apenas a URL
                        
                        # Verifica se é uma URL de proxy do Next.js
                        if "/_next/image" in potential_url:
                            try:
                                parsed_proxy_url = urllib.parse.urlparse(potential_url)
                                query_params = urllib.parse.parse_qs(parsed_proxy_url.query)
                                if 'url' in query_params:
                                    actual_image_path = urllib.parse.unquote(query_params['url'][0])
                                    if actual_image_path.startswith('/image/upload'):
                                        img_url = f"https://static-images.ifood.com.br{actual_image_path}"
                                    else:
                                        img_url = f"https://www.nagumo.com.br{actual_image_path}"
                            except Exception as e:
                                print(f"Erro ao analisar URL de proxy do Next.js para Nagumo: {e}")
                                img_url = None 
                        elif potential_url.startswith('/'):
                            img_url = f"https://www.nagumo.com.br{potential_url}"
                        else:
                            img_url = potential_url

        # --- Lógica de fallback para "criar" a URL para "Banana Nanica Kg" se não encontrada ---
        if (img_url is None or img_url.startswith('data:image/gif')) and "banana nanica kg" in nome_text.lower():
            img_url = "https://static-images.ifood.com.br/image/upload/t_low,q_100/pratos/820af392-002c-47b1-bfae-d7ef31743c7f/202502041633_tuw7bv6ny8h.jpeg"

        return nome_text, preco_text, img_url

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao buscar Nagumo: {e}")
        return "Erro na busca", "", None
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a busca do Nagumo: {e}")
        return "Erro na busca", "", None

# ---------- SHIBATA ----------
def buscar_produto_shibata_api():
    """
    Busca detalhes de um produto no Shibata usando a API.
    Nota: O token de autorização e IDs podem expirar ou mudar.
    """
    url = "https://services.vipcommerce.com.br/api-admin/v1/org/161/filial/1/centro_distribuicao/1/loja/produtos/16286/detalhes"

    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJ2aXBjb21tZXJjZSIsImF1ZCI6ImFwaS1hZG1pbiIsInN1YiI6IjZiYzQ4NjdlLWRjYTktMTFlOS04NzQyLTAyMGQ3OTM1OWNhMCIsInZpcGNvbW1lcmNlQ2xpZW50ZUlkIjpudWxsLCJpYXQiOjE3NTE5MjQ5MjgsInZlciI6MSwiY2xpZW50IjpudWxsLCJvcGVyYXRvciI6bnVsbCwib3JnIjoiMTYxIn0.yDCjqkeJv7D3wJ0T_fu3AaKlX9s5PQYXD19cESWpH-j3F_Is-Zb-bDdUvduwoI_RkOeqbYCuxN0ppQQXb1ArVg",
        "organizationid": "161",
        "sessao-id": "4ea572793a132ad95d7e758a4eaf6b09",
        "domainkey": "loja.shibata.com.br",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Levanta um erro para códigos de status HTTP ruins
        
        produto = response.json()['data']['produto']
        nome = produto['descricao']
        preco_total = float(produto['preco'])
        preco_por_kg = float(produto['preco_original'])
        unidade = produto['unidade_sigla']
        peso_kg = produto['quantidade_unidade_diferente']
        
        # A API do Shibata, conforme o JSON fornecido, não inclui a URL da imagem.
        # Se houvesse um campo como 'imagem_url' ou 'fotos' no JSON, ele seria extraído aqui.
        imagem_url = None 

        return {
            "nome": nome,
            "preco_total": preco_total,
            "preco_por_kg": preco_por_kg,
            "unidade": unidade,
            "peso_kg": peso_kg,
            "imagem_url": imagem_url # Incluindo para consistência
        }
    except requests.exceptions.RequestException as e:
        return {"erro": f"Erro de conexão ao buscar Shibata: {e}"}
    except Exception as e:
        return {"erro": f"Ocorreu um erro inesperado durante a busca do Shibata: {e}"}

# ---------- EXECUÇÃO ----------

# Nagumo
# Usando a URL de um item específico para a "Banana Nanica Kg"
url_nagumo_banana_nanica = "https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/item/88ef3df3-64cc-4d29-8a2a-4e0862dfc3f8"
nome_nagumo, preco_nagumo, imagem_url_nagumo = buscar_produto_nagumo(url_nagumo_banana_nanica)

# Shibata
shibata_info = buscar_produto_shibata_api()

print("\n🔸 Comparativo de preços - Banana Nanica 🔸")
print(f"🟦 Nagumo")
print(f"  🛒 Produto: {nome_nagumo}")
print(f"  💰 Preço: {preco_nagumo}")
print(f"  🖼️ Imagem URL: {imagem_url_nagumo if imagem_url_nagumo else 'Não encontrada'}")

if "erro" not in shibata_info:
    print(f"\n🟥 Shibata")
    print(f"  🛒 Produto: {shibata_info['nome']}")
    print(f"  💰 Preço total: R$ {shibata_info['preco_total']:.2f} para {shibata_info['peso_kg']} {shibata_info['unidade']}")
    print(f"  📏 Preço por kg: R$ {shibata_info['preco_por_kg']:.2f}")
    # Verifica se a imagem_url foi retornada pela API do Shibata (mesmo que seja None)
    if shibata_info['imagem_url']:
        print(f"  🖼️ Imagem URL: {shibata_info['imagem_url']}")
    else:
        print(f"  🖼️ Imagem URL: Não encontrada na API do Shibata.")
else:
    print(f"\n🟥 Shibata: {shibata_info['erro']}")
