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
    'document': fields.String(required=True, description='Caminho para o arquivo a ser processado'),
})
# Submodelo para 'data'
data_model = api.model('Data', {
    'CHAVEDEACESSO': fields.String(description='Chave de acesso extraída', example='3524 0613 4926 6900 0190...'),
    'N': fields.String(description='Número extraído', example='0090185'),
    'SERIE': fields.String(description='Série extraída', example='1')
})

canhoto_data_model = api.model('CanhotoData', {
    'DATARECEBIMENTO': fields.String(description='Data de recebimento', example='1/1/2024'),
    'INDENTIFICACAOEASSINATURADORECEBEDOR': fields.String(description='Identificação e assinatura do recebedor', example='João da Silva'),
    'NFENSERIE': fields.String(description='Número da nota fiscal e série', example='0000001'),
})

response_model_canhotos = api.model('ResponseCanhotos', {
    'data': fields.Nested(canhoto_data_model)
})
# Modelo de resposta principal
response_model = api.model('Response', {
    'data': fields.Nested(data_model)
})



# Modelo de erro
erro_model = api.model('Erro', {
    'error': fields.String(description='Mensagem de erro'),
})


# Função para determinar o MIME type com base na extensão do arquivo
def get_mime_type(file_path):
    ext = os.path.splitext(file_path.lower())[1]
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    elif ext == ".png":
        return "image/png"
    elif ext == ".pdf":
        return "application/pdf"
    else:
        raise ValueError(f"Formato de arquivo não suportado: {ext}")


# Função genérica para extrair informações
def extract_info(file_path, processor_id):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

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
    print(f"Processando arquivo: {file_path} com MIME type: {mime_type}")

    client = documentai.DocumentProcessorServiceClient(credentials=credentials)
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)

    return result.document


# Função para processar resposta do endpoint /extract
def parse_response(document):
    # Lista de chaves necessárias, corrigindo o problema com a tabulação
    required_keys = ['CHAVEDEACESSO', 'N', 'SERIE', 'CNPJ', 'DATAEMISSAO']
    
    # Inicializa o dicionário com None para todas as chaves
    extracted_data = {key: None for key in required_keys}


    # Itera sobre as entidades do documento
    for entity in document.entities:
        key = entity.type_.strip()  # Remove espaços e tabulações extras
        if key in extracted_data:
            extracted_data[key] = entity.mention_text.strip()  # Remove espaços extras do valor

    return extracted_data


# Função para processar resposta do endpoint /canhotos
def parse_response_canhotos(document):
    required_keys = ['DATADERECEBIMENTO', 'INDFENTIFICACAOEASSINATURADORECEBEDOR', 'NFENSERIE']
    extracted_data = {key: None for key in required_keys}

    for entity in document.entities:
        if entity.type_ in extracted_data:
            extracted_data[entity.type_] = entity.mention_text

    return extracted_data


# Namespace para documentos
ns = api.namespace('documents', description='Operações relacionadas a documentos')

@ns.route('/extract')
class DocumentExtractor(Resource):
    @ns.expect(document_model)
    @ns.response(200, 'Extração bem-sucedida', response_model)
    @ns.response(400, 'Erro de validação ou arquivo inválido', erro_model)
    @ns.response(404, 'Arquivo não encontrado no caminho especificado', erro_model)
    @ns.response(500, 'Erro interno no servidor ou falha ao chamar a API do Google Document AI', erro_model)
    def post(self):
        """Extrai informações de um documento"""
        try:
            data = request.get_json()
            if not data or 'document' not in data:
                return {'error': 'Campo "document" é obrigatório'}, 400

            file_path = data.get('document')
            processor_id = os.getenv("PROCESSOR_ID")

            document = extract_info(file_path, processor_id)
            extracted_info = parse_response(document)
            return {'data': extracted_info}, 200

        except FileNotFoundError as e:
            return {'error': str(e)}, 404
        except ValueError as e:
            return {'error': str(e)}, 400
        except RuntimeError as e:
            return {'error': str(e)}, 500
        except Exception as e:
            return {'error': f"Erro inesperado: {str(e)}"}, 500


@ns.route('/canhotos')
class CanhotosExtractor(Resource):
    @ns.expect(document_model)
    @ns.response(200, 'Extração bem-sucedida', response_model_canhotos)
    @ns.response(400, 'Erro de validação ou arquivo inválido', erro_model)
    @ns.response(404, 'Arquivo não encontrado no caminho especificado', erro_model)
    @ns.response(500, 'Erro interno no servidor ou falha ao chamar a API do Google Document AI', erro_model)
    def post(self):
        """Extrai informações específicas de canhotos"""
        try:
            data = request.get_json()
            if not data or 'document' not in data:
                return {'error': 'Campo "document" é obrigatório'}, 400

            file_path = data.get('document')
            processor_id = os.getenv("CANHOTO_PROCESSOR_ID")

            document = extract_info(file_path, processor_id)
            extracted_info = parse_response_canhotos(document)
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
