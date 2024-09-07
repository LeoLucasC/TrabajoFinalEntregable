from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/carrito')
def carrito():
    return render_template('carrito.html')


@app.route('/productos')
def productos():
    
    productos_df = pd.read_csv('productos.csv')
    productos = productos_df.to_dict(orient='records')  # Convertir a una lista de diccionarios
    return render_template('productos.html', productos=productos)


@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/login')
def login():
    return render_template('login.html')

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)


