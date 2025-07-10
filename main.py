import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# Configuração da página
st.set_page_config(page_title="Busca de Produtos Nagumo", page_icon="🛒")

# CSS para remover espaço superior e rodapé
st.markdown("""
    <style>
        .block-container { padding-top: 0rem; }
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Título
st.markdown("<h5>🛒 Preço Nagumo</h5>", unsafe_allow_html=True)

busca = st.text_input("Digite o nome do produto:")

def calcular_preco_unitario(preco_str, descricao, nome):
    try:
        preco_valor = float(preco_str.replace("R$", "").replace(",", ".").split()[0])
    except:
        return None

    preco_unitario = None
    unidade_tipo = None
    fontes = [descricao.lower(), nome.lower()]

    for fonte in fontes:
        match_g = re.search(r"(\d+)\s*(g|gramas?)", fonte)
        if match_g:
            gramas = int(match_g.group(1))
            if gramas > 0:
                preco_unitario = f"📏 ~ R$ {preco_valor / (gramas / 1000):.2f}/kg"
                return preco_unitario

        match_kg = re.search(r"(\d+)\s*(kg|quilo)", fonte)
        if match_kg:
            kg = int(match_kg.group(1))
            if kg > 0:
                preco_unitario = f"📏 ~ R$ {preco_valor / kg:.2f}/kg"
                return preco_unitario

        match_ml = re.search(r"(\d+)\s*(ml|mililitros?)", fonte)
        if match_ml:
            ml = int(match_ml.group(1))
            if ml > 0:
                preco_unitario = f"📏 ~ R$ {preco_valor / (ml / 1000):.2f}/L"
                return preco_unitario

        match_l = re.search(r"(\d+)\s*(l|litros?)", fonte)
        if match_l:
            litros = int(match_l.group(1))
            if litros > 0:
                preco_unitario = f"📏 ~ R$ {preco_valor / litros:.2f}/L"
                return preco_unitario

        match_un = re.search(r"(\d+)\s*(un|unidades?)", fonte)
        if match_un:
            unidades = int(match_un.group(1))
            if unidades > 0:
                preco_valor_unitario = preco_valor / unidades
                preco_unitario = f"📏 ~ R$ {preco_valor_unitario:.2f}/un"
                unidade_tipo = "un"

        match_rls = re.search(r"(\d+)\s*(rls?|rolos?)", fonte)
        if match_rls:
            rolos = int(match_rls.group(1))
            if rolos > 0:
                preco_valor_unitario = preco_valor / rolos
                preco_unitario = f"📏 ~ R$ {preco_valor_unitario:.2f}/rolo"
                unidade_tipo = "rolo"

    metros_por_item = None
    quantidade_itens = None

    for fonte in fontes:
        match_metros = re.search(r"(\d+)\s*(m|mt|metros?)\b", fonte)
        if match_metros:
            metros_por_item = int(match_metros.group(1))

        match_quantidade = re.search(r"(\d+)\s*(un|unidades?|rls?|rolos?)\b", fonte)
        if match_quantidade:
            quantidade_itens = int(match_quantidade.group(1))

    if metros_por_item and quantidade_itens:
        total_metros = metros_por_item * quantidade_itens
        if total_metros > 0:
            preco_metro = preco_valor / total_metros
            preco_metro_str = f"(💲{preco_metro:.3f}/m)"
            if preco_unitario:
                preco_unitario += f" {preco_metro_str}"
            else:
                preco_unitario = f"📏 ~ {preco_metro_str}"

    return preco_unitario

def buscar_produtos_nagumo(palavra_chave):
    palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
    url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}"
    headers = {"User-Agent": "Mozilla/5.0"}

    produtos = []

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        product_containers = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

        for container in product_containers:
            nome_tag = container.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
            if not nome_tag:
                continue

            nome_text = nome_tag.text.strip()

            preco_text = "Preço não encontrado"
            preco_promo_tag = container.find('span', class_='sc-fLlhyt gMFJKu sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
            preco_antigo_tag = container.find('span', class_='sc-fLlhyt ehGA-Dk sc-14455254-0 sc-c5cd0085-12 ezNOEq bFqXWZ')
            desconto_tag = container.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-11 ezNOEq hoiAgS')

            if preco_promo_tag and preco_antigo_tag and desconto_tag:
                preco_promocional = preco_promo_tag.text.strip().replace("R$", "").strip()
                preco_antigo = preco_antigo_tag.text.strip().replace("R$", "").strip()
                desconto = desconto_tag.text.strip()
                preco_text = f"💰 R$ {preco_promocional} (💲{preco_antigo}🔻 {desconto})"
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
            descricao_text = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"

            imagem_url = "Imagem não encontrada"
            noscript_tag = container.find('noscript')
            if noscript_tag:
                nosoup = BeautifulSoup(noscript_tag.decode_contents(), 'html.parser')
                img_tag = nosoup.find('img')
                if img_tag and img_tag.get('src'):
                    imagem_url = img_tag['src']

            preco_unitario = calcular_preco_unitario(preco_base, descricao_text, nome_text)

            produtos.append({
                "nome": nome_text,
                "preco": preco_text,
                "descricao": descricao_text,
                "imagem": imagem_url,
                "preco_unitario": preco_unitario
            })

        return produtos

    except Exception as e:
        return [{"nome": "Erro na busca", "preco": "", "descricao": "", "imagem": str(e)}]

if busca:
    resultados = buscar_produtos_nagumo(busca)
    if resultados:
        for produto in resultados:
            if "http" in produto["imagem"]:
                imagem_html = f'<img src="{produto["imagem"]}" width="100" style="border-radius:8px;">'
            else:
                imagem_html = "Sem imagem"

            preco_unit = f'<div style="margin-top:4px;">{produto["preco_unitario"]}</div>' if produto["preco_unitario"] else ""

            st.markdown(f"""
                <div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 1rem; flex-wrap: wrap;">
                    <div style="flex: 0 0 auto;">
                        {imagem_html}
                    </div>
                    <div style="flex: 1; word-break: break-word; overflow-wrap: anywhere;">
                        <strong>{produto['nome']}</strong><br>
                        <span>{produto['preco']}</span>
                        {preco_unit}
                        <div style="margin-top: 4px; font-size: 0.85em; color: #666;">📝 {produto['descricao']}</div>
                    </div>
                </div>
                <hr style="margin: 8px 0;">
            """, unsafe_allow_html=True)
    else:
        st.write("Nenhum produto encontrado.")
