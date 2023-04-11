FROM python:3.9

WORKDIR /tomograf

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./flaskr ./flaskr

CMD ["flask", "--app", "flaskr", "run", "--host=0.0.0.0"]