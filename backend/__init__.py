from flask import Flask,render_template,g,session
from flask_cors import CORS
def creat_app():
    app = Flask(__name__,template_folder="templates",static_folder="static",static_url_path="/backend/static")
    CORS(app)
    from . import main
    app.register_blueprint(main.main)
    app.config['SECRET_KEY'] = 'digiwebtestbare12561856!!'
    app.debug = True
    return app
