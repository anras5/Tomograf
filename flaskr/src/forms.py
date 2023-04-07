from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


class PhotoForm(FlaskForm):
    photo = FileField("Prześlij swój plik",
                      validators=[FileRequired(), FileAllowed(['jpg', 'png', 'dcm'], 'Images or DICOM only!')])
    submit = SubmitField("Prześlij")
