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

# This proxy fix is needed when working behind a proxy (like in production with nginx, or our case, in our testing using ngrok)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Digital signature secret key for sessions (you need to use a long a complex string here, but save it in .env)
app.secret_key = os.urandom(24)

# Session cookie settings (important to work and maintain sessions in iframes)
app.config['SESSION_COOKIE_NAME'] = 'lti_connector_session'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

def get_tool_conf():
    return ToolConfDict(LTI_CONFIG)

#LTI routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # This function retrieves the tool configuration (LTI_config)
        tool_conf = get_tool_conf()

        # Here the server catches the cookies and session info from the incoming request
        flask_request = FlaskRequest(
            cookies=request.cookies,
            session=session,
            request_is_secure=True
        )

        oidc_login = FlaskOIDCLogin(flask_request, tool_conf)

        # Request host is just host:port of the actual server
        launch_url = f"https://{request.host}/launch"

        # Here internally creates the login redirect response (mentioned in documentation)
        return oidc_login.redirect(launch_url)
    
    except Exception as e:
        return f"Error in Login Init: {e}", 500
    
@app.route("/launch", methods=['GET', 'POST'])
def launch():
    try:
        tool_conf = get_tool_conf()
        flask_request = FlaskRequest()

        # Create the message launch object
        message_launch = FlaskMessageLaunch(flask_request, tool_conf)

        # Extract launch data (decode and verify the JWT sent by the LMS)
        launch_data = message_launch.get_launch_data()

        #Extract decode user (client) data
        email = launch_data.get('email') # Student email
        name = launch_data.get('name') # Student full name
        sub = launch_data.get('sub') # Unique ID in the LMS (ex. unique id inside Blackboard)
        roles = launch_data.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
        context = launch_data.get('https://purl.imsglobal.org/spec/lti/claim/context', {})

        #HERE GOES THE USERS DB MATCH LOGIC (retrieve user info from your DB if user exists, if not, create it) -> integration with SABIO's DBs and backend
        #Then create the JWT with the same secret as the main backend server

        payload = {
            "sub": sub,
            "email": email,
            "name": name,
            "roles": roles,
            "course_id": context.get('id'),
            "course_title": context.get('title'),
            "source": "lti",
            "iat": time.time(),
            "exp": time.time() + 60 # Expires in 60 seconds (too short, for security reasons -just for example-)
        }
        
        # Create the JWT to handoff to the main application
        handoff_token = jwt.encode(payload, os.getenv("SHARED_SECRET"), algorithm=os.getenv("ALGORITHM"))
        
        # Redirect to the home page (SABIO's front-end) with the token as URL parameter
        # Then the frontend will use this token to authenticate with the main backend
        return redirect(f"{os.getenv('MAIN_APP_URL')}/home?token={handoff_token}")
    
    except Exception as e:
        return f"Error en LTI Launch: {e} <br><br> (Watch out the cookies sent)", 401

@app.route('/jwks', methods=['GET'])
def get_jwks():
    tool_conf = get_tool_conf()
    return jsonify(tool_conf.get_jwks())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9000, debug=True)