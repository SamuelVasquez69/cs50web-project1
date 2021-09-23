from logging import error
import os

from flask import Flask,flash, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/login", methods = ["GET", "POST"])
def login():

    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        #nos aseguramos que haya llenado el username 
        if not username:
            return "campo de Ussername vacio"

        elif not password:
            return "campo de password vacio"

        consulta = db.execute("SELECT * FROM usuarios WHERE username = :username", { "username":request.form.get("username")}).fetchone()
        
        if not consulta:
            return "usuario no registrado"
        if not check_password_hash(consulta[1], password):
            return "password no coinciden"
        
        session["id_usuario"] = consulta
        flash("LOGEADO EXITOSAMENTE")
        return redirect("/")
    else:
         return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():

    session.clear()

    if request.method == "POST":
        usser = request.form.get("username")
        contra = request.form.get("password")

        if not usser:
            return render_template("error.html")

        if not contra:
            return render_template("error.html")

        consulta = db.execute("SELECT * FROM usuarios WHERE username =:usser", {"usser": usser}).fetchone()

        if consulta:
            return "usuario tomado"
        else:
            Contra = generate_password_hash(contra)
            nuevo_usuario = db.execute("INSERT INTO usuarios(password, username) VALUES(:password, :username) ",{"password": Contra,"username": usser})

            db.commit()
            flash("Registrado Exitosamente!")

            return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/")
def index():
    
    consulta = db.execute("SELECT * FROM books").fetchall()
    
    return render_template("index.html", libros=consulta)

@app.route("/detalle_libro")
def detallelibro():

    return render_template("detalle_libro.html")
