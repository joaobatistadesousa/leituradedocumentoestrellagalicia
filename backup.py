# from flask import Flask, request, jsonify
# from flask_restx import Api, Resource, fields
# from google.cloud import documentai_v1 as documentai
# from google.oauth2 import service_account
# import os

# app = Flask(__name__)
# api = Api(
#     app,
#     version='1.0',
#     title='Read and Process Documents with Google Document AI By Itechit',
#     description='API para processar documentos usando o Google Document AI',
# )

# # Modelo de entrada para a API
# document_model = api.model('Document', {
#     'document': fields.String(required=True, description='Caminho para o arquivo a ser processado'),
# })
# response_model = api.model('Response', {
#         'CHAVEDEACESSO': fields.String(description='Chave de acesso extraída', example='3524 0613 4926 6900 0190...'),
#         'N': fields.String(description='Número extraído', example='0090185'),
#         'SERIE': fields.String(description='Série extraída', example='1'),
#     })

# erro_model = api.model('Erro', {
#     'error': fields.String(description='Mensagem de erro'),
# })

# # Função para determinar o MIME type com base na extensão do arquivo
# def get_mime_type(file_path):
#     try:
#         ext = os.path.splitext(file_path.lower())[1]
#         if ext in [".jpg", ".jpeg"]:
#             return "image/jpeg"
#         elif ext == ".png":
#             return "image/png"
#         elif ext == ".pdf":
#             return "application/pdf"
#         else:
#             raise ValueError(f"Formato de arquivo não suportado: {ext}")
#     except Exception as e:
#         raise ValueError(f"Erro ao determinar o MIME type: {str(e)}")

# def extract_info(file_path):
#     try:
#         # Verifica se o arquivo existe
#         if not os.path.isfile(file_path):
#             raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

#         # Carregar as credenciais do serviço
#         credentials = service_account.Credentials.from_service_account_file(
#             "C:\\Users\\Joao\\PycharmProjects\\documentai\\chave3.json"
#         )

#         # Configuração do ID do processador e do projeto
#         project_id = 'teste2-433701'
#         location = 'us'  # Substitua pela localização correta do processador
#         processor_id = 'a0f8eaa030f9e35b'

#         # Nome do processador
#         name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'

#         # Ler o conteúdo do arquivo
#         with open(file_path, 'rb') as file:
#             file_content = file.read()

#         # Determinar o MIME type
#         mime_type = get_mime_type(file_path)
#         print(f"Processando arquivo: {file_path} com MIME type: {mime_type}")

#         # Configurar o cliente do Document AI
#         client = documentai.DocumentProcessorServiceClient(credentials=credentials)

#         # Configurar a requisição
#         raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
#         request = documentai.ProcessRequest(name=name, raw_document=raw_document)

#         # Chamar a API do Document AI
#         result = client.process_document(request=request)

#         # Extrair as informações do resultado
#         document = result.document
#         return parse_response(document)

#     except FileNotFoundError as e:
#         raise e
#     except documentai.exceptions.GoogleAPICallError as api_error:
#         raise RuntimeError(f"Erro ao chamar a API do Google Document AI: {str(api_error)}")
#     except Exception as e:
#         raise RuntimeError(f"Erro inesperado ao processar o documento: {str(e)}")

# def parse_response(document):
#     extracted_data = {}

#     # Percorrer as entidades extraídas
#     for entity in document.entities:
#         extracted_data[entity.type_] = entity.mention_text

#     return extracted_data

# # Definir um namespace para as rotas
# ns = api.namespace('documents', description='Operações relacionadas a documentos')

# @ns.route('/extract')
# class DocumentExtractor(Resource):
#     @ns.expect(document_model)
#     @ns.response(200, 'Extração bem-sucedida', response_model)
#     @ns.response(400, 'Erro de validação ou arquivo inválido', erro_model)
#     @ns.response(404, 'Arquivo não encontrado no caminho especificado', erro_model)
#     @ns.response(500, 'Erro interno no servidor ou falha ao chamar a API do Google Document AI', erro_model)
#     def post(self):
#         """Extrai informações de um documento"""
#         try:
#             data = request.get_json()

#             # Validar entrada
#             if not data or 'document' not in data:
#                 return {'error': 'Campo "document" é obrigatório'}, 400

#             file_path = data.get('document')

#             # Verificar se o arquivo é válido
#             if not os.path.isfile(file_path):
#                 return {'error': 'Caminho do arquivo inválido ou arquivo não encontrado'}, 400

#             # Extrair informações
#             extracted_info = extract_info(file_path)
#             return {'dates': extracted_info}, 200

#         except FileNotFoundError as e:
#             return {'error': str(e)}, 404
#         except ValueError as e:
#             return {'error': str(e)}, 400
#         except RuntimeError as e:
#             return {'error': str(e)}, 500
#         except Exception as e:
#             return {'error': f"Erro inesperado: {str(e)}"}, 500

# if __name__ == '__main__':
#     app.run(debug=True)
