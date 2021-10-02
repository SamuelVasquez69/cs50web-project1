from logging import error
import os
import requests
from helpers import libro, login_required

from flask import Flask,flash, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import MethodNotAllowed, default_exceptions
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
        
        session["id_usuario"] = consulta.id_usuario
        session["nombre"]=username
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
    
    consulta = db.execute("SELECT * FROM books LIMIT 15").fetchall()
    diccionarios = []

    for filas in consulta :
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+filas[0]).json()
        try:
            imagen = response["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
        except KeyError:
            imagen = "../static/50740918_p0_master1200.jpg"
        diccionarios.append({
            "nombre_libro": filas[1],
            "author": filas[2],
            "year":filas[3],
            "imagen": imagen,
            "id_libro": filas[0]
        })
    return render_template("index.html", libros=diccionarios)

@app.route("/detalle_libro/<string:id_libro>", methods=["POST","GET"])
@login_required
def detallelibro(id_libro):

    consulta = db.execute("SELECT * FROM books WHERE isbn=:id_libro",{"id_libro":id_libro}).fetchone()
    diccionarios = []
    diccionarios = libro(consulta)

    usuario_actual = session["id_usuario"]
    comment  =  request.form.get("cajaComentario")
    try:
        rating = request.form.get("valor_rating")
    except DataError:
        rating = 0

    if comment:
        db.execute("""INSERT INTO resenas (rating, resena, id_usuario, id_isbn) 
        VALUES (:rating, :resena, :id_usuario, :id_isbn)""",
        {"rating":rating, "resena":comment, "id_usuario":usuario_actual, "id_isbn":id_libro})

    db.commit()
    comentarios = db.execute("""SELECT * FROM usuarios JOIN resenas ON usuarios.id_usuario = resenas.id_usuario
                                WHERE id_isbn =:id_isbn""", {"id_isbn": id_libro}).fetchall()
    
    validacion = db.execute(""" SELECT * FROM resenas WHERE id_usuario =:id_usser AND id_isbn =:id_book""",
                            {"id_usser":usuario_actual, "id_book":id_libro}).fetchone()
    confirmacion = False
    if validacion:
        confirmacion = True

    return render_template("detalle_libro.html",libro=diccionarios,comments=comentarios,confirmation=confirmacion)

@app.route("/search" , methods=["POST","GET"])
def search():
    
    if request.method == "POST":
        busqueda = request.form.get("busqueda")

        if not busqueda:
            return "libro no ingresado"
        
        consulta = db.execute("SELECT * FROM books WHERE isbn =:busqueda OR title =:busqueda OR author =:busqueda", {"busqueda":busqueda}).fetchone()
        diccionarios = []
        diccionarios = libro(consulta)
        return render_template("detalle_libro.html",libro=diccionarios)
    else:
        return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/comentario",  methods=["POST","GET"])
def comentario():
    if request.method == "POST":
        comment  =  request.form.get("cajaComentario")
        if not comment:
            return render_template("detalle_libro.html")
        
        consulta = db.execute("INSERT INTO resenas (rating, resena, id_usuario, id_isbn ) VALUES(:rating, :resenas, :id_usuario, :id_isbn)",{})

    return render_template("detalle_libro.html")
