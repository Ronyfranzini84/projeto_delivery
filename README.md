# 🍕 Projeto Delivery API

API REST para gerenciamento de pedidos de delivery, desenvolvida com **FastAPI** e **SQLAlchemy**.

---

## 📋 Tecnologias

| Tecnologia | Versão | Uso |
|---|---|---|
| FastAPI | 0.115.12 | Framework principal |
| SQLAlchemy | 2.0.40 | ORM / banco de dados |
| SQLite | — | Banco de dados local (`banco.db`) |
| Alembic | 1.18.4 | Migrations |
| python-jose | 3.4.0 | Geração e validação de JWT |
| passlib + bcrypt | 1.7.4 + 4.0.1 | Hash de senhas |
| Pydantic | 2.11.4 | Validação de schemas |
| python-dotenv | 1.1.0 | Variáveis de ambiente |
| uvicorn | 0.34.2 | Servidor ASGI |

---

## ⚙️ Configuração

### 1. Clonar e criar ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Executar as migrations

```bash
alembic upgrade head
```

### 5. Iniciar o servidor

```bash
uvicorn main:app --reload
```

A API ficará disponível em: `http://127.0.0.1:8000`

Documentação interativa: `http://127.0.0.1:8000/docs`

---

## 🔐 Autenticação

A API usa **JWT (JSON Web Token)** com dois tipos de token:

- **Access Token** — curta duração (padrão: 30 min), usado em todas as rotas protegidas
- **Refresh Token** — longa duração (7 dias), usado apenas para renovar o access token

### Fluxo de autenticação

```
1. Criar conta  →  POST /auth/criar_conta
2. Fazer login  →  POST /auth/login  (retorna access_token + refresh_token)
3. Usar rotas   →  Header: Authorization: Bearer <access_token>
4. Renovar token → GET /auth/refresh  (Header: Authorization: Bearer <refresh_token>)
```

---

## 📌 Endpoints

### Auth — `/auth`

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| GET | `/auth/` | Não | Rota padrão |
| POST | `/auth/criar_conta` | Não | Cadastrar novo usuário |
| POST | `/auth/login` | Não | Login via JSON → retorna access + refresh token |
| POST | `/auth/login-form` | Não | Login via form (compatível com Swagger) |
| GET | `/auth/refresh` | Refresh Token | Gera novo access token |

---

### Pedidos — `/pedidos`

> Todas as rotas de pedidos exigem **Access Token** no header.

| Método | Rota | Admin? | Descrição |
|---|---|---|---|
| GET | `/pedidos/` | Não | Rota padrão |
| POST | `/pedidos/pedido` | Não | Criar novo pedido |
| GET | `/pedidos/pedido/{id_pedido}` | Não* | Visualizar um pedido |
| POST | `/pedidos/pedido/finalizar/{id_pedido}` | Não* | Finalizar pedido |
| POST | `/pedidos/pedido/cancelar/{id_pedido}` | Não* | Cancelar pedido |
| GET | `/pedidos/usuario/{id_usuario}/pedidos` | Não* | Listar todos os pedidos de um usuário |
| GET | `/pedidos/listar` | **Sim** | Listar todos os pedidos do sistema |
| GET | `/pedidos/tabela-total-compra` | Não** | Tabela com total de compra |
| POST | `/pedidos/pedido/adicionar-item/{id_pedido}` | Não* | Adicionar item ao pedido |
| POST | `/pedidos/pedido/remover-item/{id_item_pedido}` | Não* | Remover item do pedido |

> \* Usuário só pode acessar/modificar os próprios pedidos. Admin acessa qualquer pedido.  
> \*\* Usuário vê apenas os próprios pedidos. Admin vê todos.

---

## 📦 Exemplos de Request/Response

### Criar conta

**POST** `/auth/criar_conta`
```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "minhasenha123",
  "ativo": true,
  "admin": false
}
```
```json
{
  "mensagem": "Usuário cadastrado com sucesso: joao@email.com!"
}
```

---

### Login

**POST** `/auth/login`
```json
{
  "email": "joao@email.com",
  "senha": "minhasenha123"
}
```
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "Bearer"
}
```

---

### Criar pedido

**POST** `/pedidos/pedido`  
Header: `Authorization: Bearer <access_token>`
```json
{}
```
```json
{
  "id": 1,
  "status": "PENDENTE",
  "usuario": 1,
  "preco": 0.0
}
```

---

### Adicionar item ao pedido

**POST** `/pedidos/pedido/adicionar-item/1`  
Header: `Authorization: Bearer <access_token>`
```json
{
  "sabor": "Calabresa",
  "tamanho": "Grande",
  "preco_unitario": 45.90,
  "quantidade": 2
}
```
```json
{
  "mensagem": "Item adicionado ao pedido com sucesso!",
  "item_pedido": 1,
  "preco_pedido": 91.8
}
```

---

### Finalizar pedido

**POST** `/pedidos/pedido/finalizar/1`  
Header: `Authorization: Bearer <access_token>`
```json
{
  "mensagem": "Pedido 1 finalizado com sucesso!",
  "pedido": {
    "id": 1,
    "status": "FINALIZADO",
    "usuario": 1,
    "preco": 91.8,
    "quantidade_itens": 2
  }
}
```

---

### Tabela total de compra

**GET** `/pedidos/tabela-total-compra`  
Header: `Authorization: Bearer <access_token>`
```json
[
  {
    "id_pedido": 1,
    "id_usuario": 1,
    "quantidade_itens": 2,
    "total_compra": 91.8,
    "status": "FINALIZADO"
  }
]
```

---

## 🗄️ Estrutura do Banco de Dados

```
usuarios
├── id          (PK, autoincrement)
├── nome        (String)
├── email       (String, not null)
├── senha       (String, hash bcrypt)
├── ativo       (Boolean)
└── admin       (Boolean, default=False)

pedidos
├── id          (PK, autoincrement)
├── status      (String: PENDENTE | FINALIZADO | CANCELADO)
├── usuario     (FK → usuarios.id)
└── preco       (Float, calculado automaticamente)

itens_pedido
├── id              (PK, autoincrement)
├── quantidade      (Integer)
├── sabor           (String)
├── tamanho         (String)
├── preco_unitario  (Float)
└── pedido          (FK → pedidos.id, cascade delete)
```

---

## 📁 Estrutura do Projeto

```
projeto_delivery/
├── main.py             # Entry point, configuração do app e variáveis de ambiente
├── models.py           # Modelos SQLAlchemy (Usuario, Pedido, ItemPedido)
├── schemas.py          # Schemas Pydantic para request/response
├── dependencies.py     # Dependências de sessão e validação de token
├── auth_routes.py      # Rotas de autenticação (/auth)
├── order_routes.py     # Rotas de pedidos (/pedidos)
├── requirements.txt    # Dependências do projeto
├── alembic.ini         # Configuração do Alembic
└── alembic/
    └── versions/       # Migrations
```

---

## 🔒 Regras de Negócio

- Não é possível **finalizar** um pedido sem itens
- Não é possível **finalizar** um pedido com status `CANCELADO`
- Usuários comuns só podem visualizar e modificar os **próprios pedidos**
- Administradores têm acesso total a todos os pedidos e usuários
- O preço do pedido é **recalculado automaticamente** ao adicionar ou remover itens
- Ao excluir um pedido, todos os seus itens são excluídos em cascata
