from flask import Flask


def init_app():
    app = Flask(__name__)
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    
    return app

app = init_app()

from app import routes


# app.run(debug=True)