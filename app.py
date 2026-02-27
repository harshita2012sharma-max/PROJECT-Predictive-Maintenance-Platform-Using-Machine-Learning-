from flask import Flask
from config.config import FLASK_CONFIG
from routes import register_routes


def create_app():
    app = Flask(__name__)
    register_routes(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=FLASK_CONFIG["host"],
        port=FLASK_CONFIG["port"],
        debug=FLASK_CONFIG["debug"]
    )