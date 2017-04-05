from flask import request, session, url_for
from requests_oauthlib import OAuth2Session

class OAuth2Login(object):
  """
  Clase base OAuth2Login que tendra los metodos requeridos para completar 
  un login usando el protocolo OAuth 2.0
  """
  def __init__(self, app=None):
    """
    Si tiene el parámetro 'app', se envía como referencia a la función 'init_app'
    
    :param app: Es un parámetro opcional, contiene un diccionario con las configuraciones de la app
    """
    if app:
      self.init_app(app)

  def get_config(self, app, name, default_value=None):
    """
    Método que obtiene los tokens de cada uno de los proveedores de las configuraciones al la app
    usando el contexto de la instacia llamandolo por su prefijo definido en la variable 'config_prefix
    
    :param app:  Arreglo de configuraciones
    :param name: Nombre de la llave en el arreglo
    :param default_value: En caso que no exista el valor por defecto en None.
    :return: retorna el valor en el diccionario 'config' correpondiente al índice en 'name'
    """
    return app.config.get(self.config_prefix + name, default_value)

  def init_app(self, app):
    """
    
    Con la ayuda de la función 'get_config' esta funcion obtiene cada uno de las tokens de los 
    proveedores y otras configuraciones como los permisos del API(scope), el protocolo y el path de redirección

    :param app: Es un parámetro opcional, contiene un diccionario con las configuraciones de la app
    """
    self.client_id = self.get_config(app, "CLIENT_ID")
    self.client_secret = self.get_config(app, "CLIENT_SECRET")
    self.scope = self.get_config(app, "SCOPE", self.default_scope).split(",")
    self.redirect_scheme = self.get_config(app, "REDIRECT_SCHEME", "http")

    # Agregar una nueva ruta para cada redirecion, el primer parametro corresponde a el path del redirecion definido
    # Ej: /login/google, el segundo parametro redirect_endpoint corresponde al nombre de ruta, y el tercero
    # Corresponde a la funcion que se ejecuta cuando se hace una peticion al path del primer parametro.
    app.add_url_rule(
      self.get_config(app, "REDIRECT_PATH", self.default_redirect_path),
      self.redirect_endpoint,
      self.get_token,
    )

  @property
  def redirect_uri(self):
    """
    Crea una atributo de solo lectura con el string de la URI de redireccion 
    registrada como Callback en la configuracion del API.
    """
    return url_for(
      self.redirect_endpoint,
      _external=True,
      _scheme=self.redirect_scheme,
    )

  def session(self):
    """
    Crea una sesión con el token del proveedor, la url de redirección y los permisos del API. 
    """
    return OAuth2Session(
      self.client_id,
      redirect_uri=self.redirect_uri,
      scope=self.scope,
    )

  def authorization_url(self, **kwargs):
    """
    Esta función obtiene la sesión en el contexto actual, la almacena y genera una url 
    de autorizacion utlizando el endpoint del proveedor utilizando el valor de la variable 'auth_url' 
    de la clase instanciada.
    """
    sess = self.session()
    auth_url, state = sess.authorization_url(self.auth_url, **kwargs)
    session[self.state_session_key] = state
    return auth_url

  def get_token(self):

    """
    Esta función obtiene el token de acceso utilizando el endpoint definido en 'token_url' de la clase instanciada
    y la llave secreta del API, luego con el endpoint 'profile_url' hace el intento de obtener una respuesta del API 
    en JSON con los atributos del usuario utilzando la funcion 'get_profile'. Si es exitoso, se pasa con callback 
    la función 'login_success', en caso contrario se pasa a la función 'login_failure'.
    
    """
    sess = self.session()
    # Obtener token
    try:
      sess.fetch_token(
        self.token_url,
        code=request.args["code"],
        client_secret=self.client_secret,
      )
    except Warning as w:
      print w
      pass
    except Exception as e:
      return self.login_failure_func(e)

    # Obtener datos de usuario
    try:
      profile = self.get_profile(sess)

    except Exception as e:
      return self.login_failure_func(e)

    return self.login_success_func(sess.token, profile)

  def login_success(self, f):
    """
    Función callback de login exitoso.
    """
    self.login_success_func = f
    return f

  def login_failure(self, f):
    """
    Función callback de login fallido.
    """
    self.login_failure_func = f
    return f

  def get_profile(self, sess):
    """
    Función para obtener datos del usuario y retornarlos como JSON.
    """
    resp = sess.get(self.profile_url)
    resp.raise_for_status()
    return resp.json()
