class Carrito{
    //Añadir el producto al carrito
    comprarProducto(e){
        e.preventDefault();
        if(e.target.classList.contains('agregar-carrito')){
            const producto = e.target.parentElement;
            this.leerDatosProducto(producto);
            //console.log(producto);            
        }
    }

    leerDatosProducto(producto){
        const infoProducto ={
            imagen : producto.querySelector('img').src,
            titulo : producto.querySelector('h5').textContent,
            precio : producto.querySelector('.precio').textContent,
            id : producto.querySelector('a').getAttribute('data-id'),
            cantidad : 1
        }
        let productosLS;
        productosLS = this.obtenerProductosLocalStorage();
        productosLS.forEach(function(productoLS){
            if(productoLS.id === infoProducto.id){
                productosLS = productoLS.id;
            }
        });
        if(productosLS === infoProducto.id){
            //console.log('El producto ya está agregado');
            Swal.fire({
                icon: 'warning',
                title: 'No tenemos stock suficiente, prueba con menos unidades',
                timer: 2500,
                showConfirmButton: false
            })
        }
        else{
            this.insertarCarrito(infoProducto);
            //console.log(infoProducto);
            Swal.fire({
                icon: 'success',
                title: 'Agregado',
                timer: 2500,
                showConfirmButton: false
            })
        }
        
    }

    insertarCarrito(producto){
        const row = document.createElement('tr');
        row.innerHTML= `
        <td>
        <img src="${producto.imagen}" width=100>
        </td>
        <td>${producto.titulo}</td>
        <td>${producto.precio}</td>
        <td>
        <a href="#" class="borrar-producto fas fa-times-circle" data-id="${producto.id}"></a>
        </td>
        `;
        listaProductos.appendChild(row);
        this.guardarProductosLocalStorage(producto);
    }

    eliminarProducto(e){
        e.preventDefault();
        let producto, productoID;
        if(e.target.classList.contains('borrar-producto')){
            e.target.parentElement.parentElement.remove();
            producto = e.target.parentElement.parentElement;
            productoID = producto.querySelector('a').getAttribute('data-id');
            Swal.fire({
                icon: 'info',
                title: 'Eliminado',
                timer: 2500,
                showConfirmButton: false
            })
        }
        this.eliminarProductoLocalStorage(productoID);
        this.calcularTotal();        
    }

    vaciarCarrito(e){
        e.preventDefault();
        while(listaProductos.firstChild){
            listaProductos.removeChild(listaProductos.firstChild);
            Swal.fire({
                icon: 'info',
                title: 'Carrito Vacío',
                timer: 2500,
                showConfirmButton: false
            })
        }
        this.vaciarLocalStorage();
        return false;
    }

    guardarProductosLocalStorage(producto){
        let productos;
        productos = this.obtenerProductosLocalStorage();
        productos.push(producto);
        localStorage.setItem('productos', JSON.stringify(productos));
    }

    obtenerProductosLocalStorage(){
        let productoLS;
        if(localStorage.getItem('productos')===null){
            productoLS = [];
        }
        else{
            productoLS = JSON.parse(localStorage.getItem('productos'));
        }
        return productoLS;
    }

    eliminarProductoLocalStorage(productoID){
        let productosLS;
        productosLS = this.obtenerProductosLocalStorage();
        productosLS.forEach(function(productoLS, index){
            if(productoLS.id === productoID){
                productosLS.splice(index, 1);
            }
        });
        localStorage.setItem('productos', JSON.stringify(productosLS));
    }

    leerLocalStorage(){
        let productosLS;
        productosLS = this.obtenerProductosLocalStorage();
        productosLS.forEach(function(producto){
            const row = document.createElement('tr');
            row.innerHTML= `
            <td>
            <img src="${producto.imagen}" width=100>
            </td>
            <td>${producto.titulo}</td>
            <td>${producto.precio}</td>
            <td>
            <a href="#" class="borrar-producto fas fa-times-circle" data-id="${producto.id}"></a>
            </td>
            `;
            listaProductos.appendChild(row);
        });
    }

    leerLocalStorageCompra(){
        let productosLS;
        productosLS = this.obtenerProductosLocalStorage();
        productosLS.forEach(function(producto){
            const row = document.createElement('tr');
            row.innerHTML= `
            <td>
            <img src="${producto.imagen}" width=100>
            </td>
            <td>${producto.titulo}</td>
            <td>${producto.precio}</td>
            <td>${producto.cantidad}</td>
            <td>${producto.precio * producto.cantidad}</td>
            <td>
            <a href="#" class="borrar-producto fas fa-times-circle" data-id="${producto.id}"></a>
            </td>
            `;
            listaCompra.appendChild(row);
        });
    }    

    vaciarLocalStorage(){
        localStorage.clear();        
    }

    procesarPedido(e) {
        e.preventDefault();
        if (this.obtenerProductosLocalStorage().length === 0) {
            Swal.fire({
                icon: 'error',
                title: 'El carrito está vacío, agrega un producto',
                timer: 2500,
                showConfirmButton: false
            });
        } else {
            // Redirige a la ruta Flask para carrito
            location.href = "/carrito"; // Asegúrate de que esta ruta esté definida en tu Flask app.
        }
    }
    

    calcularTotal(){
        let productoLS;
        let total = 0, subtotal = 0, igv = 0;
        productoLS = this.obtenerProductosLocalStorage();
    
        for(let i = 0; i < productoLS.length; i++){
            let precio = parseFloat(productoLS[i].precio) || 0; // Asegura que el precio sea un número
            let cantidad = parseInt(productoLS[i].cantidad) || 0; // Asegura que la cantidad sea un número entero
            let element = precio * cantidad; // Calcula el total del producto
    
            total += element; // Suma al total
        }
    
        igv = parseFloat(total * 0.18).toFixed(2); // Calcula el IGV (18%)
        subtotal = parseFloat(total - igv).toFixed(2); // Calcula el subtotal
    
        document.getElementById('subtotal').innerHTML = "S/. " + subtotal; // Muestra el subtotal
        document.getElementById('igv').innerHTML = "S/. " + igv; // Muestra el IGV
        document.getElementById('total').value = "S/. " + total.toFixed(2); // Muestra el total
    }
    
    
}
document.addEventListener('DOMContentLoaded', function() {
    const botonesComprar = document.querySelectorAll('.agregar-carrito');

    botonesComprar.forEach(boton => {
        boton.addEventListener('click', function(event) {
            event.preventDefault();
            const productoId = this.getAttribute('data-id');

            // Hacer una solicitud a Flask para agregar el producto
            fetch(`/agregar_al_carrito/${productoId}`)
                .then(response => {
                    if (response.ok) {
                        console.log(`Producto con ID ${productoId} agregado al carrito`);
                        // Puedes agregar aquí alguna lógica adicional, como actualizar la UI
                    } else {
                        console.error('Error al agregar el producto al carrito');
                    }
                })
                .catch(error => console.error('Error en la solicitud:', error));
        });
    });
});


