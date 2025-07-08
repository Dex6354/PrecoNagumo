def buscar_produto_nagumo(palavra_chave):
    palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
    url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        product_containers = soup.find_all('div', class_='sc-c5cd0085-0 fWmXTW')

        for container in product_containers:
            nome_tag = container.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-4 ezNOEq clsIKA')
            if not nome_tag:
                continue

            nome_text = nome_tag.text.strip()
            search_words = set(palavra_chave.lower().split())
            product_words = set(nome_text.lower().split())
            if not search_words.intersection(product_words):
                continue

            # Preço atual promocional
            preco_promocao_tag = container.find('span', class_='sc-fLlhyt gMFJKu sc-14455254-0 sc-c5cd0085-9 ezNOEq dDNfcV')
            preco_promocao = preco_promocao_tag.text.strip() if preco_promocao_tag else None

            # Preço antigo
            preco_antigo_tag = container.find('span', class_='sc-fLlhyt ehGA-Dk sc-14455254-0 sc-c5cd0085-12 ezNOEq bFqXWZ')
            preco_antigo = preco_antigo_tag.text.strip() if preco_antigo_tag else None

            # Percentual de desconto
            desconto_tag = container.find('span', class_='sc-fLlhyt hJreDe sc-14455254-0 sc-c5cd0085-11 ezNOEq hoiAgS')
            desconto = desconto_tag.text.strip() if desconto_tag else None

            # Monta o preço final de acordo com os dados encontrados
            if preco_promocao and preco_antigo and desconto:
                preco_text = f"{preco_promocao} ({preco_antigo} {desconto})"
            elif preco_promocao:
                preco_text = preco_promocao
            else:
                preco_text = "Preço não encontrado"

            descricao_tag = container.find('span', class_='sc-fLlhyt dPLwZv sc-14455254-0 sc-c5cd0085-10 ezNOEq krnAMj')
            descricao_text = descricao_tag.text.strip() if descricao_tag else "Descrição não encontrada"

            imagem_url = "Imagem não encontrada"
            noscript_tag = container.find('noscript')
            if noscript_tag:
                nosoup = BeautifulSoup(noscript_tag.decode_contents(), 'html.parser')
                img_tag = nosoup.find('img')
                if img_tag and img_tag.get('src'):
                    imagem_url = img_tag['src']

            return nome_text, preco_text, descricao_text, imagem_url

        return "Nome não encontrado", "Preço não encontrado", "Descrição não encontrada", "Imagem não encontrada"

    except Exception as e:
        return "Erro na busca", "", "", str(e)
