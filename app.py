#Importação de bibliotecas
from flask import Flask, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import pandas as pd
from flasgger import Swagger, swag_from
import os
import json

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'TechChallenge2025'
#Swagger
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Tech Challenge - API para acesso a dados Embrapa",
        "description": "API para acesso aos dados Embrapa",
        "version": "1.0.0"
    },
    "basePath": "/",
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
        }
    },
    "tags": [
    {
        "name": "Autenticação",
        "description": "Endpoints de autenticação"
    },
    {
        "name": "Produção",
        "description": "Endpoints de produção"
    },
    {
        "name": "Processamento",
        "description": "Endpoints de processamento"
    },
    {
        "name": "Comercialização",
        "description": "Endpoints de comercialização"
    },
    {
        "name": "Importação",
        "description": "Endpoints de importação"
    },
    {
        "name": "Exportação",
        "description": "Endpoints de exportação"
    },
    {
        "name": "Admin",
        "description": "Endpoints de administração"
    }
]
}

swagger = Swagger(app, template=swagger_template)
jwt = JWTManager(app)
api = Api(app)

# Dicionário de fontes com fontes oficiais e alternativas
SOURCES = {
    "producao": {
        "url": "http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv",
        "url_alternativa": "https://web.archive.org/web/20240916154529/http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv",
        "json": "dados_cacheados_producao.json",
        "sep": ";"
    },
    "processamento": {
        "url": "http://vitibrasil.cnpuv.embrapa.br/download/ProcessaViniferas.csv",
        "url_alternativa": "https://web.archive.org/web/20240916161047/http://vitibrasil.cnpuv.embrapa.br/download/ProcessaViniferas.csv",
        "json": "dados_cacheados_processamento.json",
        "sep": ";"
    },
    "comercializacao": {
        "url": "http://vitibrasil.cnpuv.embrapa.br/download/Comercio.csv",
        "url_alternativa": "https://web.archive.org/web/20240916163523/http://vitibrasil.cnpuv.embrapa.br/download/Comercio.csv",
        "json": "dados_cacheados_comercializacao.json",
        "sep": ";"
    },
    "importacao": {
        "url": "http://vitibrasil.cnpuv.embrapa.br/download/ImpVinhos.csv",
        "url_alternativa": "https://web.archive.org/web/20240814202758/http://vitibrasil.cnpuv.embrapa.br/download/ImpVinhos.csv",
        "json": "dados_cacheados_importacao.json",
        "sep": "\t"
    },
    "exportacao": {
        "url": "http://vitibrasil.cnpuv.embrapa.br/download/ExpVinho.csv",
        "url_alternativa": "https://web.archive.org/web/20240916171200/http://vitibrasil.cnpuv.embrapa.br/download/ExpVinho.csv",
        "json": "dados_cacheados_exportacao.json",
        "sep": "\t"
    }
}

#Função de download da tabela e criação de cache
def baixar_csv_e_salvar_json(url_csv: str, url_alternativa: str, nome_arquivo: str, sep: str) -> None:
    if not os.path.exists('cache'):
        os.makedirs('cache')
    print('Baixando arquivo: ' + nome_arquivo)
    try:
        try:
            df = pd.read_csv(url_csv, sep=sep, encoding='utf-8')
        except Exception as e_principal:
            if url_alternativa:
                print(f'Falha na principal, tentando alternativa: {url_alternativa}')
                try:
                    df = pd.read_csv(url_alternativa, sep=sep, encoding='utf-8')
                except Exception as e_alt:
                    with open('cache/' + nome_arquivo, 'w', encoding='utf-8') as f:
                        json.dump({'erro': f'Erro na leitura do CSV principal: {str(e_principal)} | alternativa: {str(e_alt)}'}, f, ensure_ascii=False)
                    return
            else:
                with open('cache/' + nome_arquivo, 'w', encoding='utf-8') as f:
                    json.dump({'erro': f'Erro na leitura do CSV principal: {str(e_principal)}'}, f, ensure_ascii=False)
                return
        df.to_json('cache/' + nome_arquivo, orient='records', force_ascii=False)
    except Exception as e:
        with open('cache/' + nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump({'erro': f'Erro inesperado: {str(e)}'}, f, ensure_ascii=False)

def carregar_e_salvar_todos() -> None:
    for fonte in SOURCES.values():
        baixar_csv_e_salvar_json(fonte["url"], fonte.get("url_alternativa", ""), fonte["json"], fonte["sep"])

def ler_json_local(nome_arquivo: str):
    print('Lendo arquivo: ' + nome_arquivo)
    if not os.path.exists('cache/' + nome_arquivo):
        return {'erro': f'Arquivo {nome_arquivo} não encontrado.'}
    try:
        with open('cache/' + nome_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {'erro': f'Erro ao ler o arquivo {nome_arquivo}: {str(e)}'}

# Carregar dados ao iniciar a API
carregar_e_salvar_todos()

class Login(Resource):
    @swag_from({
        'tags': ['Autenticação'],
        'description': 'Realiza login e retorna um token JWT.',
        'parameters': [
            {
                'in': 'body',
                'name': 'body',
                'schema': {
                    'type': 'object',
                    'required': ['usuario', 'senha'],
                    'properties': {
                        'usuario': {'type': 'string'},
                        'senha': {'type': 'string'}
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Token JWT gerado com sucesso',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'token': {'type': 'string'}
                    }
                }
            },
            401: {'description': 'Usuário ou senha inválidos'}
        }
    })
    def post(self):
        dados = request.get_json()
        usuario = dados.get('usuario')
        senha = dados.get('senha')
        if usuario == 'admin' and senha == '1234':
            token = create_access_token(identity=usuario)
            return {"token": token}, 200
        else:
            return {"msg": "Usuário ou senha inválidos"}, 401

class Producao(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['Produção'],
        'description': 'Retorna dados de produção em formato tabular (uma linha por produto/ano).',
        'security': [{'BearerAuth': []}],
        'responses': {
            200: {
                'description': 'Lista tabular de dados de produção',
                'schema': {
                    'type': 'array',
                    'items': {'type': 'object'}
                }
            },
            401: {'description': 'Token JWT ausente ou inválido'}
        }
    })
    def get(self):
        dados = ler_json_local(SOURCES["producao"]["json"])
        if isinstance(dados, dict) and 'erro' in dados:
            return dados
        resultado = []
        for item in dados:
            id_ = item.get('id')
            control = item.get('control')
            produto = item.get('produto')
            for chave, valor in item.items():
                if chave.isdigit():
                    resultado.append({
                        'id': id_,
                        'control': control,
                        'produto': produto,
                        'ano': int(chave),
                        'quantidade': valor
                    })
        return resultado

class Processamento(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['Processamento'],
        'description': 'Retorna dados de processamento em formato tabular (uma linha por produto/ano).',
        'security': [{'BearerAuth': []}],
        'responses': {
            200: {
                'description': 'Lista tabular de dados de processamento',
                'schema': {
                    'type': 'array',
                    'items': {'type': 'object'}
                }
            },
            401: {'description': 'Token JWT ausente ou inválido'}
        }
    })
    def get(self):
        dados = ler_json_local(SOURCES["processamento"]["json"])
        if isinstance(dados, dict) and 'erro' in dados:
            return dados
        resultado = []
        for item in dados:
            cultivar = item.get('cultivar')
            control = item.get('control')
            for chave, valor in item.items():
                if chave.isdigit():
                    resultado.append({
                        'control': control,
                        'cultivar': cultivar,
                        'ano': int(chave),
                        'quantidade': valor
                    })
        return resultado

