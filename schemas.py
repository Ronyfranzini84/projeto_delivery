from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: bool 
    admin: bool 

    class Config:
        from_attributes = True

class PedidoSchema(BaseModel):
    usuario: Optional[int] = None

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True

class ItemPedidoSchema(BaseModel):
    id_pedido: Optional[int] = None
    sabor: str
    tamanho: str
    preco_unitario: float
    quantidade: int

    class Config:
        from_attributes = True


class PedidoResumoSchema(BaseModel):
    id: int
    status: str
    usuario: int
    preco: float

    class Config:
        from_attributes = True


class TabelaTotalCompraSchema(BaseModel):
    id_pedido: int
    id_usuario: int
    quantidade_itens: int
    total_compra: float
    status: str

    class Config:
        from_attributes = True