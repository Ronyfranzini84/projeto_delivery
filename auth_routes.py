from fastapi import APIRouter, Depends
from models import Usuario
from dependencies import pegar_sessao

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/")
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema.
    """
    return {"mensagem": "Você acessou a rota de autenticação!"}

@auth_router.post("/criar_conta")
async def criar_conta(email: str, senha: str, nome: str, session=Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter_by(Usuario.email==email).first()
    if usuario:
        # já existe um usuario com esse email
        return {"mensagem": "Já existe um usuário com esse email!"}
    else:
        # criar um novo usuario
        novo_usuario = Usuario(nome, email, senha)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": "Usuário cadastrado com sucesso!"}  

    