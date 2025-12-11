from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract
from datetime import datetime

# --- Configuración ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    # 1. Lógica POST (Agregar Gasto)
    if request.method == 'POST':
        try:
            date_str = request.form['date']
            description = request.form['description']
            category = request.form['category']
            amount = float(request.form['amount'])
            
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            new_expense = Expense(date=date_obj, description=description, category=category, amount=amount)
            db.session.add(new_expense)
            db.session.commit()
            
            return redirect(url_for('home'))
        except Exception as e:
            return f"Ocurrió un error al guardar: {e}"

    # 2. Lógica GET (Mostrar y Filtrar)
    
    # Obtener parámetros de filtro de la URL (si existen)
    filter_year = request.args.get('year', type=int)
    filter_month = request.args.get('month', type=int)

    # Consulta base
    query = Expense.query

    # Aplicar filtros si fueron seleccionados
    if filter_year and filter_month:
        query = query.filter(extract('year', Expense.date) == filter_year, 
                             extract('month', Expense.date) == filter_month)

    # Ordenar y ejecutar
    expenses = query.order_by(Expense.date.desc()).all()

    # --- Generar lista de fechas disponibles para el selector ---
    # Obtenemos todas las fechas únicas para poblar el dropdown
    all_dates = db.session.query(Expense.date).all()
    available_dates = set()
    for (d,) in all_dates:
        available_dates.add((d.year, d.month))
    
    # Ordenar fechas (más reciente primero)
    available_dates = sorted(list(available_dates), reverse=True)

    # Lista de nombres de meses para mostrar bonito en el HTML
    month_names = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    return render_template('index.html', 
                           expenses=expenses, 
                           available_dates=available_dates, 
                           month_names=month_names,
                           sel_year=filter_year, 
                           sel_month=filter_month)

# RUTA: Eliminar Gasto
@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    try:
        expense_to_delete = Expense.query.get_or_404(id)
        db.session.delete(expense_to_delete)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Error al eliminar: {e}"

# API JSON para el Gráfico
@app.route('/api/chart-data')
def chart_data():
    expenses = Expense.query.all()
    data = {}
    
    for expense in expenses:
        if expense.category in data:
            data[expense.category] += expense.amount
        else:
            data[expense.category] = expense.amount
            
    labels = list(data.keys())
    values = list(data.values())
    
    return jsonify({'labels': labels, 'data': values})

# --- Ejecución ---
if __name__ == '__main__':
    app.run(debug=True)