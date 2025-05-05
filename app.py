import os
from datetime import datetime
import pytz  # Importar pytz para gestionar la zona horaria
from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize DB and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models AFTER db init
from models import Imagen

# Zona horaria de España (Madrid)
spain_tz = pytz.timezone('Europe/Madrid')


@app.route('/', methods=['GET'])
def index():
    print("Request for index page received.")
    imagenes = Imagen.query.order_by(Imagen.fecha.desc()).all()
    return render_template('index.html', imagenes=imagenes)


@app.route('/upload', methods=['POST'])
@csrf.exempt
def upload_image_data():
    data = request.get_json()
    try:
        print(f"Fecha recibida (original): {data['fecha']}")  # Depuración
        # Convertir la fecha de la imagen de UTC a la zona horaria de España
        fecha_utc = datetime.fromisoformat(data['fecha'])
        fecha_spain = fecha_utc.replace(tzinfo=pytz.utc).astimezone(spain_tz)
        
        print(f"Fecha convertida a España: {fecha_spain}")  # Depuración
        
        imagen = Imagen(
            nombre=data['nombre'],
            fecha=fecha_spain,  # Usar la fecha en zona horaria de España
            rojo=data['rojo'],
            verde=data['verde'],
            azul=data['azul'],
            total=data['total']
        )
        db.session.add(imagen)
        db.session.commit()
        
        print(f"Imagen guardada con fecha: {imagen.fecha}")  # Depuración
        
        return jsonify({"status": "ok", "message": "Imagen guardada correctamente"}), 201
    except Exception as e:
        print(f"Error: {str(e)}")  # Depuración
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/test-insert')
def test_insert():
    # Obtener la hora actual y convertirla a la zona horaria de España
    fecha_spain = datetime.now(pytz.timezone('Europe/Madrid'))

    print(f"Fecha de prueba (España): {fecha_spain}")  # Depuración
    
    imagen = Imagen(
        nombre='imagen_prueba.bmp',
        fecha=fecha_spain,
        rojo=1000,
        verde=2000,
        azul=3000,
        total=6000
    )
    db.session.add(imagen)
    db.session.commit()
    
    print(f"Imagen de prueba añadida con fecha: {fecha_spain}")  # Depuración
    
    return "Imagen de prueba añadida correctamente"


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()
