import os
import uuid

from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename

from flaskr.src.forms import PhotoForm
from flaskr.src.tomograf import calculate_sinogram


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

            # create temporary_images directory if it does not exist
            temporary_images_directory_path = os.path.join('flaskr', 'static', 'temporary_images')
            if not os.path.exists(temporary_images_directory_path):
                os.makedirs(temporary_images_directory_path)

            f = form.photo.data
            filename = secure_filename(f.filename)

            # create user's unique directory
            users_uid = str(uuid.uuid4())
            users_directory_path = os.path.join(temporary_images_directory_path, users_uid)
            os.makedirs(users_directory_path)

            # make paths to files
            input_path = os.path.join(users_directory_path, filename)
            sinogram_path = os.path.join(users_directory_path, 'sinogram.png')
            output_path = os.path.join(users_directory_path, 'output.png')

            # save input file and create sinogram and output files
            f.save(input_path)
            calculate_sinogram(input_path, sinogram_path, output_path)

            return redirect(url_for('result', uid=users_uid, input_name=filename))
        return render_template("index.html", form=form)

    @app.route("/result")
    def result():
        uid = request.args.get('uid')
        input_name = request.args.get('input_name')
        directory = os.path.join('flaskr', 'static', 'temporary_images', uid)
        if uid and input_name and os.path.exists(directory):
            return render_template('result.html', uid=uid, input_name=input_name)
        return redirect(url_for('home'))

    return app
