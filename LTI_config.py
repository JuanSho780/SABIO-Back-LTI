from dotenv import load_dotenv
import os

load_dotenv()
PLATFORM_ID = os.getenv("PLATFORM_ID")

CONFIGURACION_COMUN = {
    "client_id": "flask1234",
    "auth_login_url": f"https://lti-ri.imsglobal.org/platforms/{PLATFORM_ID}/authorizations/new",
    "auth_token_url": f"https://lti-ri.imsglobal.org/platforms/{PLATFORM_ID}/access_tokens",
    "key_set_url": f"https://lti-ri.imsglobal.org/platforms/{PLATFORM_ID}/platform_keys/5287.json",
    "private_key_file": "private.key",
    "public_key_file": "public.key",
    "deployment_ids": ["1"]  
}

LTI_CONFIG = {
    "https://lti-ri.imsglobal.org": CONFIGURACION_COMUN,
    "flask1234": CONFIGURACION_COMUN
}