from fastapi import FastAPI
from  passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

def get_required_env(var_name: str) -> str:
	env_value = os.getenv(var_name)
	if not env_value:
		raise RuntimeError(f"A variável de ambiente {var_name} não foi definida.")
	return env_value


SECRET_KEY = get_required_env("SECRET_KEY")
ALGORITHM = get_required_env("ALGORITHM")

try:
	ACCESS_TOKEN_EXPIRE_MINUTES = int(get_required_env("ACCESS_TOKEN_EXPIRE_MINUTES"))
except ValueError as exc:
	raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES deve ser um número inteiro.") from exc

app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-form")
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
