from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- Configuración de la App ---
app = Flask(__name__)
# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)

# --- Modelos (Base de Datos) ---
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Expense {self.description} - ${self.amount}>'

# --- Inicialización de la BD ---
with app.app_context():
    db.create_all()

# --- Rutas ---
@app.route('/')
def home():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('index.html', expenses=expenses)

# --- Ejecución ---
if __name__ == '__main__':
    app.run(debug=True)