import requests

# URL da imagem
url = "https://blipmediastore.blip.ai/secure-medias/Media_ede818cd-8924-4435-b66e-d543df5f35b4?sv=2024-05-04&st=2024-12-13T12%3A21%3A10Z&se=2024-12-13T12%3A51%3A10Z&sr=b&sp=r&sig=wCCZHOAagDjwJgpSsDDdGPcfpIj%2FT1SfFKFxnsX%2FUWA%3D&secure=true"

# Nome do arquivo para salvar
output_file = "imagem.png"

try:
    # Fazer o download do conteúdo
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Levanta exceção para erros HTTP

    # Salvar o conteúdo como arquivo
    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"Imagem salva como {output_file}")
except requests.exceptions.RequestException as e:
    print(f"Erro ao baixar a imagem: {e}")
