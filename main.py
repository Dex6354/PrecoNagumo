import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import hashlib
import time
import concurrent.futures
import unicodedata

st.set_page_config(page_title="Busca de Produtos Nagumo", page_icon="🛒")

st.markdown("""
    <style>
        .block-container { padding-top: 0rem; }
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        div, span, strong, small {
            font-size: 0.75rem !important;
        }
        img {
            max-width: 100px;
            height: auto;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h5 style="display: flex; align-items: center;">
        <img src="https://institucional.nagumo.com.br/images/nagumo-2000.png" width="80" style="margin-right:8px; background-color: white; border-radius: 4px; padding: 2px;"/>
        Preço Nagumo
    </h5>
""", unsafe_allow_html=True)

busca = st.text_input("🛒Digite o nome do produto:")

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def calcular_preco_unitario(preco_str, descricao, nome):
    try:
        preco_valor = float(preco_str.replace("R$", "").replace(",", ".").split()[0])
    except:
        return "📦 Sem unidade", None

    preco_unitario = None
    preco_metro = None
    fontes = [descricao.lower(), nome.lower()]

    for fonte in fontes:
        match_g = re.search(r"(\d+[.,]?\d*)\s*(g|gramas?)", fonte)
        if match_g:
            gramas = float(match_g.group(1).replace(',', '.'))
            if gramas > 0:
                return f"📦 ~ R$ {preco_valor / (gramas / 1000):.2f}/kg", None

        match_kg = re.search(r"(\d+[.,]?\d*)\s*(kg|quilo)", fonte)
        if match_kg:
            kg = float(match_kg.group(1).replace(',', '.'))
            if kg > 0:
                return f"📦 ~ R$ {preco_valor / kg:.2f}/kg", None

        match_ml = re.search(r"(\d+[.,]?\d*)\s*(ml|mililitros?)", fonte)
        if match_ml:
            ml = float(match_ml.group(1).replace(',', '.'))
            if ml > 0:
                return f"📦 ~ R$ {preco_valor / (ml / 1000):.2f}/L", None

        match_l = re.search(r"(\d+[.,]?\d*)\s*(l|litros?)", fonte)
        if match_l:
            litros = float(match_l.group(1).replace(',', '.'))
            if litros > 0:
                return f"📦 ~ R$ {preco_valor / litros:.2f}/L", None

        match_un = re.search(r"(\d+[.,]?\d*)\s*(un|unidades?)", fonte)
        if match_un:
            unidades = float(match_un.group(1).replace(',', '.'))
            if unidades > 0:
                preco_unitario = f"📦 ~ R$ {preco_valor / unidades:.2f}/un"

        match_rls = re.search(r"(\d+[.,]?\d*)\s*(rls?|rolos?)", fonte)
        if match_rls:
            rolos = float(match_rls.group(1).replace(',', '.'))
            if rolos > 0:
                preco_unitario = f"📦 ~ R$ {preco_valor / rolos:.2f}/rolo"

    metros_por_item = None
    quantidade_itens = None

    for fonte in fontes:
        match_metros = re.search(r"(\d+[.,]?\d*)\s*(m|mt|metros?)", fonte)
        if match_metros:
            metros_por_item = float(match_metros.group(1).replace(',', '.'))

        match_qtd = re.search(r"(\d+[.,]?\d*)\s*(un|unidades?|rolos?|rls?)", fonte)
        if match_qtd:
            quantidade_itens = float(match_qtd.group(1).replace(',', '.'))

    if metros_por_item and quantidade_itens:
        total_metros = metros_por_item * quantidade_itens
        if total_metros > 0:
            preco_metro = f"📏 ~ R$ {preco_valor / total_metros:.3f}/m"

    if preco_unitario is None and preco_metro is None:
        return "📦 Sem unidade", None

    return preco_unitario, preco_metro

def extrair_valor_unitario(preco_unitario_str):
    if not preco_unitario_str or preco_unitario_str == "📦 Sem unidade":
        return float('inf')
    m = re.search(r"R\$ ([\d.,]+)", preco_unitario_str)
    if m:
        valor_str = m.group(1).replace('.', '').replace(',', '.')
        try:
            return float(valor_str)
        except:
            return float('inf')
    return float('inf')

def extrair_valor_metro(preco_metro_str):
    if not preco_metro_str:
        return float('inf')
    match = re.search(r"R\$ ([\d.,]+)", preco_metro_str)
    if match:
        valor_str = match.group(1).replace('.', '').replace(',', '.')
        try:
            return float(valor_str)
        except:
            return float('inf')
    return float('inf')

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text

