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
            return render_template("error.html", 403)

        elif not password:
            return render_template("error.html", 403)

        consulta = db.execute("SELECT * FROM usuarios WHERE username = :username", { "username":request.form.get("username")})
        
        if consulta:
            return render_template("error.html")
        if not check_password_hash(consulta[0][password], password):
            return render_template("error.html")
        
        session["id_usuario"] = consulta[0]["id_usuario"]

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
            return "usuario disponible"

        contra = generate_password_hash(contra)
        nuevo_usuario = db.execute("""INSERT INTO usuarios(password, username) VALUES(:password, :username) """,{" username": usser, "password": contra}).fetchone()

        db.commit()

       # nuevo_usuario = db.execute("SELECT id_usuario FROM usuarios  WHERE username = :usser", usser=usser).fetchone()
        #nuevo_usuario=nuevo_usuario[0]
        #print(nuevo_usuario)
        session["id_usuario"] = nuevo_usuario[0]
        session["ussername"]= nuevo_usuario[1]
        flash("Registrado Exitosamente!")

        return redirect(url_for("index"))
    else:
        return render_template("register.html")

@app.route("/")
def index():
    return render_template("index.html")
