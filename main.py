import streamlit as st
import requests
import re
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

termo = st.text_input("🛒Digite o nome do produto:")

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def calcular_preco_unitario(preco_valor, descricao, nome, unidade_api=None):
    preco_unitario = "Sem unidade"
    fontes = [descricao.lower(), nome.lower()]

    for fonte in fontes:
        match_g = re.search(r"(\d+[.,]?\d*)\s*(g|gramas?)", fonte)
        if match_g:
            gramas = float(match_g.group(1).replace(',', '.'))
            if gramas > 0:
                return f"~ R$ {preco_valor / (gramas / 1000):.2f}/kg"

        match_kg = re.search(r"(\d+[.,]?\d*)\s*(kg|quilo)", fonte)
        if match_kg:
            kg = float(match_kg.group(1).replace(',', '.'))
            if kg > 0:
                return f"~ R$ {preco_valor / kg:.2f}/kg"

        match_ml = re.search(r"(\d+[.,]?\d*)\s*(ml|mililitros?)", fonte)
        if match_ml:
            ml = float(match_ml.group(1).replace(',', '.'))
            if ml > 0:
                return f"~ R$ {preco_valor / (ml / 1000):.2f}/L"

        match_l = re.search(r"(\d+[.,]?\d*)\s*(l|litros?)", fonte)
        if match_l:
            litros = float(match_l.group(1).replace(',', '.'))
            if litros > 0:
                return f"~ R$ {preco_valor / litros:.2f}/L"

        match_un = re.search(r"(\d+[.,]?\d*)\s*(un|unidades?)", fonte)
        if match_un:
            unidades = float(match_un.group(1).replace(',', '.'))
            if unidades > 0:
                return f"~ R$ {preco_valor / unidades:.2f}/un"

    # Fallback com campo "unit"
    if unidade_api:
        unidade_api = unidade_api.lower()
        if unidade_api == 'kg':
            return f"~ R$ {preco_valor:.2f}/kg"
        elif unidade_api == 'g':
            return f"~ R$ {preco_valor * 1000:.2f}/kg"
        elif unidade_api == 'l':
            return f"~ R$ {preco_valor:.2f}/L"
        elif unidade_api == 'ml':
            return f"~ R$ {preco_valor * 1000:.2f}/L"
        elif unidade_api == 'un':
            return f"~ R$ {preco_valor:.2f}/un"

    return preco_unitario

def extrair_valor_unitario(preco_unitario):
    match = re.search(r"R\$ (\d+[.,]?\d*)", preco_unitario)
    if match:
        return float(match.group(1).replace(',', '.'))
    return float('inf')

def buscar_nagumo(term="banana"):
    url = "https://nextgentheadless.instaleap.io/api/v3"

    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.nagumo.com",
        "Referer": "https://www.nagumo.com/",
        "User-Agent": "Mozilla/5.0",
        "apollographql-client-name": "Ecommerce SSR",
        "apollographql-client-version": "0.11.0"
    }

    payload = {
        "operationName": "SearchProducts",
        "variables": {
            "searchProductsInput": {
                "clientId": "NAGUMO",
                "storeReference": "22",
                "currentPage": 1,
                "minScore": 1,
                "pageSize": 100,
                "search": [{"query": term}],
                "filters": {},
                "googleAnalyticsSessionId": ""
            }
        },
        "query": """
        query SearchProducts($searchProductsInput: SearchProductsInput!) {
          searchProducts(searchProductsInput: $searchProductsInput) {
            products {
              name
              price
              photosUrl
              sku
              stock
              description
              unit
              promotion {
                isActive
                type
                conditions {
                  price
                  priceBeforeTaxes
                }
              }
            }
          }
        }
        """
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    return data.get("data", {}).get("searchProducts", {}).get("products", [])

if termo:
    with st.spinner("🔍 Buscando produtos..."):
        produtos = buscar_nagumo(termo)

    st.markdown(f"<small>🔎 {len(produtos)} produto(s) encontrado(s).</small>", unsafe_allow_html=True)

    for p in produtos:
        preco_normal = p.get("price", 0)
        promocao = p.get("promotion") or {}
        cond = promocao.get("conditions") or []
        preco_desconto = None

        if promocao.get("isActive") and isinstance(cond, list) and len(cond) > 0:
            preco_desconto = cond[0].get("price")

        preco_exibir = preco_desconto if preco_desconto else preco_normal
        p['preco_unitario_str'] = calcular_preco_unitario(preco_exibir, p['description'], p['name'], p.get("unit"))
        p['preco_unitario_valor'] = extrair_valor_unitario(p['preco_unitario_str'])

    produtos = sorted(produtos, key=lambda x: x['preco_unitario_valor'])

    for p in produtos:
        imagem = p['photosUrl'][0] if p.get('photosUrl') else ""
        preco_unitario = p['preco_unitario_str']
        preco = p['price']
        promocao = p.get("promotion") or {}
        cond = promocao.get("conditions") or []
        preco_desconto = None

        if promocao.get("isActive") and isinstance(cond, list) and len(cond) > 0:
            preco_desconto = cond[0].get("price")

        if preco_desconto and preco_desconto < preco:
            desconto_percentual = ((preco - preco_desconto) / preco) * 100
            preco_html = f"""
                <span style='font-weight: bold; font-size: 1rem;'>R$ {preco_desconto:.2f}</span>
                <span style='color: red; font-size: 0.9rem;'> ({desconto_percentual:.0f}% OFF)</span><br>
                <span style='text-decoration: line-through; color: gray;'>R$ {preco:.2f}</span>
            """
        else:
            preco_html = f"R$ {preco:.2f}"

        st.markdown(f"""
            <div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 1rem; flex-wrap: wrap;">
                <div style="flex: 0 0 auto;">
                    <img src="{imagem}" width="100" style="border-radius:8px;">
                </div>
                <div style="flex: 1; word-break: break-word; overflow-wrap: anywhere;">
                    <strong>{p['name']}</strong><br>
                    <strong>{preco_html}</strong><br>
                    <div style="margin-top: 4px; font-size: 0.9em; color: #666;">{preco_unitario}</div>
                    <div style="color: gray; font-size: 0.8em;">Estoque: {p['stock']}</div>
                </div>
            </div>
            <hr style="margin: 8px 0;">
        """, unsafe_allow_html=True)
