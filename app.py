from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract
from datetime import datetime
import csv
import io

# --- Configuración ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

BUDGET_LIMIT = 50000.0 

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

    # Filtros
    filter_year = request.args.get('year', type=int)
    filter_month = request.args.get('month', type=int)

    query = Expense.query

    if filter_year and filter_month:
        query = query.filter(extract('year', Expense.date) == filter_year, 
                             extract('month', Expense.date) == filter_month)

    expenses = query.order_by(Expense.date.desc()).all()

    # --- CÁLCULO DE PRESUPUESTO ---
    total_spent = sum(e.amount for e in expenses)
    budget_limit = BUDGET_LIMIT
    
    # Calcular porcentaje
    percentage = (total_spent / budget_limit * 100) if budget_limit > 0 else 0
    percentage = min(percentage, 100)

    # Determinar color
    if percentage < 50:
        progress_color = "bg-green-500"
    elif percentage < 80:
        progress_color = "bg-yellow-500"
    else:
        progress_color = "bg-red-500"

    # Datos para selectores
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
                           sel_month=filter_month,
                           total_spent=total_spent,
                           budget_limit=budget_limit,
                           percentage=percentage,
                           progress_color=progress_color)

# Actualizar Presupuesto
@app.route('/update_budget', methods=['POST'])
def update_budget():
    global BUDGET_LIMIT
    try:
        new_limit = float(request.form['budget'])
        BUDGET_LIMIT = new_limit
    except:
        pass
    return redirect(url_for('home'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    try:
        expense_to_delete = Expense.query.get_or_404(id)
        db.session.delete(expense_to_delete)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Error al eliminar: {e}"

@app.route('/api/chart-data')
def chart_data():
    filter_year = request.args.get('year', type=int)
    filter_month = request.args.get('month', type=int)

    query = Expense.query

    if filter_year and filter_month:
        query = query.filter(extract('year', Expense.date) == filter_year, 
                             extract('month', Expense.date) == filter_month)
    
    expenses = query.all()
    
    data = {}
    for expense in expenses:
        if expense.category in data:
            data[expense.category] += expense.amount
        else:
            data[expense.category] = expense.amount
            
    labels = list(data.keys())
    values = list(data.values())
    
    return jsonify({'labels': labels, 'data': values})

@app.route('/export')
def export_data():
    filter_year = request.args.get('year', type=int)
    filter_month = request.args.get('month', type=int)

    query = Expense.query

    if filter_year and filter_month:
        query = query.filter(extract('year', Expense.date) == filter_year, 
                             extract('month', Expense.date) == filter_month)
        filename = f"gastos_{filter_year}_{filter_month}.csv"
    else:
        filename = "gastos_totales.csv"

    expenses = query.order_by(Expense.date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Fecha', 'Descripción', 'Categoría', 'Monto'])
    
    for expense in expenses:
        writer.writerow([expense.id, expense.date, expense.description, expense.category, expense.amount])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

if __name__ == '__main__':
    app.run(debug=True)