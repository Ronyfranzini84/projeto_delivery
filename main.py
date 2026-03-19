from fastapi import FastAPI

app = FastAPI()

from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)

# para rodar o nosso código, execuatar no terminal: uvicorn main:app --reload

# endpoint
# dominio.com/ordens/lista 

#   Rest APIs
#   GET - para ler dados
#   POST - para criar dados
#   PUT - para atualizar dados
#   DELETE - para deletar dados
