import requests
from bs4 import BeautifulSoup

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

        # Buscar nome do produto
        # O nome do produto em uma página de item geralmente está em um <h1> ou <span> específico
        nome_tag = soup.find('span', class_='sc-fLlhyt fvrgXC sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
        if not nome_tag: # Fallback para h1 se a span não for encontrada
            nome_tag = soup.find('h1')
        nome_text = nome_tag.text.strip() if nome_tag else "Nome não encontrado"

        # Buscar o preço
        preco_text = "Preço não encontrado"
        # A classe 'sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV' é do preço
        preco_span = soup.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
        if preco_span:
            preco_text = preco_span.text.strip()
        else: # Fallback para busca genérica de spans se a classe específica não for encontrada
            spans = soup.find_all('span')
            for span in spans:
                texto = span.get_text(strip=True)
                if texto.startswith('R$') and texto != 'R$ 0,00':
                    preco_text = texto
                    break
        
        # Buscar a URL da imagem do produto
        img_url = None
        # A div que contém a imagem principal do produto parece ter a classe 'sc-c5cd0085-2'
        image_container_div = soup.find('div', class_='sc-bczRLJ sc-f719e9b0-0 sc-c5cd0085-2 hJJyHP dbeope eKZaNO')
        if image_container_div:
            img_tag = image_container_div.find('img')
            if img_tag and 'src' in img_tag.attrs:
                img_url = img_tag['src']

        return nome_text, preco_text, img_url # Retorna também a URL da imagem

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
        
        # A API do Shibata não fornece a URL da imagem diretamente no JSON de detalhes do produto
        # no exemplo fornecido. Se ela fornecesse, seria adicionada aqui.
        imagem_url = None # Placeholder, pois a API não forneceu no exemplo

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
    # Se a API do Shibata retornasse a imagem, você poderia imprimir aqui:
    # print(f"  🖼️ Imagem URL: {shibata_info['imagem_url']}")
else:
    print(f"\n🟥 Shibata: {shibata_info['erro']}")
