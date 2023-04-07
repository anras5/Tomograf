# TOMOGRAF

## How to run
The app will run on `localhost:5000`

### Docker

```commandline
docker build -t tomograf
docker run -p 5000:5000 tomograf
```

### Locally

Windows 10:
```commandline
python -m venv venv
venv/Scripts/activate.ps1
pip install -r requirements.txt
flask --app flaskr run --host="0.0.0.0"
```

Linux:
```commandline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask --app flaskr run --host="0.0.0.0"
```