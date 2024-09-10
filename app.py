from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import pandas as pd
import csv
import matplotlib.pyplot as plt
import io
from datetime import datetime
import os
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Ruta para guardar las gráficas
GRAPHICS_DIR = os.path.join('static', 'img')

def generar_grafica_compras():
    compras_df = pd.read_csv('compras.csv')
    
    # Expandir la columna 'Historial' en una lista de IDs de productos
    compras_df['Historial'] = compras_df['Historial'].apply(lambda x: [int(id) for id in x.split(',')])
    
    # Crear una lista de todos los IDs de productos comprados
    producto_ids = [id for sublist in compras_df['Historial'] for id in sublist]
    
    # Contar la frecuencia de cada ID de producto
    frecuencia_productos = pd.Series(producto_ids).value_counts()

    # Obtener los 10 productos más comprados
    top_10_productos = frecuencia_productos.head(10)
    
    # Leer datos del producto más comprado
    productos_df = pd.read_csv('productos.csv')
    producto_mas_comprado_id = top_10_productos.idxmax()
    producto_mas_comprado_freq = top_10_productos.max()
    
    producto_mas_comprado = productos_df[productos_df['id'] == producto_mas_comprado_id].iloc[0]

    plt.figure(figsize=(12, 8))
    top_10_productos.plot(kind='bar', color='skyblue')
    plt.title('Frecuencia de Compras de Productos (Top 10)')
    plt.xlabel('ID del Producto')
    plt.ylabel('Frecuencia de Compras')
    plt.xticks(rotation=45)
    
    if not os.path.exists(GRAPHICS_DIR):
        os.makedirs(GRAPHICS_DIR)
    
    file_path = os.path.join(GRAPHICS_DIR, 'grafica_compras.png')
    plt.savefig(file_path)
    plt.close()

    return {
        'id': producto_mas_comprado_id,
        'nombre': producto_mas_comprado['nombre'],
        'imagen': producto_mas_comprado['url'],
        'frecuencia': producto_mas_comprado_freq
    }


@app.route('/')
def index():
    grafica_info = generar_grafica_compras()
    # Leer datos de compras y productos
    compras_df = pd.read_csv('compras.csv')
    productos_df = pd.read_csv('productos.csv')
    
    # Contar frecuencia de compras por producto
    compras_df['Historial'] = compras_df['Historial'].apply(lambda x: list(map(int, x.split(','))))
    all_products = [item for sublist in compras_df['Historial'] for item in sublist]
    product_counts = pd.Series(all_products).value_counts()
    
    # Crear gráfica de frecuencia de compras
    fig, ax = plt.subplots()
    product_counts.plot(kind='bar', ax=ax)
    ax.set_title('Frecuencia de Compras de Productos')
    ax.set_xlabel('ID del Producto')
    ax.set_ylabel('Frecuencia')
    
    # Guardar la gráfica en un objeto BytesIO
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    
    # Determinar el producto más comprado
    most_purchased_product_id = product_counts.idxmax()
    most_purchased_product = productos_df[productos_df['id'] == most_purchased_product_id].iloc[0]
    
    return render_template(
        'index.html',
        usuario=session.get('usuario'),
        graph_url=f'data:image/png;base64,{graph_url}',
        most_purchased_product=most_purchased_product
    )

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html', usuario=session.get('usuario'))

@app.route('/carrito')
def carrito():
    return render_template('carrito.html', usuario=session.get('usuario'))