def extrair_produtos(html, produtos_unicos):
    soup = BeautifulSoup(html, 'html.parser')
    containers = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

    for container in containers:
        nome_tag = container.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
        if not nome_tag:
            continue
        nome_text = nome_tag.text.strip()
        hash_nome = hashlib.md5(nome_text.encode()).hexdigest()
        if hash_nome in produtos_unicos:
            continue

        preco_text = "Preço não encontrado"
        preco_promo_tag = container.find('span', class_='sc-fLlhyt gMFJKu sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
        preco_antigo_tag = container.find('span', class_='sc-fLlhyt ehGA-Dk sc-14455254-0 sc-c5cd0085-12 ezNOEq bFqXWZ')
        desconto_tag = container.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-11 ezNOEq hoiAgS')

        if preco_promo_tag and preco_antigo_tag and desconto_tag:
            preco_promocional = preco_promo_tag.text.strip().replace("R$", "").strip()
            preco_antigo = preco_antigo_tag.text.strip().replace("R$", "").strip()
            desconto = desconto_tag.text.strip()
            preco_text = f"💰 R$ {preco_promocional} ({preco_antigo} {desconto})"
            preco_base = preco_promocional
        elif preco_promo_tag:
            preco = preco_promo_tag.text.strip().replace("R$", "").strip()
            preco_text = f"💰 R$ {preco}"
            preco_base = preco
        else:
            preco_normal_tag = container.find('span', class_='sc-fLlhyt fKrYQk sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
            if preco_normal_tag:
                preco = preco_normal_tag.text.strip().replace("R$", "").strip()
                preco_text = f"💰 R$ {preco}"
                preco_base = preco
            else:
                preco_base = "0"

        descricao_tag = container.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
        descricao_text = descricao_tag.text.strip() if descricao_tag else "Sem descrição"

        imagem_url = "Imagem não encontrada"
        noscript_tag = container.find('noscript')
        if noscript_tag:
            nosoup = BeautifulSoup(noscript_tag.decode_contents(), 'html.parser')
            img_tag = nosoup.find('img')
            if img_tag and img_tag.get('src'):
                imagem_url = img_tag['src']

        preco_unitario, preco_metro = calcular_preco_unitario(preco_base, descricao_text, nome_text)
        preco_unitario_valor = extrair_valor_unitario(preco_unitario)
        preco_metro_valor = extrair_valor_metro(preco_metro)

        produtos_unicos[hash_nome] = {
            "nome": nome_text,
            "preco": preco_text,
            "descricao": descricao_text,
            "imagem": imagem_url,
            "preco_unitario": preco_unitario,
            "preco_metro": preco_metro,
            "preco_unitario_valor": preco_unitario_valor,
            "preco_metro_valor": preco_metro_valor
        }

def buscar_produtos_dupla(busca):
    palavra_chave_url = busca.strip().lower().replace(" ", "+")
    url_base = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}"
    urls = [url_base, url_base]

    produtos_unicos = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        resultados_html = list(executor.map(fetch_html, urls))

    for html in resultados_html:
        extrair_produtos(html, produtos_unicos)

    busca_normalizada = remover_acentos(busca)
    palavras_busca = busca_normalizada.split()

    produtos_filtrados = [
        p for p in produtos_unicos.values()
        if all(palavra in remover_acentos(p["nome"]) for palavra in palavras_busca)
    ]

    if any(p["preco_metro_valor"] != float('inf') for p in produtos_filtrados):
        produtos_filtrados.sort(key=lambda p: p.get("preco_metro_valor", float('inf')))
    else:
        produtos_filtrados.sort(key=lambda p: p.get("preco_unitario_valor", float('inf')))

    return produtos_filtrados

if busca:
    inicio = time.time()
    resultados = buscar_produtos_dupla(busca)
    fim = time.time()
    tempo_execucao = fim - inicio
    st.markdown(f"<small>🔎 {len(resultados)} produto(s) encontrado(s). {tempo_execucao:.1f}s.</small>", unsafe_allow_html=True)

    for produto in resultados:
        imagem_html = f'<img src="{produto["imagem"]}" width="100" style="border-radius:8px;">' if "http" in produto["imagem"] else "Sem imagem"

        preco_unit = ""
        if produto["preco_unitario"]:
            preco_unit += f'<div style="margin-top:4px;">{produto["preco_unitario"]}</div>'
        if produto["preco_metro"]:
            preco_unit += f'<div style="margin-top:2px;">{produto["preco_metro"]}</div>'

        preco_html = ""
        preco_texto = produto["preco"]

        m = re.match(r"💰 R\$ ([\d.,]+)(?: \(([\d.,]+) (-?\d+%)\))?", preco_texto)

        if m:
            preco_promocional = m.group(1)
            preco_antigo = m.group(2)
            desconto = m.group(3)

            if preco_antigo and desconto:
                preco_html = (
                    f'<div style="font-weight:bold; font-size:1rem;">R$ {preco_promocional} '
                    f'<span style="color: red;">{desconto} OFF</span></div>'
                    f'<div style="color: gray; text-decoration: line-through; font-size:0.9rem; margin-top:2px;">R$ {preco_antigo}</div>'
                )
            else:
                preco_html = f'<div style="font-weight:bold; font-size:1rem;">R$ {preco_promocional}</div>'
        else:
            preco_html = f'<div>{preco_texto}</div>'

        st.markdown(f"""
            <div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 1rem; flex-wrap: wrap;">
                <div style="flex: 0 0 auto;">
                    {imagem_html}
                </div>
                <div style="flex: 1; word-break: break-word; overflow-wrap: anywhere;">
                    <strong>{produto['nome']}</strong><br>
                    {preco_html}
                    {preco_unit}
                    <div style="margin-top: 4px; font-size: 0.85em; color: #666;">📝 {produto['descricao']}</div>
                </div>
            </div>
            <hr style="margin: 8px 0;">
        """, unsafe_allow_html=True)
