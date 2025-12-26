import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
import config
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(24)

bcrypt = Bcrypt(app) 

def get_db_connection():
    try:
        return mysql.connector.connect(**config.DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

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
        
        query = "SELECT * FROM Usuarios WHERE USUARIO = %s"
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()

        cursor.close()
        db.close()

        if user_data:
            try:
                if bcrypt.check_password_hash(user_data["SENHA"], password):
                    session["username"] = user_data["USUARIO"]
                    session["user_data"] = user_data 
                    return redirect(url_for("dashboard"))
                else:
                    error = "Usuário ou senha incorretos. Tente novamente."
            except ValueError:
                error = "Erro de validação da senha. Contate o administrador."
        else:
            error = "Usuário ou senha incorretos. Tente novamente."
    
    return render_template("login.html", error=error, info_message=None)

@app.route("/dashboard")
@app.route("/dashboard/<bi_key>")
def dashboard(bi_key=None):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_data = session.get("user_data", {})
    
    bi_url = None
    error_message = None
    
    report_mapping = {
        "dp": "DP",
        "fiscal": "FISCAL",
        "contabil": "CONTABIL",
        "produtos": "PRODUTOS"
    }

    available_reports = []
    if hasattr(config, 'REPORTS'): 
        for key, data in config.REPORTS.items():
            available_reports.append({
                "key": key,
                "name": data.get("name")
            })

    if bi_key and bi_key in report_mapping:
        column_name = report_mapping[bi_key]
        bi_url = user_data.get(column_name) 
        
        if not bi_url:
            report_name = config.REPORTS.get(bi_key, {}).get("name", "este relatório")
            error_message = f"Você não tem permissão de acesso ao relatório de {report_name}."

    return render_template(
        "dashboard.html",
        bi_url=bi_url,
        error=error_message,
        available_reports=available_reports,
        username=username,
        active_key=bi_key
    )

@app.route("/forgot-password")
def forgot_password():
    info_message = "Entre em contato com o suporte ao cliente."
    return render_template("login.html", info_message=info_message)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/health")
def health():
    return {"status": "ok"}, 200
