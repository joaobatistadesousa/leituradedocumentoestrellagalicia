# Document AI API: Extração de Informações de Documentos

Este projeto implementa uma API para processar documentos utilizando o **Google Document AI**. Ele permite enviar um documento para extração de informações específicas, retornando os dados relevantes de forma estruturada.

---

## **Instalação**

1. **Clonar o repositório:**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_PROJETO>
   ``` 
## *Criação de um ambiente virual*
 

```bash
 python -m venv venv
source venv/bin/activate # Linux/MacOS
venv\Scripts\activate    # Windows
```



## instalação de todas as dependencias
Instale todas as dependências necessárias com o comando:

```bash
pip install -r requirements.txt

```
## Configurar o arquivo .env: Crie um arquivo chamado .env no diretório raiz do projeto com as seguintes variáveis:

```.env
GOOGLE_CREDENTIALS_PATH=path/para/sua/chave.json
PROJECT_ID=seu-id-do-projeto
PROCESSOR_LOCATION=us
PROCESSOR_ID=seu-id-do-processador

```


# Configuração do Google Cloud
 ##### 1 . Ative o Google Document AI na sua conta do Google Cloud:

* Vá para o painel Google Cloud Console.
* Ative a API Document AI.
#### 2. Crie um processador:

* Navegue até "Document AI > Processors".
* Crie um novo processador e copie o Processor ID.
* Baixe o arquivo de credenciais:

#### Vá para "IAM e Administrador > Contas de Serviço".
* Crie uma chave para sua conta de serviço e baixe o arquivo JSON.
* Salve-o no caminho especificado no .env.

# Execução
* 1. Iniciar o servidor Flask:


```bash 
python app.py
```
* 2. Acessar a documentação interativa da API (Swagger): Acesse no navegador:
no seu dominio e porta 
exemplo
[seu dominio:porta](http://127.0.0.1:5000.)

# Endpoints da API
##### POST /documents/extract
<p>Este endpoint processa um documento e retorna as informações extraídas.
</p>

*  Request Header:

* Content-Type: application/json

* Body (JSON): 
```json
{
  "document": "path/para/seu/arquivo.pdf/images"
}
```

### Responses
 * 200 (Extração bem-sucedida):
 ```json
 {
  "data": {
    "CHAVEDEACESSO": "3524 0613 4926 6900 0190...",
    "N": "0090185",
    "SERIE": "1"
  }
}

 ```
### 400 (Erro de validação):
```json
{
  "error": "Campo 'document' é obrigatório"
}

```
### 404 (Arquivo não encontrado):

```json
{

  "error": "Caminho do arquivo inválido ou arquivo não encontrado"
}


```

### 500 (Erro interno):

```json
{
  "error": "Erro interno no servidor ou falha ao chamar a API do Google Document AI"
}



```