import os

from flask import Flask, render_template, redirect, url_for
from werkzeug.utils import secure_filename

from flaskr.src.forms import PhotoForm


def create_app():
    """Create and configure an instance of the Flask app"""

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    @app.route("/", methods=['GET', 'POST'])
    def home():
        form = PhotoForm()
        if form.validate_on_submit():
            f = form.photo.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(
               'flaskr', 'static', 'temporary_images', filename
            ))
            return render_template("index.html", filename=filename)
        return render_template("index.html", form=form)

    return app
