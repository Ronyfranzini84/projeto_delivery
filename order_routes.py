from fastapi import APIRouter, Depends, HTTPException
from dependencies import pegar_sessao, verificar_token_acesso
from sqlalchemy.orm import Session
from schemas import PedidoSchema, ItemPedidoSchema, PedidoResumoSchema, TabelaTotalCompraSchema
from models import Pedido, Usuario, ItemPedido

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token_acesso)]) # order = pedidos


def usuario_eh_admin(usuario: Usuario) -> bool:
    return bool(getattr(usuario, "admin", False))


def serializar_pedido(pedido: Pedido) -> dict:
    return {
        "id": pedido.id,
        "status": pedido.status,
        "usuario": pedido.usuario,
        "preco": pedido.preco,
        "quantidade_itens": sum(int(getattr(item, "quantidade") or 0) for item in pedido.itens),
    }

@order_router.get("/") 
async def pedidos(usuario: Usuario = Depends(verificar_token_acesso)):
    """
    Essa é a rota padrão de pedidos do nosso sistema.
    Todas as rotas dos pedidos precisam de autenticação.
    """
    return {"mensagem": "Você acessou a rota de pedidos!"}

@order_router.post("/pedido", response_model=PedidoResumoSchema)
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token_acesso)):
    novo_pedido = Pedido(usuario=usuario.id)
    session.add(novo_pedido)
    session.commit()
    session.refresh(novo_pedido)
    return serializar_pedido(novo_pedido)


@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int,
                            session: Session = Depends(pegar_sessao),
                            usuario: Usuario = Depends(verificar_token_acesso)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado!")
    id_usuario_pedido = int(getattr(pedido, "usuario"))
    if not usuario_eh_admin(usuario) and id_usuario_pedido != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para visualizar este pedido!")
    return serializar_pedido(pedido)


@order_router.get("/usuario/{id_usuario}/pedidos")
async def visualizar_pedidos_usuario(id_usuario: int,
                                     session: Session = Depends(pegar_sessao),
                                     usuario: Usuario = Depends(verificar_token_acesso)):
    id_usuario_logado = int(getattr(usuario, "id"))
    if not usuario_eh_admin(usuario) and id_usuario_logado != id_usuario:
        raise HTTPException(status_code=403, detail="Você não tem permissão para visualizar pedidos deste usuário!")
    pedidos = session.query(Pedido).filter(Pedido.usuario == id_usuario).all()
    return {
        "id_usuario": id_usuario,
        "total_pedidos": len(pedidos),
        "pedidos": [serializar_pedido(pedido) for pedido in pedidos],
    }


@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int,
                           session: Session = Depends(pegar_sessao),
                           usuario: Usuario = Depends(verificar_token_acesso)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado!")
    id_usuario_pedido = int(getattr(pedido, "usuario"))
    if not usuario_eh_admin(usuario) and id_usuario_pedido != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para finalizar este pedido!")
    status_pedido = str(getattr(pedido, "status"))
    if status_pedido == "CANCELADO":
        raise HTTPException(status_code=400, detail="Não é possível finalizar um pedido cancelado!")
    if len(pedido.itens) == 0:
        raise HTTPException(status_code=400, detail="Não é possível finalizar pedido sem itens!")
    pedido.status = "FINALIZADO"
    session.commit()
    session.refresh(pedido)
    return {
        "mensagem": f"Pedido {pedido.id} finalizado com sucesso!",
        "pedido": serializar_pedido(pedido),
    }

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, sesssion: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token_acesso)):
    pedido = sesssion.query(Pedido).filter(Pedido.id ==id_pedido).first()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado!")
    id_usuario_pedido = int(getattr(pedido, "usuario"))
    if not usuario_eh_admin(usuario) and id_usuario_pedido != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para cancelar este pedido!")
    pedido.status = "CANCELADO"
    sesssion.commit()
    return {
        "mensagem": f"Pedido {pedido.id} cancelado com sucesso!",
        "pedido": serializar_pedido(pedido)
        }

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token_acesso)):
    if not usuario_eh_admin(usuario):
        raise HTTPException(status_code=403, detail="Você não tem permissão para listar os pedidos!")
    else:
        pedidos = session.query(Pedido).all()
        return {
            "pedidos": [
                {
                    "id": pedido.id,
                    "status": pedido.status,
                    "usuario": pedido.usuario,
                    "preco": pedido.preco
                }
                for pedido in pedidos
            ]
        }


@order_router.get("/tabela-total-compra", response_model=list[TabelaTotalCompraSchema])
async def tabela_total_compra(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token_acesso)):
    if usuario_eh_admin(usuario):
        pedidos = session.query(Pedido).all()
    else:
        pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()

    tabela = []
    for pedido in pedidos:
        quantidade_itens = sum(int(getattr(item, "quantidade") or 0) for item in pedido.itens)
        total_compra = float(getattr(pedido, "preco") or 0)
        tabela.append(
            {
                "id_pedido": pedido.id,
                "id_usuario": pedido.usuario,
                "quantidade_itens": quantidade_itens,
                "total_compra": total_compra,
                "status": pedido.status,
            }
        )
    return tabela
    
@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_Item_pedido(id_pedido: int, 
                            item_pedido_schema: ItemPedidoSchema,
                            session: Session = Depends(pegar_sessao),
                            usuario: Usuario = Depends(verificar_token_acesso)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if pedido is None:
        raise HTTPException(status_code=400, detail="Pedido não encontrado!")
    id_usuario_pedido = int(getattr(pedido, "usuario"))
    if not usuario_eh_admin(usuario) and id_usuario_pedido != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para alterar este pedido!")
    item_pedido = ItemPedido(item_pedido_schema.quantidade,
                            item_pedido_schema.sabor,
                            item_pedido_schema.tamanho,
                            item_pedido_schema.preco_unitario, id_pedido)
    session.add(item_pedido)
    session.flush()
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": f"Item adicionado ao pedido com sucesso!",
        "item_pedido": item_pedido.id,
        "preco_pedido": pedido.preco
    }

@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_Item_pedido(id_item_pedido: int,
                            session: Session = Depends(pegar_sessao),
                            usuario: Usuario = Depends(verificar_token_acesso)):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    if item_pedido is None:
        raise HTTPException(status_code=400, detail="Item do pedido não encontrado!")
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    if pedido is None:
        raise HTTPException(status_code=400, detail="Pedido não encontrado!")
    id_usuario_pedido = int(getattr(pedido, "usuario"))
    if not usuario_eh_admin(usuario) and id_usuario_pedido != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para alterar este pedido!")
    session.delete(item_pedido)
    session.flush()
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": f"Item removido do pedido com sucesso!",
        "pedido": serializar_pedido(pedido)
    }