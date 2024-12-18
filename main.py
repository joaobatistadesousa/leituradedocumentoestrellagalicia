import requests
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from google.cloud import documentai_v1 as documentai
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='Read and Process Documents with Google Document AI By Itechit',
    description='API para processar documentos usando o Google Document AI',
)

# Modelo de entrada para a API
document_model = api.model('Document', {
    'url': fields.String(required=True, description='URL do arquivo a ser baixado e processado'),
})

# Submodelo para 'data'
data_model = api.model('Data', {
    'CHAVEDEACESSO': fields.String(description='Chave de acesso extraída', example='3524 0613 4926 6900 0190...'),
    'N': fields.String(description='Número extraído', example='0090185'),
    'SERIE': fields.String(description='Série extraída', example='1'),
    'DATAEMISSAO': fields.String(description='Data de emissão', example='1/1/2024'),
    "CNPJ": fields.String(description='CNPJ', example='12.345.678/0001-90'),
    
})

canhoto_data_model = api.model('CanhotoData', {
    'DATARECEBIMENTO': fields.String(description='Data de recebimento', example='1/1/2024'),
    'INDENTIFICACAOEASSINATURADORECEBEDOR': fields.String(description='Identificação e assinatura do recebedor', example='João da Silva'),
    'NFENSERIE': fields.String(description='Número da nota fiscal e série', example='0000001'),
    'Serie': fields.String(description='Série da nota fiscal', example='1')
})
# Função para determinar o MIME type com base na extensão do arquivo
def get_mime_type(file_path):
    ext = os.path.splitext(file_path.lower())[1]
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    elif ext == ".png":
        return "image/png"
    else:
        raise ValueError(f"Formato de arquivo não suportado: {ext}")

# Função para baixar o arquivo
def download_file(url, output_path):
    """Baixa um arquivo a partir de uma URL e salva localmente"""
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Levanta exceção se houver erro HTTP
    with open(output_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

# Função para processar o documento com Google Document AI
def extract_info(file_path, processor_id):
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("PROCESSOR_LOCATION")

    if not all([credentials_path, project_id, location, processor_id]):
        raise RuntimeError("Configurações ausentes. Verifique o arquivo .env.")

    if not os.path.isfile(credentials_path):
        raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_path}")

    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'

    with open(file_path, 'rb') as file:
        file_content = file.read()

    mime_type = get_mime_type(file_path)

    client = documentai.DocumentProcessorServiceClient(credentials=credentials)
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)

    return result.document

# Função para processar a resposta
def parse_response(document):
    # Lista de chaves necessárias
    required_keys = ['CHAVEDEACESSO', 'N', 'SERIE', 'CNPJ', 'DATAEMISSAO']
    
    # Inicializa o dicionário com None para todas as chaves
    extracted_data = {key: None for key in required_keys}

    # Itera sobre as entidades do documento
    for entity in document.entities:
        print(f"Tipo de entidade: {entity.type_}, Texto mencionado: {entity.mention_text}")  # Log de depuração
        
        key = entity.type_.strip()  # Remove espaços e tabulações extras
        if key in extracted_data:
            extracted_data[key] = entity.mention_text.strip() if entity.mention_text else None  # Garantir que valores vazios sejam tratados

    return extracted_data

def parse_response_canhotos(document):
    required_keys = ['DATADERECEBIMENTO', 'INDFENTIFICACAOEASSINATURADORECEBEDOR', 'NFENSERIE', 'Serie']
    extracted_data = {key: None for key in required_keys}

    for entity in document.entities:
        if entity.type_ in extracted_data:
            value = entity.mention_text.strip() if entity.mention_text else None
            
            # Remover pontos e espaços para NFENSERIE
            if entity.type_ == "NFENSERIE" and value:
                value = value.replace(".", "").replace(" ", "")
            
            extracted_data[entity.type_] = value

    return extracted_data


# Namespace para documentos
ns = api.namespace('documents', description='Operações relacionadas a documentos')

@ns.route('/extract')
class DocumentExtractor(Resource):
    @ns.expect(document_model)
    @ns.response(200, 'Extração bem-sucedida', data_model)
    def post(self):
        """Baixa e processa um documento para extração de dados"""
        try:
            data = request.get_json()
            if not data or 'url' not in data:
                return {'error': 'Campo "url" é obrigatório'}, 400

            url = data.get('url')
            output_path = "temp_document.jpg"  # Alterado para imagem

            # Baixar o arquivo (imagem)
            download_file(url, output_path)

            processor_id = os.getenv("PROCESSOR_ID")

            # Processar o arquivo (imagem)
            document = extract_info(output_path, processor_id)
            extracted_info = parse_response(document)

            # Remover arquivo temporário
            os.remove(output_path)

            return {'data': extracted_info}, 200

        except FileNotFoundError as e:
            return {'error': str(e)}, 404
        except ValueError as e:
            return {'error': str(e)}, 400
        except RuntimeError as e:
            return {'error': str(e)}, 500
        except Exception as e:
            return {'error': f"Erro inesperado: {str(e)}"}, 500

# Endpoint específico para o canhoto (pode ser semelhante ao outro)
@ns.route('/extract-canhoto')
class CanhotoExtractor(Resource):
    @ns.expect(document_model)
    @ns.response(200, 'Extração bem-sucedida', canhoto_data_model)
    def post(self):
        """Baixa e processa o canhoto para extração de dados"""
        try:
            data = request.get_json()
            if not data or 'url' not in data:
                return {'error': 'Campo "url" é obrigatório'}, 400

            url = data.get('url')
            output_path = "temp_canhoto.jpg"  # Para o canhoto, alterado para imagem

            # Baixar o arquivo (imagem do canhoto)
            download_file(url, output_path)

            processor_id = os.getenv("CANHOTO_PROCESSOR_ID")

            # Processar o arquivo (imagem do canhoto)
            document = extract_info(output_path, processor_id)
            extracted_info = parse_response_canhotos(document)

            # Remover arquivo temporário
            os.remove(output_path)

            return {'data': extracted_info}, 200

        except FileNotFoundError as e:
            return {'error': str(e)}, 404
        except ValueError as e:
            return {'error': str(e)}, 400
        except RuntimeError as e:
            return {'error': str(e)}, 500
        except Exception as e:
            return {'error': f"Erro inesperado: {str(e)}"}, 500

if __name__ == '__main__':
    app.run(debug=True)
