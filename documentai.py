from google.cloud import documentai_v1 as documentai
from google.oauth2 import service_account

def extract_info(file_path):
    try:
        # Carregar as credenciais do serviço
        credentials = service_account.Credentials.from_service_account_file(
            "C:\\Users\\Joao\\PycharmProjects\\documentai\\chave3.json"
        )

        # Configuração do ID do processador e do projeto
        project_id = 'teste2-433701'
        location = 'us'  # Substitua pela localização correta do processador
        processor_id = 'cabab424991139fa'

        # Nome do processador
        name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'

        # Ler o conteúdo do arquivo
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Configurar o cliente do Document AI
        client = documentai.DocumentProcessorServiceClient(credentials=credentials)

        # Configurar a requisição
        raw_document = documentai.RawDocument(content=file_content, mime_type="image/jpeg")
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)

        # Chamar a API do Document AI
        result = client.process_document(request=request)

        # Extrair as informações do resultado
        document = result.document
        return parse_response(document)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

def parse_response(document):
    extracted_data = {}

    # Percorrer as entidades extraídas
    for entity in document.entities:
        extracted_data[entity.type_] = entity.mention_text

    return extracted_data

if __name__ == '__main__':
    file_path = "C:\\Users\\Joao\\Downloads\\minhaIdentidade.jpg"
    extracted_info = extract_info(file_path)
    if extracted_info:
        print(extracted_info)
    else:
        print("Nenhuma informação foi extraída.")
