# main.py
import azure.functions as func
from azure_functions_wsgi import WsgiMiddleware
from app import app  # 导入 Flask app


wsgi_app = WsgiMiddleware(app)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return wsgi_app.handle(req, context)