class Comercializacao(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['Comercialização'],
        'description': 'Retorna dados de comercialização em formato tabular (uma linha por produto/ano).',
        'security': [{'BearerAuth': []}],
        'responses': {
            200: {
                'description': 'Lista tabular de dados de comercialização',
                'schema': {
                    'type': 'array',
                    'items': {'type': 'object'}
                }
            },
            401: {'description': 'Token JWT ausente ou inválido'}
        }
    })
    def get(self):
        dados = ler_json_local(SOURCES["comercializacao"]["json"])
        if isinstance(dados, dict) and 'erro' in dados:
            return dados
        resultado = []
        for item in dados:
            id_ = item.get('id')
            control = item.get('control')
            produto = item.get('Produto')
            for chave, valor in item.items():
                if chave.isdigit():
                    resultado.append({
                        'id': id_,
                        'control': control,
                        'produto': produto,
                        'ano': int(chave),
                        'quantidade': valor
                    })
        return resultado

class Importacao(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['Importação'],
        'description': 'Retorna dados de importação em formato tabular (uma linha por país/ano).',
        'security': [{'BearerAuth': []}],
        'responses': {
            200: {
                'description': 'Lista tabular de dados de importação',
                'schema': {
                    'type': 'array',
                    'items': {'type': 'object'}
                }
            },
            401: {'description': 'Token JWT ausente ou inválido'}
        }
    })
    def get(self):
        dados = ler_json_local(SOURCES["importacao"]["json"])
        if isinstance(dados, dict) and 'erro' in dados:
            return dados
        resultado = []
        for item in dados:
            pais = item.get('País') or item.get('País ') or item.get('Países') or item.get('Pais')
            for chave, valor in item.items():
                if chave.isdigit():
                    resultado.append({
                        'pais': pais,
                        'ano': int(chave),
                        'quantidade': valor
                    })
        return resultado

class Exportacao(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['Exportação'],
        'description': 'Retorna dados de exportação em formato tabular (uma linha por país/ano).',
        'security': [{'BearerAuth': []}],
        'responses': {
            200: {
                'description': 'Lista tabular de dados de exportação',
                'schema': {
                    'type': 'array',
                    'items': {'type': 'object'}
                }
            },
            401: {'description': 'Token JWT ausente ou inválido'}
        }
    })
    def get(self):
        dados = ler_json_local(SOURCES["exportacao"]["json"])
        if isinstance(dados, dict) and 'erro' in dados:
            return dados
        resultado = []
        for item in dados:
            pais = item.get('País') or item.get('País ') or item.get('Países') or item.get('Pais')
            for chave, valor in item.items():
                if chave.isdigit():
                    resultado.append({
                        'pais': pais,
                        'ano': int(chave),
                        'quantidade': valor
                    })
        return resultado

class AtualizarDados(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['Admin'],
        'description': 'Atualiza manualmente todos os arquivos JSON locais com os dados mais recentes das URLs.',
        'security': [{'BearerAuth': []}],
        'responses': {
            200: {'description': 'Dados atualizados com sucesso.'},
            401: {'description': 'Token JWT ausente ou inválido'}
        }
    })
    def post(self):
        carregar_e_salvar_todos()
        return {"msg": "Dados atualizados com sucesso."}, 200

api.add_resource(Login, '/login')
api.add_resource(Producao, '/producao')
api.add_resource(Processamento, '/processamento')
api.add_resource(Comercializacao, '/comercializacao')
api.add_resource(Importacao, '/importacao')
api.add_resource(Exportacao, '/exportacao')
api.add_resource(AtualizarDados, '/atualizar-dados')

if __name__ == '__main__':
    app.run(debug=True)
