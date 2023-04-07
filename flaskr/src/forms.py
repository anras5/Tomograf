from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, IntegerField
from wtforms.validators import InputRequired, NumberRange


class InputForm(FlaskForm):
    interval = IntegerField("Co jaki kąt przesuwany ma być emiter [°]?",
                            validators=[InputRequired(), NumberRange(min=1, max=90)])
    detectors_number = IntegerField("Ile ma być detektorów?",
                                    validators=[InputRequired(), NumberRange(min=1)])
    extent = IntegerField("Jaka ma być rozpiętość kątowa detektorów?",
                          validators=[InputRequired(), NumberRange(min=1, max=180)])
    photo = FileField("Prześlij swój plik",
                      validators=[FileRequired(), FileAllowed(['jpg', 'png', 'dcm'], 'Images or DICOM only!')])
    submit = SubmitField("Prześlij")
