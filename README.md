# API Embrapa - Tech Challenge FIAP

API desenvolvida para o desafio Tech Challenge FIAP, fornecendo acesso a dados públicos da Embrapa sobre produção, processamento, comercialização, importação e exportação de vinhos no Brasil.

## Descrição do Projeto
A API faz a leitura dos dados diretamente dos arquivos CSV da Embrapa, com fallback para URLs alternativas (Web Archive) ou cache local em JSON, garantindo alta disponibilidade e resiliência no acesso.

## Tecnologias Utilizadas
- Python 3
- Flask
- Flask-RESTful
- Flask-JWT-Extended - para autenticação
- Flasgger (Swagger UI)
- Pandas

## Como Executar o Projeto

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/lucianalima777/tech-challenge-2025.git
   cd tech-challenge-2025
   ```

2. **Crie um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação:**
   ```bash
   python app.py
   ```

A API estará disponível em `http://localhost:5000`.

## Autenticação

A API utiliza autenticação JWT. Para acessar os endpoints protegidos, siga os passos:

1. **Obtenha o token:**
   - Endpoint: `POST /login`
   - Payload:
     ```json
     {
       "usuario": "admin",
       "senha": "1234"
     }
     ```
   - Resposta:
     ```json
     {
       "token": "<seu_token_aqui>"
     }
     ```

2. **Utilize o token nos endpoints protegidos:**
   - Adicione o header:
     ```
     Authorization: Bearer <seu_token_aqui>
     ```

## Documentação Interativa (Swagger)

Acesse a documentação interativa da API pelo Swagger em:

```
http://localhost:5000/apidocs
```

Nela, é possível testar todos os endpoints diretamente pelo navegador.

## Endpoints Disponíveis

- `POST /login` - Autenticação e obtenção do token JWT.
- `GET /producao` - Dados de produção (protegido).
- `GET /processamento` - Dados de processamento (protegido).
- `GET /comercializacao` - Dados de comercialização (protegido).
- `GET /importacao` - Dados de importação (protegido).
- `GET /exportacao` - Dados de exportação (protegido).

Todos os endpoints (exceto `/login`) exigem o token JWT no header `Authorization`.

## Exemplo de Uso com curl

```bash
# 1. Obtenha o token
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"usuario": "admin", "senha": "1234"}'

# 2. Use o token para acessar um endpoint protegido
curl http://localhost:5000/producao \
  -H "Authorization: Bearer <seu_token_aqui>"
```

## Observações
- Credenciais de teste: `usuario: admin`, `senha: 1234`
- Os dados são extraídos diretamente dos arquivos CSV públicos da Embrapa.
- Em caso de dúvidas, utilize o Swagger em `/apidocs` para explorar e testar a API. 
- A ordem dos campos exibida nos exemplos do Swagger pode variar por limitação da ferramenta, mas isso não afeta a funcionalidade dos endpoints.