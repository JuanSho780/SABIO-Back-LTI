import os
import time
import jwt
from flask import Flask, request, redirect, jsonify, session
from pylti1p3.contrib.flask import FlaskOIDCLogin, FlaskMessageLaunch, FlaskRequest
from pylti1p3.tool_config import ToolConfDict
from dotenv import load_dotenv

from werkzeug.middleware.proxy_fix import ProxyFix

from LTI_config import LTI_CONFIG


app = Flask(__name__)
load_dotenv()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'lti_connector_session'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

def get_tool_conf():
    return ToolConfDict(LTI_CONFIG)

#LTI routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        tool_conf = get_tool_conf()

        flask_request = FlaskRequest(
            cookies=request.cookies,
            session=session,
            request_is_secure=True
        )

        oidc_login = FlaskOIDCLogin(flask_request, tool_conf)

        launch_url = f"https://{request.host}/launch"
        return oidc_login.redirect(launch_url)
    except Exception as e:
        #print(f"Error en Login: {e}")
        return f"Error in Login Init: {e}", 500
    
@app.route("/launch", methods=['GET', 'POST'])
def launch():
    # --- DEBUGGING (cookies) ---
    print(f"- Cookies recibidas: {request.cookies}")
    print(f"- Form Data (state): {request.form.get('state')}")
    # -------------------------------------------------------
    state_param = request.form.get('state')
    print(f"- Form Data (state): {state_param}")

    try:
        tool_conf = get_tool_conf()
        flask_request = FlaskRequest()

        message_launch = FlaskMessageLaunch(flask_request, tool_conf)

        launch_data = message_launch.get_launch_data()
        #print("Launch validado correctamente")

        #Extract decode user (client) data
        email = launch_data.get('email')
        name = launch_data.get('name')
        sub = launch_data.get('sub') # ID único del usuario en Blackboard
        roles = launch_data.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
        context = launch_data.get('https://purl.imsglobal.org/spec/lti/claim/context', {})

        payload = {
            "sub": sub,
            "email": email,
            "name": name,
            "roles": roles,
            "course_id": context.get('id'),
            "course_title": context.get('title'),
            "source": "lti",
            "iat": time.time(),
            "exp": time.time() + 60 # Expires in 60 seconds (muy corto, por seguridad)
        }
        
        handoff_token = jwt.encode(payload, os.getenv("SHARED_SECRET"), algorithm=os.getenv("ALGORITHM"))
        
        return redirect(f"{os.getenv('MAIN_APP_URL')}/home?token={handoff_token}")
    
    except Exception as e:
        #print(f"Error en Launch: {e}")
        return f"Error en LTI Launch: {e} <br><br> (Watch out the cookies sent)", 401

@app.route('/jwks', methods=['GET'])
def get_jwks():
    tool_conf = get_tool_conf()
    return jsonify(tool_conf.get_jwks())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9000, debug=True)