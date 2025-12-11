from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- Configuración ---
app = Flask(__name__)
# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)

# --- Modelos ---
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Expense {self.description}>'

# --- Inicialización ---
with app.app_context():
    db.create_all()

# --- Rutas ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            date_str = request.form['date']
            description = request.form['description']
            category = request.form['category']
            amount = float(request.form['amount'])
            
            # Convertir fecha de string a objeto date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Crear y guardar el gasto
            new_expense = Expense(date=date_obj, description=description, category=category, amount=amount)
            db.session.add(new_expense)
            db.session.commit()
            
            return redirect(url_for('home'))
        except Exception as e:
            return f"Ocurrió un error al guardar: {e}"

    # Obtener gastos para mostrar en la tabla
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('index.html', expenses=expenses)

@app.route('/api/chart-data')
def chart_data():
    # Agrupamos los gastos por categoría
    expenses = Expense.query.all()
    data = {}
    
    for expense in expenses:
        if expense.category in data:
            data[expense.category] += expense.amount
        else:
            data[expense.category] = expense.amount
            
    # Preparamos las listas para Chart.js
    labels = list(data.keys())
    values = list(data.values())
    
    return jsonify({'labels': labels, 'data': values})

# --- Ejecución ---
if __name__ == '__main__':
    app.run(debug=True)