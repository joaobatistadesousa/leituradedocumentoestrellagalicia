import time
from google.cloud import documentai_v1 as documentai
from google.oauth2 import service_account
import os

# Configurações
credentials_path = "C:\\Users\\Joao\\PycharmProjects\\documentai\\chave3.json"
processor_name = "projects/teste2-433701/locations/us/processors/a0f8eaa030f9e35b"

# Verifique se o arquivo de credenciais existe
if not os.path.exists(credentials_path):
    print(f"Arquivo de credenciais não encontrado: {credentials_path}")
    exit(1)

# Verifique se o processador está configurado corretamente
try:
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = documentai.DocumentProcessorServiceClient(credentials=credentials)
    processor = client.get_processor(name=processor_name)
    print(f"Processador encontrado: {processor.display_name}")
except Exception as e:
    print(f"Erro ao acessar o processador: {e}")
    exit(1)

def process_file(file_path):
    """Processa o arquivo de forma síncrona."""
    # Verifique se o arquivo existe
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return None

    try:
        # Ler o arquivo
        with open(file_path, "rb") as file:
            file_content = file.read()
        print("Arquivo lido com sucesso.")

        # Configurar o request
        raw_document = documentai.RawDocument(content=file_content, mime_type="image/jpeg")
        request = documentai.ProcessRequest(name=processor_name, raw_document=raw_document)
        print("Requisição configurada com sucesso.")

        # Medir o tempo do processamento
        start_time = time.time()
        result = client.process_document(request=request)
        elapsed_time = time.time() - start_time
        print(f"Tempo de processamento do Document AI: {elapsed_time:.2f} segundos")

        # Extrair dados do documento
        extracted_data = {entity.type_: entity.mention_text for entity in result.document.entities}
        print("Extração concluída com sucesso.")
        return extracted_data

    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
    return None

if __name__ == "__main__":
    file_path = "C:\\Users\\Joao\\Downloads\\notas_fiscais\\ilovepdf_pages-to-jpg\\02\\02_page-0001.jpg"
    print("Iniciando processamento...")

    # Processar o arquivo e exibir dados extraídos
    try:
        extracted_data = process_file(file_path)
        if extracted_data:
            print("Dados extraídos:")
            print(extracted_data)
        else:
            print("Nenhum dado extraído.")
    except Exception as e:
        print(f"Erro durante a execução: {e}")
