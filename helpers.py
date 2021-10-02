
import requests
from flask import redirect, session
from functools import wraps

def libro(consulta):
    
    diccionarios = []

    if consulta:
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+consulta[0]).json()
        try:
            imagen = response["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
        except KeyError:
            imagen = "../static/50740918_p0_master1200.jpg"
        diccionarios.append({
            "nombre_libro": consulta[1],
            "author": consulta[2],
            "year":consulta[3],
            "imagen": imagen,
            "id_libro": consulta[0]
        })
        print(diccionarios)
    return diccionarios

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

