import azure.functions as func
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Banco de dados
DATABASE_URL = (
    "mssql+pyodbc://server-master:qazwsx123."
    "@server-ada-projeto-final.database.windows.net:1433/produtos"
    "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Modelo
class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), unique=True, nullable=False)

# Garantir que o banco de dados exista
Base.metadata.create_all(bind=engine)


def main(req: func.HttpRequest) -> func.HttpResponse:
    path = req.route_params.get('path') or ''
    method = req.method.upper()

    session = SessionLocal()
    try:
        # GET /produtos ou GET /produto
        if method == "GET":
            if path.isdigit():
                produto = session.query(Produto).get(int(path))
                if not produto:
                    return func.HttpResponse('{"error":"Produto não encontrado"}', status_code=404, mimetype="application/json")
                return func.HttpResponse(f'{{"id":{produto.id},"nome":"{produto.nome}"}}', status_code=200, mimetype="application/json")
            else:
                produtos = session.query(Produto).all()
                produtos_list = [{"id": p.id, "nome": p.nome} for p in produtos]
                return func.HttpResponse(str(produtos_list).replace("'", '"'), status_code=200, mimetype="application/json")

        # POST /produtos
        elif method == "POST":
            dados = req.get_json()
            novo_produto = Produto(nome=dados['nome'])
            session.add(novo_produto)
            session.commit()
            return func.HttpResponse(f'{{"id":{novo_produto.id},"nome":"{novo_produto.nome}"}}', status_code=201, mimetype="application/json")

        # PUT /produtos/{id}
        elif method == "PUT":
            if not path.isdigit():
                return func.HttpResponse('{"error":"ID inválido"}', status_code=400, mimetype="application/json")
            produto = session.query(Produto).get(int(path))
            if not produto:
                return func.HttpResponse('{"error":"Produto não encontrado"}', status_code=404, mimetype="application/json")
            dados = req.get_json()
            produto.nome = dados['nome']
            session.commit()
            return func.HttpResponse(f'{{"id":{produto.id},"nome":"{produto.nome}"}}', status_code=200, mimetype="application/json")

        # DELETE /produtos/{id}
        elif method == "DELETE":
            if not path.isdigit():
                return func.HttpResponse('{"error":"ID inválido"}', status_code=400, mimetype="application/json")
            produto = session.query(Produto).get(int(path))
            if not produto:
                return func.HttpResponse('{"error":"Produto não encontrado"}', status_code=404, mimetype="application/json")
            session.delete(produto)
            session.commit()
            return func.HttpResponse(f'{{"message":"Produto {produto.id} deletado com sucesso"}}', status_code=200, mimetype="application/json")

        else:
            return func.HttpResponse('{"error":"Método não permitido"}', status_code=405, mimetype="application/json")

    except IntegrityError:
        session.rollback()
        return func.HttpResponse('{"error":"Produto com esse nome já existe"}', status_code=409, mimetype="application/json")
    except Exception as e:
        session.rollback()
        return func.HttpResponse(f'{{"error":"{str(e)}"}}', status_code=500, mimetype="application/json")
    finally:
        session.close()
