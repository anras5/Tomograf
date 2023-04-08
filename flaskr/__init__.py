import datetime
import os
import uuid

from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from werkzeug.utils import secure_filename

from flaskr.src.dicom import Patient
from flaskr.src.forms import InputForm
from flaskr.src.tomograf import calculate_sinogram


def create_app():
    """Create and configure an instance of the Flask app"""

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    @app.route("/", methods=['GET', 'POST'])
    def home():
        form = InputForm()
        if form.validate_on_submit():

            # -------------------------------------------------------------------------------------------------------- #
            # HANDLE FILE
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

            # save input file
            f.save(input_path)

            # -------------------------------------------------------------------------------------------------------- #
            # HANDLE TOMOGRAPH SETTINGS
            interval = form.interval.data
            detectors_number = form.detectors_number.data
            extent = form.extent.data
            gradual = form.gradual.data
            dicom = form.dicom.data
            filtered = form.filtered.data

            patient = Patient(
                form.name.data,
                form.id.data,
                form.sex.data,
                form.birth_date.data.strftime("%Y%m%d"),
                form.comment.data
            )

            dicom_name = f'{patient.name}_{datetime.date.today()}.dcm'

            # create sinogram and output files
            gradual_number = calculate_sinogram(input_path, users_directory_path,
                                                interval, detectors_number, extent,
                                                gradual,
                                                dicom, filtered, patient, dicom_name)

            return redirect(url_for('result',
                                    uid=users_uid, input_name=filename, gradual_number=gradual_number,
                                    dicom_name=dicom_name))

        return render_template("index.html", form=form, today=datetime.date.today().strftime("%Y-%m-%d"))

    @app.route("/download")
    def download():
        uid = request.args.get('uid')
        dicom_name = request.args.get('dicom_name')
        dicom_path = os.path.join('static', 'temporary_images', uid, dicom_name)
        if os.path.exists(os.path.join('flaskr', 'static', 'temporary_images', uid, dicom_name)):
            return send_file(dicom_path)

    @app.route("/result")
    def result():
        uid = request.args.get('uid')
        input_name = request.args.get('input_name')
        gradual_number = request.args.get('gradual_number', type=int)
        dicom_name = request.args.get('dicom_name')
        if uid and input_name and gradual_number is not None:
            directory = os.path.join('flaskr', 'static', 'temporary_images', uid)
            if os.path.exists(directory):
                return render_template('result.html',
                                       uid=uid, input_name=input_name, gradual_number=gradual_number,
                                       dicom_name=dicom_name)
        flash("Brak odpowiednich parametrów", 'error')
        return redirect(url_for('home'))

    return app
