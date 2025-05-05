import os
from datetime import datetime
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
        imagen = Imagen(
            nombre=data['nombre'],
            fecha=datetime.fromisoformat(data['fecha']),
            rojo=data['rojo'],
            verde=data['verde'],
            azul=data['azul'],
            total=data['total']
        )
        db.session.add(imagen)
        db.session.commit()
        return jsonify({"status": "ok", "message": "Imagen guardada correctamente"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/test-insert')
def test_insert():
    imagen = Imagen(
        nombre='imagen_prueba.bmp',
        fecha=datetime.now(),
        rojo=1000,
        verde=2000,
        azul=3000,
        total=6000
    )
    db.session.add(imagen)
    db.session.commit()
    return "Imagen de prueba añadida correctamente"

@app.route('/clear-db', methods=['GET'])
def clear_db():
    try:
        # Elimina todas las filas de la tabla Imagen
        db.session.query(Imagen).delete()
        db.session.commit()
        return redirect(url_for('index'))  # Redirige al índice después de limpiar
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()