# Definir la función leer_usuarios_csv
def leer_usuarios_csv():
    try:
        usuarios = []
        with open('usuarios.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                usuarios.append(row)
        return usuarios
    except Exception as e:
        print(f"Error al leer usuarios.csv: {e}")
        return []

@app.route('/productos')
def productos():
    productos_df = pd.read_csv('productos.csv')
    productos = productos_df.to_dict(orient='records')

    
    usuario_id = session.get('usuario')  
    historial_recomendaciones = []

    if usuario_id:
        # Leer el archivo de compras y filtrar por el usuario actual
        compras_df = pd.read_csv('compras.csv')
        compras_usuario = compras_df[compras_df['id'] == int(usuario_id)]
        
        # Extraer todos los IDs de historial de compras del usuario
        historial_ids = []
        if not compras_usuario.empty:
            for ids in compras_usuario['Historial']:
                if pd.notna(ids):
                    
                    historial_ids.extend([int(id.strip()) for id in ids.split(',') if id.strip().isdigit()])

        # Filtrar los productos que coinciden con los IDs del historial
        historial_recomendaciones = [p for p in productos if int(p['id']) in historial_ids]

    return render_template(
        'productos.html', 
        productos=productos, 
        usuario=usuario_id, 
        historial_recomendaciones=historial_recomendaciones
    )



@app.route('/contacto')
def contacto():
    return render_template('contacto.html', usuario=session.get('usuario'))

# Función para leer compras desde el archivo CSV
def leer_compras_csv():
    compras = []
    try:
        with open('compras.csv', mode='r') as file:
            reader = csv.DictReader(file)
            compras = list(reader)
    except FileNotFoundError:
        pass  # Si el archivo no existe, simplemente devuelve una lista vacía
    return compras

# Función para agregar una compra
def agregar_compra(compra):
    try:
        with open('compras.csv', mode='a', newline='') as file:  # Modo 'a' para agregar
            fieldnames = ['id', 'sexo', 'Historial', 'ultima_actividad']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            
            if file.tell() == 0:
                writer.writeheader()
            
            writer.writerow(compra)
            
            
            print(f"Compra agregada: {compra}")
    except Exception as e:
        print(f"Error al agregar la compra a compras.csv: {e}")


# Función para actualizar el archivo de compras
def actualizar_compras_csv(compras):
    try:
        with open('compras.csv', mode='w', newline='') as file:
            fieldnames = ['id', 'sexo', 'Historial', 'ultima_actividad']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(compras)
    except Exception as e:
        print(f"Error al actualizar compras.csv: {e}")


# Función para registrar historial y actualizar última actividad
def actualizar_historial(usuario_id, producto_id):
    compras = leer_compras_csv()
    historial_actualizado = False

    
    print(f"[DEBUG] Iniciando actualización de historial para usuario {usuario_id} con producto {producto_id}")
    
    for compra in compras:
        if compra['id'] == str(usuario_id):
            historial = compra.get('Historial', '')

            
            if historial:
                historial_ids = historial.split(',')
            else:
                historial_ids = []

            
            print(f"[DEBUG] Historial actual del usuario {usuario_id}: {historial_ids}")

            
            if str(producto_id) not in historial_ids:
                historial_ids.append(str(producto_id))
            
            
            compra['Historial'] = ','.join(historial_ids)
            compra['ultima_actividad'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            
            print(f"[DEBUG] Historial actualizado para el usuario {usuario_id}: {compra['Historial']}")

            historial_actualizado = True
            break
    
    # Si no se encontró el usuario, agregar una nueva entrada
    if not historial_actualizado:
        nueva_compra = {
            'id': str(usuario_id),
            'sexo': 'Desconocido',  
            'Historial': str(producto_id),
            'ultima_actividad': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        compras.append(nueva_compra)

        # Debug: Print para verificar la nueva compra añadida
        print(f"[DEBUG] Nueva compra añadida para el usuario {usuario_id}: {nueva_compra}")
    
    actualizar_compras_csv(compras)
    print(f"[DEBUG] Compra actualizada para usuario {usuario_id}: {compra}")





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')

        
        usuarios = leer_usuarios_csv()  

        # Verificar las credenciales
        for user in usuarios:
            if user['usuario'] == usuario and user['contrasena'] == contrasena:
                session['usuario'] = user['id']  
                flash('Has iniciado sesión correctamente.', 'success')
                return redirect(url_for('index'))

        flash('Usuario o contraseña incorrectos.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('index'))

@app.route('/agregar_al_carrito/<int:producto_id>')
def agregar_al_carrito(producto_id):
    usuario_id = session.get('usuario')
    if not usuario_id:
        flash('Por favor, inicia sesión para realizar una compra.', 'warning')
        return redirect(url_for('login'))
    
    # Debug: Print para verificar llamada y valores de usuario y producto
    print(f"[DEBUG] Producto ID {producto_id} agregado al carrito por el usuario ID {usuario_id}")

   
    actualizar_historial(usuario_id, producto_id)
    
    flash('Producto agregado a tus compras.', 'success')
    return redirect(url_for('productos'))



# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
