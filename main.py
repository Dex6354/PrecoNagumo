import requests

def salvar_html_nagumo(palavra_chave, nome_arquivo="pagina_nagumo.html"):
    palavra_chave_url = palavra_chave.strip().lower().replace(" ", "+")
    url = f"https://www.nagumo.com.br/nagumo/74b2f698-cffc-4a38-b8ce-0407f8d98de3/busca/{palavra_chave_url}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(r.text)
        print(f"Arquivo salvo: {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao baixar página: {e}")

# Exemplo de uso:
salvar_html_nagumo("banana prata")
