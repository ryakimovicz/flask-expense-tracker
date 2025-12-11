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

    # Lógica de Filtrado para la Tabla
    filter_year = request.args.get('year', type=int)
    filter_month = request.args.get('month', type=int)

    query = Expense.query

    if filter_year and filter_month:
        query = query.filter(extract('year', Expense.date) == filter_year, 
                             extract('month', Expense.date) == filter_month)

    expenses = query.order_by(Expense.date.desc()).all()

    # Datos para el selector de fechas
    all_dates = db.session.query(Expense.date).all()
    available_dates = set()
    for (d,) in all_dates:
        available_dates.add((d.year, d.month))
    
    available_dates = sorted(list(available_dates), reverse=True)

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

@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    try:
        expense_to_delete = Expense.query.get_or_404(id)
        db.session.delete(expense_to_delete)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Error al eliminar: {e}"

# API JSON
@app.route('/api/chart-data')
def chart_data():
    # 1. Lee los mismos filtros de la URL
    filter_year = request.args.get('year', type=int)
    filter_month = request.args.get('month', type=int)

    query = Expense.query

    # 2. Aplica el filtro si existe
    if filter_year and filter_month:
        query = query.filter(extract('year', Expense.date) == filter_year, 
                             extract('month', Expense.date) == filter_month)
    
    expenses = query.all()
    
    # 3. Procesa los datos filtrados
    data = {}
    for expense in expenses:
        if expense.category in data:
            data[expense.category] += expense.amount
        else:
            data[expense.category] = expense.amount
            
    labels = list(data.keys())
    values = list(data.values())
    
    return jsonify({'labels': labels, 'data': values})

if __name__ == '__main__':
    app.run(debug=True)