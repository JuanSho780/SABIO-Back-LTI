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
    "https://sandbox.moodledemo.net": {
        
        # 1. THIS IS THE CLIENT ID THAT THE LMS (MOODLE) GAVE YOU WHEN YOU REGISTERED YOUR TOOL (talk to LMS admin):
        "client_id": "CmKcol4EwBZaTTf",
        
        # 2. STATICS URLs OF MOODLE (You need to talk to LMS admin to get this enpoints):
        "auth_login_url": "https://sandbox.moodledemo.net/mod/lti/auth.php",
        "auth_token_url": "https://sandbox.moodledemo.net/mod/lti/token.php",
        "key_set_url": "https://sandbox.moodledemo.net/mod/lti/certs.php",
        
        # 3. Here goes your keys (the name of the files):
        "private_key_file": "private.key",
        "public_key_file": "public.key",
        
        # 4. DEPLOYMENT ID:
        # In Moodle, the Deployment ID normally is "2" for manual tools (sandbox). 
        # to be sure, we can put many ids:
        "deployment_ids": ["1", "2", "3", "4", "5"] 
    }
}