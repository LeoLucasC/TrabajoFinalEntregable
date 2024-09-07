from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import csv

app = Flask(__name__)
app.secret_key = 'supersecretkey'  



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

# Función para leer usuarios desde el archivo CSV
def leer_usuarios_csv():
    usuarios = []
    with open('usuarios.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            usuarios.append(row)
    return usuarios

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')

       
        usuarios = leer_usuarios_csv()

        
        for user in usuarios:
            if user['usuario'] == usuario and user['contrasena'] == contrasena:
                session['usuario'] = usuario
                return redirect(url_for('index'))

        flash('Usuario o contraseña incorrectos.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)


