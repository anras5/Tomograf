from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, IntegerField, BooleanField, StringField, DateField, DecimalField, FloatField
from wtforms.validators import InputRequired, NumberRange, DataRequired, Length


class InputForm(FlaskForm):
    interval = FloatField("Kąt przesuwania emitera [°]?",
                            validators=[InputRequired()])
    detectors_number = IntegerField("Liczba detektorów",
                                    validators=[InputRequired(), NumberRange(min=1)])
    extent = IntegerField("Rozpiętość kątowa detektorów",
                          validators=[InputRequired(), NumberRange(min=1)])
    photo = FileField("Prześlij plik",
                      validators=[FileRequired(), FileAllowed(['jpg', 'png', 'dcm'], 'Images or DICOM only!')])

    gradual = BooleanField("Czy rejestrować kroki pośrednie?", default=False)

    dicom = BooleanField("Czy wygenerować plik dicom?", default=False)
    filtered = BooleanField("Czy użyć filtrowania do poprawy jakości wyniku?", default=False)
    name = StringField("Podaj imię pacjenta")
    id = StringField("Podaj ID pacjenta")
    sex = StringField("Podaj płeć pacjenta")
    birth_date = DateField("Podaj datę urodzin", format="%Y-%m-%d")
    comment = StringField("Podaj komentarz do badania")

    submit = SubmitField("Prześlij")
