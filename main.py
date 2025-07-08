import requests
from bs4 import BeautifulSoup

# ---------- NAGUMO ----------
def buscar_produto_nagumo(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Nome do produto
    nome = soup.find('h1')
    nome_text = nome.text.strip() if nome else "Nome não encontrado"

    # Preço do produto
    preco_text = "Preço não encontrado"
    spans = soup.find_all('span')
    for span in spans:
        texto = span.get_text(strip=True)
        if texto.startswith('R$') and texto != 'R$ 0,00':
            preco_text = texto
            break

    # Imagem do produto
    imagem_url = "Imagem não encontrada"
    img_tag = soup.find('img', {'class': 'MuiCardMedia-root'})
    if img_tag and img_tag.get('src'):
        imagem_url = img_tag['src']

    return nome_text, preco_text, imagem_url

# ---------- SHIBATA ----------
def buscar_produto_shibata_api():
    url = "https://services.vipcommerce.com.br/api-admin/v1/org/161/filial/1/centro_distribuicao/1/loja/produtos/16286/detalhes"

    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJ2aXBjb21tZXJjZSIsImF1ZCI6ImFwaS1hZG1pbiIsInN1YiI6IjZiYzQ4NjdlLWRjYTktMTFlOS04NzQyLTAyMGQ3OTM1OWNhMCIsInZpcGNvbW1lcmNlQ2xpZW50ZUlkIjpudWxsLCJpYXQiOjE3NTE5MjQ5MjgsInZlciI6MSwiY2xpZW50IjpudWxsLCJvcGVyYXRvciI6bnVsbCwib3JnIjoiMTYxIn0.yDCjqkeJv7D3wJ0T_fu3AaKlX9s5PQYXD19cESWpH-j3F_Is-Zb-bDdUvduwoI_RkOeqbYCuxN0ppQQXb1ArVg",
        "organizationid": "161",
        "sessao-id": "4ea572793a132ad95d7e758a4eaf6b09",
        "domainkey": "loja.shibata.com.br",
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        produto = response.json()['data']['produto']
        nome = produto['descricao']
        preco_total = float(produto['preco'])
        preco_por_kg = float(produto['preco_original'])
        unidade = produto['unidade_sigla']
        peso_kg = produto['quantidade_unidade_diferente']

        return {
            "nome": nome,
            "preco_total": preco_total,
            "preco_por_kg": preco_por_kg,
            "unidade": unidade,
            "peso_kg": peso_kg
        }
    else:
        return {"erro": f"Erro {response.status_code}: {response.text}"}

# ---------- EXECUÇÃO ----------

# Nagumo
url_nagumo = "https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/item/88ef3df3-64cc-4d29-8a2a-4e0862dfc3f8"
nome_nagumo, preco_nagumo, imagem_nagumo = buscar_produto_nagumo(url_nagumo)

# Shibata
shibata = buscar_produto_shibata_api()

print("\n🔸 Comparativo de preços - Banana Nanica 🔸")

print(f"🟦 Nagumo")
print(f"  🛒 Produto: {nome_nagumo}")
print(f"  💰 Preço: {preco_nagumo}")
print(f"  🖼️ Imagem: {imagem_nagumo}")

if "erro" not in shibata:
    print(f"\n🟥 Shibata")
    print(f"  🛒 Produto: {shibata['nome']}")
    print(f"  💰 Preço total: R$ {shibata['preco_total']:.2f} para {shibata['peso_kg']} {shibata['unidade']}")
    print(f"  📏 Preço por kg: R$ {shibata['preco_por_kg']:.2f}")
else:
    print(f"\n🟥 Shibata: {shibata['erro']}")
