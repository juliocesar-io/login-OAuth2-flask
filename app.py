import os

from flask import Flask, jsonify
from proveedor import GoogleLogin, LinkedInLogin, FacebookLogin


"""

El protocolo a utilizar para hacer login con los 3 provedores sera ** OAuth 2.0 **, es decir que el proceso
para cada uno de los proovedores sera el mismo y con cada uno de ellos usaremos un id del cliente y una llave
secreta.

Lo único que varía en cada proveedor son los 'endpoints' o urls donde se hacen las peticiones,
vease el directorio 'proveedor' y vera que cada uno de estos tiene sus atributos respectivos,
cada proveedor hereda de la clase base 'OAuth2Login' que tiene la definicion de los procedimientos
estándares del protocolo.

"""

#Definición de variables de entorno, usa aqui tus API keys.

# Google
os.environ["GOOGLE_LOGIN_CLIENT_ID"] = "-"
os.environ["GOOGLE_LOGIN_CLIENT_SECRET"] = "-"
# Linkedin
os.environ["LINKEDIN_LOGIN_CLIENT_ID"] = "-"
os.environ["LINKEDIN_LOGIN_CLIENT_SECRET"] = "-"
# Facebook
os.environ["FACEBOOK_LOGIN_CLIENT_ID"] = "-"
os.environ["FACEBOOK_LOGIN_CLIENT_SECRET"] = "-"



# Configuracion de la app

app = Flask(__name__)
app.config.update(
  SECRET_KEY="x34sdfm34",
)

"""
Se crea un tupla de llave-valor que luego se itera en el diccionario app.config donde se alamcena
el par de tokens de cada proveedor para uso gobal en la app.
"""

for config in (
  "GOOGLE_LOGIN_CLIENT_ID",
  "GOOGLE_LOGIN_CLIENT_SECRET",
  "LINKEDIN_LOGIN_CLIENT_ID",
  "LINKEDIN_LOGIN_CLIENT_SECRET",
  "FACEBOOK_LOGIN_CLIENT_ID",
  "FACEBOOK_LOGIN_CLIENT_SECRET"

):app.config[config] = os.environ[config]


# Se instancia cada una de clases con las configuraciones repectivas para cada proveerdor.

google_login = GoogleLogin(app)
linkedin_login = LinkedInLogin(app)
facebook_login = FacebookLogin(app)


# Definicion de la ruta raiz

"""
En la ruta raiz se retorna un HTML con enlaze a las 3 opciones de login, mateniendo el minimalismo, se usa la
funcion 'format' para hacer render de las urls de autorizacion en su orden definición en los parámetros de esta
y la aparición de las llaves en los hrefs.
"""


@app.route("/")
def index():
  return """
<html>
<a href="{}">Login con Google</a> <br>
<a href="{}">Login con Linkedin</a> <br>
<a href="{}">Login con Facebook</a> <br>
""".format(google_login.authorization_url(), linkedin_login.authorization_url(), facebook_login.authorization_url())


"""
Luego que alguna opción de login es selecionada se responde con una fallo o con exito
para el cual se responde con el JSON retornado por el API de cada proveedor utilizando la funcion 'jsonify'

Las funciones a continación son implementaciones de la funciones login_success y login_failure definidas en la
clase base OAuth2Login, con esto podemos cambiar el comportamiento en la respuesta dependiendo de cada proveedor
almacenarlo en una base de datos y mostrar un perfil, foto etc. Pero para el objetivo de esta practica, solo se muestra
la respuesta exitosa con la informacion del usuario (almacenada en la variable 'profile') en formato JSON tal cual como
lo envia el API del proveedor.

"""

@google_login.login_success
def login_success(token, profile):
  return jsonify(token=token, profile=profile)

@google_login.login_failure
def login_failure(e):
  return jsonify(error=str(e))

@linkedin_login.login_success
def login_success(token, profile):
  return jsonify(token=token, profile=profile)

@linkedin_login.login_failure
def login_failure(e):
  return jsonify(error=str(e))

@facebook_login.login_success
def login_success(token, profile):
  return jsonify(token=token, profile=profile)

@facebook_login.login_failure
def login_failure(e):
  return jsonify(error=str(e))


if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
