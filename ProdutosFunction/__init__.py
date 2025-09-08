import azure.functions as func
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 
    "mssql+pyodbc://server-master:qazwsx123."
    "@server-ada-projeto-final.database.windows.net:1433/produtos"
    "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Produto(db.Model):
    __tablename__ = "produtos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WSGIMiddleware(app).handle(req, context)


@app.route("/api/produtos", methods=["GET"])
def consultar_produtos():
    produtos = Produto.query.all()
    return jsonify([{"id": p.id, "nome": p.nome} for p in produtos]), 200

@app.route("/api/produtos/<int:id>", methods=["GET"])
def consultar_produto(id):
    produto = Produto.query.get(id)
    if produto:
        return jsonify({"id": produto.id, "nome": produto.nome}), 200
    else:
        return jsonify({"error": "Produto não encontrado"}), 404

@app.route("/api/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    nome = dados.get('nome')
    if not nome:
        return jsonify({"error": "Nome é obrigatório"}), 400
    
    novo_produto = Produto(nome=nome)
    try:
        db.session.add(novo_produto)
        db.session.commit()
        return jsonify({"id": novo_produto.id, "nome": novo_produto.nome}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Produto '{nome}' já existe"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    produto = Produto.query.get(id)
    if not produto:
        return jsonify({"error": "Produto não encontrado"}), 404
    
    dados = request.get_json()
    novo_nome = dados.get('nome')
    if not novo_nome:
        return jsonify({"error": "Nome é obrigatório"}), 400
    
    produto.nome = novo_nome
    try:
        db.session.commit()
        return jsonify({"id": produto.id, "nome": produto.nome}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Produto '{novo_nome}' já existe"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/produtos/<int:id>", methods=["DELETE"])
def delete_produto(id):
    produto = Produto.query.get(id)
    if not produto:
        return jsonify({"error": "Produto não encontrado"}), 404
    try:
        db.session.delete(produto)
        db.session.commit()
        return jsonify({"message": f"Produto {id} deletado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400