from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oauth2_scheme
from models import db
from sqlalchemy.orm import sessionmaker, Session
from models import Usuario
from jose import JWTError, jwt


def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()


def verificar_token(token: str = Depends(oauth2_scheme), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = dic_info.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Token inválido: usuário não identificado.")
        id_usuario = int(sub)
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Acesso negado, verifique a validade do token!")
    # verificar se o token é válido
    # extrair o usuário do token
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso inválido!")
    return usuario