Login-OAuth2-Flask
==================

En esta practica se reliza Login con el protocolo OAuth 2.0 utilizando 3 proveedores diferentes (Google, Linkedin y Facebook).

## Requerimientos

- flask
- requests-oauthlib

Para instalar los requerimientos, simplemente ejecutar el siguiente comando:

```bash
pip install -r requirements.txt
```

## Configuracion de API's

Lo primero que debemo hacer es registrar un aplicacion con cada proveedor, obtener las configuraiones y llaves de acceso.

**Google**

Ir a [Google APIs](https://console.developers.google.com/apis/credentials) seleccionar "OAuth cliente Id" para generar tokens de acceso al API.

![3](http://i.imgur.com/1Gdtsmv.png)

Definir un nombre, generara dos llaves un id de cliente y un token de autenticacion como en la imagen.

Luego agregar una URI autorizada para hacer la redirecion del login.

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

 auth_url = "https://accounts.google.com/o/oauth2/auth"
 token_url = "https://accounts.google.com/o/oauth2/token"
 profile_url = "https://www.googleapis.com/oauth2/v2/userinfo"
```
Con esto estaria finalizada la configuracion minina para hacer login con Google.

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

Ir a [Facebook Develoers](), crear un app. Obtener las llaves respectivas 

![Imgur](http://i.imgur.com/t2WoGKa.png)

```python
os.environ["FACEBOOK_LOGIN_CLIENT_ID"] = "tu_id_aqui"
os.environ["FACEBOOK_LOGIN_CLIENT_SECRET"] = "tu_token_aqui"
```

Luego configurar Facebook Login.

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

En terminos generales el programa permite configurar los endpoints requeridos para que los usuarios hagan login usando los proveedores mencionados, con esto el programa obtiene un token valido para realizar peticiones a las APIs, con el token de acceso resultado de su autorizacion este puede obtener informacion de un servidor de recursos. En la **Fig.1** se ilustra el diagrama del funcionamiento de este protocolo.

**Fig.1** Diagrama alto nivel protocolo OAuth 2.0
![Fig.1](http://i.imgur.com/RsKyg2I.png)

El digrama muestra el funcionamiento de alto nivel, ahora para entender un poco mas, veamos un caso de uso desde el usuario en el siguiente diagrama.

**Fig.2** Diagrama de caso de uso Login con OAuth 2.0

![Fig.2](http://i.imgur.com/fLKQkNi.png)

> OAuth 2.0 es considerado un procolo estandar para autorizacion. Utiliza el estandar RFC 6749, para mas informacion visitar el sitio oficial [OAuth 2.0](https://oauth.net/2/)

### Clases

Luego de comprender el protocolo podemos diseñar las clases. Primero creamos una clase base llamada `OAuth2Login` que tendra los metodos requeridos para completar un login usando el protocolo OAuth 2.0 ilustrado en la **Fig.1**.

**Fig.3** Diagrama de clases cada proveedor hereda del protocolo OAuth 2.0

![Fig.3](http://i.imgur.com/elA5D36.png)

![Imgur](http://i.imgur.com/7G9i05n.png)



### Clase OAuth2Login

Esta clase recibira como parametro las configuracion de la app que contiene un diccionario con las llaves de cada uno de los proveedores y sera la clase padre para cada uno de los proveedores como se ilustra en la **Fig.3**.

Con este disño garantizamos la modularidad de la aplicacion para agregar cualquier otro porveedor y la abstracion del protocolo de las configuraciones de cada proveedor. Ahora veamos lo metodos, atributos de la clase.

Para la clase `OAuth2Login` el metodo auxiliar `get_config` obtiene los tokens de cada uno de los proveedores de las configuraciones al la app usando el contexto de la instacia para obtener el prefijo definido en la variable `config_prefix`.

:param app:  Arreglo de configuraciones 
:param name: Nombre de la llave en el arreglo
:param default_value: En caso que no exista el valor por defecto en None.
:return: retorna el valor en el diccionario 'config' correpondiente a la indice en 'name'

```python
  def get_config(self, app, name):
    return app.config.get(self.config_prefix + name)
```

Con esto simplemente se identifican cada una del par de llaves da cada proveedor haciendo `get(indice)` en el diccionario `config`, los indices cumplen con el sigueinte patron:

<:Prefijo proveedor>_CLIENT_ID
<:Prefijo proveedo>_CLIENT_SECRET

Ej: Con el supuesto que el valor `config_prefix` en la instacia de la case es "LINKEDIN_LOGIN_"

```python
  get_config(app, "CLIENT_ID")
  # Retorna el valor LINKEDIN_LOGIN_CLIENT_ID
```
Esta valor fue definido en la varibles entorno en la seccion anterior [Configuracion de API’s]().

Luego se inicializa la instancia de la clase con el metodo `init_app` obteniendo las configuraciones usando el metodo anterior  y se define la rutas de redireccion para el login correpondiente a la de configuracion en el API. 

Como Ejemplo si fuera la instacia de la clase de Facebook:

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
## Implementacion Protocolo OAuth 2.0
Veamos como es el funcionamiento de la implementacion de protocolo OAuth 2.0 basados en la **Fig.1** y **Fig.2** implementado en codigo.

### Paso 1

El priner paso es crear una session con el id del cliente correpondiente a "FACEBOOK_LOGIN_CLIENT_ID" para luego pedir autorizacion al servidor de autenticacion del proveedor para que este retorne un token de acceso.

```python
  def session(self):
    return OAuth2Session(
      self.client_id,
      redirect_uri=self.redirect_uri,
      scope=self.scope,
    )
```

El metodo crea una sesion con el `client_id`, la url de redirecion `redirect_uri` y el alcanze de permisos del API `scope`, cuando el cliente pusla el link es enviado al sitio de proveedor, este autoriza y el servidor de autenticacion del proveedor valida la sesison de usuario y hace a redirecion a la aplicacion usando `redirect_uri`. Corresponde al primer paso del procolo OAuth 2.0 ilustrado en la **Fig.4**.


**Fig.4**.Primer paso del procolo OAuth 2.0

![Imgur](http://i.imgur.com/eq2STMC.png)

### Paso 2
Luego con la sesison activa podemos hacer una petecion para obtener el token de acceso para el servidor de recursos, para lograr eso utilizaremos ahora el `client_secret` correpondiente para el ejemplo a "FACEBOOK_LOGIN_CLIENT_SECRET" y la URL correpondiente para obtenerl token, llamada `token_url` y correspondiente a "https://graph.facebook.com/oauth/access_token".

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
El  metodo anterior obtiene el token de acceso utilizando el endpoint definido en `token_url` de la clase instanciada y la llave secreta del API extraida del diccionario `config`, identificada en el metodo como `client_secret`. Correponde al segudno paso del protocolo OAuth 2.0 ilustrado en la **Fig.5**.

**Fig.5**. Segundo paso del procolo OAuth 2.0
![Imgur](http://i.imgur.com/ELjnBpM.png)

### Paso 3
Finalmente para obtener la informacion del usuario del servidor de recursos utilizamos el token de acceso ya en la sesion y la `profile_url` donde se realizara la consulta.

```python
  def get_profile(self, sess):
    """
    Funcion para obtener datos del usuario y retonarlos como JSON.
    """
    resp = sess.get(self.profile_url)
    resp.raise_for_status()
    return resp.json()
```

En la funcion anterior se realiza simplemente una peticion GET al endpoint `profile_url` y  se retorna la respuesta como JSON. Corresponde al paso final del protocolo OAuth 2.0 ilustrado en la **Fig.6**.

**Fig.6**. Paso final  del procolo OAuth 2.0
![Imgur](http://i.imgur.com/AC7q8bH.png)


### Clase configuracion proveedor

Esta clases solamente tienen definadas las propiedades del proveedor y heredan de la clase padre `OAuth2Login`.

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

## Script de ejecucion

En este scipt `app.py` reciden las variables de entorno en app y las intancias de las clases de los porveedores, veamos como usarlas.
```python
# Se instancia cada una de clases con las configuraciones repectivas para cada proveerdor.

google_login = GoogleLogin(app)
linkedin_login = LinkedInLogin(app)
facebook_login = FacebookLogin(app)

```


Con estan instacias tenemos acceso a todos los metodos del protocolo OAuth 2.0, ahora definimos los enlaces para hacer el login y las URLS autorizacion para empepzar con el primer paso del protocolo explicado en la seccion [Implementacion Protocolo OAuth 2.0]().

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

En la funcion anteriro se define una  ruta raiz que retorna un HTML con enlaze a las 3 opciones de login, mateniendo el minimalismo, se usa la funcion `format` para hacer render de las urls de autorizacion en su orden definicion en los parametros de esta y la aparicion de las llaves en los hrefs.

Como resultado de la herencia de la clase `OAuth2Login`, cada una de las instacias de los porveedores debe implementar las funciones `login_success` y `login_failure` como atributo de clase, para esto usamos un `decorator` que lo que hace es asignar una funcion como un atributo.

Ejemplo con la instacia de `google_login`:

```python
@google_login.login_success
def login_success(token, profile):
  return jsonify(token=token, profile=profile)

@google_login.login_failure
def login_failure(e):
  return jsonify(error=str(e))
```

Esta funciones se ejecutan al final del los pasos de protocolo, dependiendo de su flujo exitoso o fallido, cada proveedor tiene la opcion de responder a su manera.

## Resultados

Respuesta URL raiz:

![Imgur](http://i.imgur.com/nsTZ9X9.png)
- **Google**

Redirecion a Login con **Google**, observar la URL en los rectangulos se peude apreciar los parametros genrados por la funcion authorization_url. 
![Imgur](http://i.imgur.com/JhMvblS.png)

Resultado con la informacion del usuario

![Imgur](http://i.imgur.com/9acILPY.png)

- **Linkedin**

![Imgur](http://i.imgur.com/Csojyii.png)

Resultado con la informacion del usuario

![Imgur](http://i.imgur.com/a9Vb89d.png)

- **Facebook**

![Imgur](http://i.imgur.com/PRmthqL.png)

Resultado con la informacion del usuario

![Imgur](http://i.imgur.com/PgocZu7.png)
