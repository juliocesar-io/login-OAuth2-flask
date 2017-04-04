from .base import OAuth2Login


class FacebookLogin(OAuth2Login):

  config_prefix = "FACEBOOK_LOGIN_"
  redirect_endpoint = "_facebook_login"
  state_session_key = "_facebook_login_state"

  default_scope = (
    "public_profile"
  )

  default_redirect_path = "/login/facebook"

  auth_url = "https://www.facebook.com/dialog/oauth"
  token_url = "https://graph.facebook.com/oauth/access_token"
  profile_url = "https://graph.facebook.com/me?"

