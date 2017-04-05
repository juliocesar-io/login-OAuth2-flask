# UDEM: Universidad de Monterrey
![Imgur](http://www.udem.edu.mx/Style%20Library/UDEM_Images/header/logo_udem.gif)
### DIVISIÓN DE INGENIERÍA Y TECNOLOGÍA
### DESARROLLO DE APLICACIONES WEB
### Ejercicio de log-in con terceros
#### Andrea Puente - 317000 | Juan Issac - 350629 
#### Julio César   - 568095 | Luca Grossmann - 561080


Login-OAuth2-Flask
==================

En esta practica se realizó un módulo Login con el protocolo OAuth 2.0 utilizando 3 proveedores diferentes (Google, Linkedin y Facebook).

## Requerimientos

- flask
- requests-oauthlib

Para instalar los requerimientos, simplemente ejecutar el siguiente comando:

```bash
pip install -r requirements.txt
```

## Configuracion de API's

Lo primero que hicimos fué registrar una aplicacion con cada proveedor, obtener las configuraiones y llaves de acceso.

**Google**

Ir a [Google APIs](https://console.developers.google.com/apis/credentials) seleccionar "OAuth cliente Id" para generar tokens de acceso al API.

![3](http://i.imgur.com/1Gdtsmv.png)

Definir un nombre, generara dos llaves: una id de cliente y un token de autenticación como en la imágen indicada.

Luego, agregar una URI autorizada para hacer la redirección del login.

![4](http://i.imgur.com/opIkoVj.png)

En app.py definimos las variables de entorno respectivas:

```python
os.environ["GOOGLE_LOGIN_CLIENT_ID"] = "tu_id_aqui"
os.environ["GOOGLE_LOGIN_CLIENT_SECRET"] = "tu_token_aqui"
```

Y abstraemos las configuraciones del API de Google en nuestra clase GoogleLogin con los siguientes atributos:
```python
 default_scope = (
    "https://www.googleapis.com/auth/userinfo.email,"
    "https://www.googleapis.com/auth/userinfo.profile"
 )
 default_redirect_path = "/login/google"

! auth_url = "https://accounts.google.com/o/oauth2/auth"
 token_url = "https://accounts.google.com/o/oauth2/token"
 profile_url = "https://www.googleapis.com/oauth2/v2/userinfo"
```
Con esto queda finalizada la configuración para hacer login con Google.

**Linkedin**

Ir a [Linkedin developers](https://www.linkedin.com/developer/), crear una nueva app, obtener las llaves respectivas y definir el callback URL para OAuth 2.0.

![Imgur](http://i.imgur.com/RLWdR3b.png)
```python
os.environ["LINKEIND_LOGIN_CLIENT_ID"] = "tu_id_aqui"
os.environ["LINKEIND_LOGIN_CLIENT_SECRET"] = "tu_token_aqui"
```

Abstraemos las configuraciones del API en la clase LinkedInLogin.

```python
 default_scope = (
    "r_basicprofile,"
    "r_emailaddress"
 )
 default_redirect_path = "/login/linkedin"

 auth_url = "https://www.linkedin.com/oauth/v2/authorization"
 token_url = "https://www.linkedin.com/oauth/v2/accessToken"
 profile_url = "https://api.linkedin.com/v1/people/~?format=json"
```

**Facebook**

Ir a [Facebook Develoers](), crear una app y obtener las llaves respectivas. 

![Imgur](http://i.imgur.com/t2WoGKa.png)

```python
os.environ["FACEBOOK_LOGIN_CLIENT_ID"] = "tu_id_aqui"
os.environ["FACEBOOK_LOGIN_CLIENT_SECRET"] = "tu_token_aqui"
```

Luego configuramos el Facebook Login.

![Imgur](http://i.imgur.com/YRIiPTm.png)

Y finalmente abstraemos las configuraciones del API en la clase FacebookLogin.

```python
default_scope = (
  "public_profile"
)

default_redirect_path = "/login/facebook"

auth_url = "https://www.facebook.com/dialog/oauth"
token_url = "https://graph.facebook.com/oauth/access_token"
profile_url = "https://graph.facebook.com/me?"
```

## Diseño

La manera en que funciona, es permtir configurar los endpoints para que los usuarios hagan login usando los proveedores mencionados (Google, LinkedIn, Facebook). El programa obtiene un token válido para realizar peticiones a las APIs con el que se puede obtener información de un servidor de recursos. En la **Fig.1** se ilustra el diagrama del funcionamiento de este protocolo.

**Fig.1** Diagrama alto nivel protocolo OAuth 2.0
![Fig.1](http://i.imgur.com/RsKyg2I.png)

El digrama muestra el funcionamiento de alto nivel, mejor ejemplificaado se puede ver un caso de uso del lado usuario en el siguiente diagrama.

**Fig.2** Diagrama de caso de uso Login con OAuth 2.0

![Fig.2](http://i.imgur.com/fLKQkNi.png)

> OAuth 2.0 es considerado un procolo estándar para autorización. Utiliza el estándar RFC 6749, descrito en el sitio oficial [OAuth 2.0](https://oauth.net/2/)

### Clases

Para un diseño reutilizable se generan clases. Primero creamos una clase base llamada `OAuth2Login` que tiene los métodos requeridos para completar un login usando el protocolo OAuth 2.0 ilustrado en la **Fig.1**.

**Fig.3** Diagrama de clases cada proveedor hereda del protocolo OAuth 2.0

![Fig.3](http://i.imgur.com/elA5D36.png)

![Imgur](http://i.imgur.com/7G9i05n.png)



### Clase OAuth2Login

Esta clase recibirá como parámetro las configuración de la app que contiene un diccionario con las llaves de cada uno de los proveedores y será la clase padre como se ilustra en la **Fig.3**.

Con éste diseño garantizamos la modularidad de la aplicación para agregar cualquier otro porveedor y la abstración del protocolo de las configuraciones de cada proveedor.

**Métodos y atributos**

Para la clase `OAuth2Login` el metodo auxiliar `get_config` obtiene los tokens de cada uno de los proveedores usando el contexto de la instacia para obtener el prefijo en la variable `config_prefix`.

:param app:  Arreglo de configuraciones 
:param name: Nombre de la llave en el arreglo
:param default_value: En caso que no exista el valor por defecto en None.
:return: retorna el valor en el diccionario 'config' correpondiente a la indice en 'name'

```python
  def get_config(self, app, name):
    return app.config.get(self.config_prefix + name)
```

Con esto, se identifican cada una del par de llaves da cada proveedor haciendo `get(indice)` en el diccionario `config`, los índices cumplen con el sigueinte patrón:

<:Prefijo proveedor>_CLIENT_ID
<:Prefijo proveedo>_CLIENT_SECRET

Ej: Con el supuesto que el valor `config_prefix` en la instancia de la case es "LINKEDIN_LOGIN_"

```python
  get_config(app, "CLIENT_ID")
  # Retorna el valor LINKEDIN_LOGIN_CLIENT_ID
```
Este valor fue definido en las varibles de entorno en la seccion anterior [Configuracion de API’s]().

Luego, se inicializa la instancia de la clase con el método `init_app` obteniendo las configuraciones y se definen la rutas de redirección para el login correpondiente al de configuracion en el API. 

Como Ejemplo si fuera la instancia de la clase de Facebook:

```python
  def init_app(self, app):

    self.client_id = self.get_config("FACEBOOK_LOGIN_CLIENT_ID")
    # Otras configuraciones 
    ...
    ...
    
    # Define el comportamiento de la URL, en /login/facebook
    # El tercer parametro corresponde al metodo que se ejecuta
    # cuando se hace una peticion a la URL.
    app.add_url_rule(
      "/login/facebook",
      "_facebook_login",
      self.login,
    )

```
## Implementación Protocolo OAuth 2.0
Se describe el funcionamiento de la implementación del protocolo OAuth 2.0 basados en la **Fig.1** y **Fig.2** implementado en el código.

### Paso 1

El primer paso es crear una sesión con el id del cliente correpondiente a "FACEBOOK_LOGIN_CLIENT_ID" para luego pedir autorización al servidor de autenticación y que retorne un token de acceso.

```python
  def session(self):
    return OAuth2Session(
      self.client_id,
      redirect_uri=self.redirect_uri,
      scope=self.scope,
    )
```

El método abre una sesión con el `client_id`, la url de redirección `redirect_uri` y el alcance de permisos del API `scope`. Cuando el cliente pusla el link es enviado al sitio de proveedor, registra sus credenciales y el servidor de autenticación del proveedor valida la sesión de usuario haciendo la redirección a la aplicacion usando `redirect_uri`. El primer paso del procolo OAuth 2.0 está ilustrado en la **Fig.4**.


**Fig.4**.Primer paso del procolo OAuth 2.0

![Imgur](http://i.imgur.com/eq2STMC.png)

### Paso 2
Luego, con la sesisón activa hacemos una petecion para obtener el token de acceso para el servidor utilizando ahora el `client_secret` correpondiente para el ejemplo a "FACEBOOK_LOGIN_CLIENT_SECRET" y la URL correpondiente para obtener el token, llamado `token_url`  correspondiente a "https://graph.facebook.com/oauth/access_token".

```python
 def get_token(self):
 # Obtenemos la sesion activa
 sess = self.session()
    # Luego obtenemos el token de acceso
    try:
      sess.fetch_token(
        self.token_url,
        code=request.args["code"],
        client_secret=self.client_secret,
      )
    except:
    ..
    .
```
El  método anterior obtiene el token de acceso utilizando el endpoint definido en `token_url` de la clase instanciada y la llave secreta del API extraida del diccionario `config`, identificada en el método como `client_secret`. Correponde al segundo paso del protocolo OAuth 2.0 ilustrado en la **Fig.5**.

**Fig.5**. Segundo paso del procolo OAuth 2.0
![Imgur](http://i.imgur.com/ELjnBpM.png)

### Paso 3
Finalmente, para obtener la información del usuario del servidor de recursos utilizamos el token de acceso ya en la sesión y la `profile_url` donde se realiza la consulta.

```python
  def get_profile(self, sess):
    """
    Funcion para obtener datos del usuario y retonarlos como JSON.
    """
    resp = sess.get(self.profile_url)
    resp.raise_for_status()
    return resp.json()
```

En la funcion anterior se realiza una petición GET al endpoint `profile_url` y se retorna la respuesta en JSON. Corresponde al paso final del protocolo OAuth 2.0 ilustrado en la **Fig.6**.

**Fig.6**. Paso final  del procolo OAuth 2.0
![Imgur](http://i.imgur.com/AC7q8bH.png)


### Clase configuracion proveedor

Esta clase solamente tiene definadas las propiedades del proveedor y hereda de la clase padre `OAuth2Login`.

- **config_prefix**: Prefijo para idententificar al proveedor en el diccionario de configuraciones.
- **redirect_endpoint**: Nombre para la URL del redireccion
- **state_session_key**: Llave que identifica la sesion activa
- **default_scope**: Tupla con los nombres de las variables que configuran el alcanze de permisos en el proveedor.
- **default_redirect_path**: Path de la URL de redireccion.
- **auth_url**: URL del servidor de autenticacion del proveedor
- **token_url**: URL endpoint de peticion del token de acceso
- **profile_url**: URL endpoint de peticion de datos del usuario (Servidor de recursos)



```python
class NombreProveedor(OAuth2Login):

  config_prefix = "PROVEEDOR_LOGIN_"
  redirect_endpoint = "_proveedor_login"
  state_session_key = "_proveedor_login_state"

  default_scope = (
    "variables_del_proveedor"
  )

  default_redirect_path = "/login/proveedor"

  auth_url = "auth_url_proveedor"
  token_url = "token_url_proveedor"
  profile_url = "profile_url_proveedor"
```

## Script de ejecución

En este scipt `app.py` se encuentran las variables de entorno en app y las intancias de las clases de los proveedores.
```python
# Se instancia cada una de clases con las configuraciones repectivas para cada proveerdor.

google_login = GoogleLogin(app)
linkedin_login = LinkedInLogin(app)
facebook_login = FacebookLogin(app)

```


Con estan instancias tenemos acceso a todos los métodos del protocolo OAuth 2.0, definimos los enlaces para hacer el login y las URLS de autorización para empepzar con el primer paso del protocolo explicado en la sección [Implementacion Protocolo OAuth 2.0]().

```python
@app.route("/")
def index():
  return """
<html>
<a href="{}">Login con Google</a> <br>
<a href="{}">Login con Linkedin</a> <br>
<a href="{}">Login con Facebook</a> <br>
""".format(google_login.authorization_url(), linkedin_login.authorization_url(), facebook_login.authorization_url())
```

En la función anterior se define una ruta raiz que retorna un HTML con enlace a las 3 opciones de login. Se usa la función `format` para hacer render de las urls de autorización y la aparición de las llaves en los hrefs.

Como resultado de la herencia de la clase `OAuth2Login`, cada una de las instancias de los porveedores debe implementar las funciones `login_success` y `login_failure` como atributo de clase, para esto usamos un `decorator` que lo que hace es asignar una función como un atributo.

Ejemplo con la instancia de `google_login`:

```python
@google_login.login_success
def login_success(token, profile):
  return jsonify(token=token, profile=profile)

@google_login.login_failure
def login_failure(e):
  return jsonify(error=str(e))
```

Esta funciones se ejecutan al final del los pasos de protocolo, dependiendo de su flujo exitoso o fallido, cada proveedor tiene la opción de responder a su manera.

## Resultados

En las siguientes capturas se muestra el resultado de cada paso para cada uno de los proveedores, véase los rectangulos resaltados con rojo, alli se puede identificar en las URLs algunos de los parámetros y valores generados por las funciones expuestas en este documento.

Respuesta URL raíz:

![Imgur](http://i.imgur.com/nsTZ9X9.png)
- **Google**

Redirección a Login con **Google**, en la URL de los rectángulos se pueden apreciar los parámetros generados por la función authorization_url. 
![Imgur](http://i.imgur.com/JhMvblS.png)

Resultado con la información del usuario

![Imgur](http://i.imgur.com/9acILPY.png)

- **Linkedin**

![Imgur](http://i.imgur.com/Csojyii.png)

Resultado con la información del usuario

![Imgur](http://i.imgur.com/a9Vb89d.png)

- **Facebook**

![Imgur](http://i.imgur.com/PRmthqL.png)

Resultado con la información del usuario

![Imgur](http://i.imgur.com/PgocZu7.png)
