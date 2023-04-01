from flask import Flask, render_template


def create_app():
    """Create and configure an instance of the Flask app"""

    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app
