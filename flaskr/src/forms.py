from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField


class PhotoForm(FlaskForm):
    photo = FileField("Prześlij swój plik", validators=[FileRequired()])
    submit = SubmitField("Prześlij")
