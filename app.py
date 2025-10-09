# app.py

import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
import config

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- FUNÇÃO PARA CONECTAR AO BANCO DE DADOS ---
def get_db_connection():
    try:
        return mysql.connector.connect(**config.DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

# --- ROTA DE LOGIN ---
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db_connection()
        if db is None:
            error = "Erro de conexão com o banco de dados. Tente novamente mais tarde."
            return render_template("login.html", error=error)

        cursor = db.cursor(dictionary=True)
        
        # A consulta busca o usuário e a senha para autenticação
        query = "SELECT * FROM Usuarios WHERE USUARIO = %s AND SENHA = %s"
        cursor.execute(query, (username, password))
        user_data = cursor.fetchone()

        cursor.close()
        db.close()

        if user_data:
            session["username"] = user_data["USUARIO"]
            # Armazena todos os dados do BD, incluindo os links do BI
            session["user_data"] = user_data 
            return redirect(url_for("dashboard"))
        else:
            error = "Usuário ou senha incorretos. Tente novamente."
    
    return render_template("login.html", error=error)

# --- ROTA DO PAINEL ---
@app.route("/dashboard")
@app.route("/dashboard/<bi_key>")
def dashboard(bi_key=None):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_data = session.get("user_data", {})
    
    bi_url = None
    error_message = None
    
    # Mapeia as chaves dos relatórios para as colunas do banco de dados
    report_mapping = {
        "dp": "DP",
        "fiscal": "FISCAL",
        "contabil": "CONTABIL",
        "produtos": "PRODUTOS"
    }

    # Gera a lista COMPLETA de relatórios para exibir TODOS os botões
    available_reports = []
    for key, data in config.REPORTS.items():
        available_reports.append({
            "key": key,
            "name": data.get("name")
        })

    # Se uma chave de BI foi especificada na URL, tenta encontrar o link
    if bi_key and bi_key in report_mapping:
        column_name = report_mapping[bi_key]
        # Pega o link do BI da sessão
        bi_url = user_data.get(column_name) 
        
        if not bi_url:
            # Mensagem de erro aprimorada
            error_message = f"Você não tem permissão de acesso ao relatório de {config.REPORTS[bi_key]['name']}."

    # Envia também a chave do relatório ativo para destacar o botão no menu
    return render_template(
        "dashboard.html",
        bi_url=bi_url,
        error=error_message,
        available_reports=available_reports,
        username=username,
        active_key=bi_key # Adicionado para destacar o botão ativo
    )

# --- OUTRAS ROTAS ---
@app.route("/forgot-password")
def forgot_password():
    info_message = "Entre em contato com o suporte ao cliente."
    return render_template("login.html", info_message=info_message)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# (Opcional) Healthcheck para plataformas de deploy
@app.get("/health")
def health():
    return {"status": "ok"}, 200
