from flask import Flask, render_template, request, redirect
import sqlite3
import re
import html

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def validar_correo(correo):
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(regex, correo)

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    
    if request.method == "POST":
        try:
            nombre = html.escape(request.form["nombre"].strip())
            correo = html.escape(request.form["correo"].strip())
            password = html.escape(request.form["password"].strip())

            if not nombre or not correo or not password:
                error = "Todos los campos son obligatorios."
            
            elif not validar_correo(correo):
                error = "Correo inválido."

            elif len(password) < 6:
                error = "La contraseña debe tener mínimo 6 caracteres."

            if error:
                return render_template("index.html", error=error)

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)",
                (nombre, correo, password)
            )
            conn.commit()
            conn.close()

            return redirect("/")

        except sqlite3.IntegrityError:
            error = "El correo ya está registrado."
        except Exception:
            error = "Ocurrió un error inesperado."

    conn = get_db_connection()
    usuarios = conn.execute("SELECT nombre, correo FROM usuarios").fetchall()
    conn.close()

    return render_template("index.html", usuarios=usuarios, error=error)

if __name__ == "__main__":
    app.run(debug=False)