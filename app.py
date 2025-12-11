from flask import Flask, render_template

# --- Configuración de la App ---
app = Flask(__name__)

# --- Rutas ---
@app.route('/')
def home():
    return "<h1>🚀 Sistema de Gastos Funcionando</h1>"

# --- Ejecución ---
if __name__ == '__main__':
    app.run(debug=True)