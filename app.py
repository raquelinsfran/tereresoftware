from flask import Flask, render_template, request, redirect, url_for, send_file,  jsonify
from flask_mysqldb import MySQL
import os

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'  # Host de la base de datos
app.config['MYSQL_USER'] = 'root'      # Usuario de la base de datos
app.config['MYSQL_PASSWORD'] = ''      # Contraseña del usuario
app.config['MYSQL_DB'] = 'nueva_contactos'  # Nombre de la base de datos

# Inicialización de la conexión con MySQL

mysql = MySQL(app)

# ------------------- ABM para Contactos (Tabla 1) -------------------

@app.route('/')
def index():
        #Renderiza la página de inicio.
    return render_template('index.html')

@app.route('/list_contact')
def list_contact():
    #Lista todos los contactos de tabla_1.
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tabla_1")  # Consulta para obtener todos los contactos
    contacts = cur.fetchall()
    cur.close()
    return render_template('list_contact.html', contacts=contacts)

# ------------------- ABM para Contactos (Tabla 1) -------------------

@app.route('/edit_contact/<int:id>', methods=['GET', 'POST'])
def update_contact(id):
    #Edita un contacto existente en tabla_1.
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tabla_1 WHERE ID = %s", (id,))
    contact = cur.fetchone()
    cur.close()

    if contact is None:
        # Si no se encuentra el cliente, redirigir o mostrar un mensaje
        return "Cliente no encontrado", 404  # o redirigir a otra página

    if request.method == 'POST':
        # Actualizar contacto con los datos del formulario
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE tabla_1
            SET FULLNAME = %s, PHONE = %s, EMAIL = %s
            WHERE ID = %s
        """, (fullname, phone, email, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('list_contact'))
    return render_template('edit_clientenuevo.html', contact=contact)



@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    #Agrega un nuevo contacto a tabla_1.
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO tabla_1 (FULLNAME, PHONE, EMAIL)
            VALUES (%s, %s, %s)
        """, (fullname, phone, email))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('list_contact'))
    return render_template('add_contact.html')

@app.route('/delete_contact/<int:id>', methods=['POST'])
def delete_contact(id):
    #Elimina un contacto de tabla_1.
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM tabla_1 WHERE ID = %s", (id,))
        mysql.connection.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
    return redirect(url_for('list_contact'))


# ------------------- ABM para Clientes Fijos (Tabla 2) -------------------

@app.route('/clientesfijos')
def clientes_fijos():
    # Captura el término de búsqueda del query string
    search_query = request.args.get('search', '').strip()
    
    cur = mysql.connection.cursor()
    if search_query:
        # Realiza una búsqueda parcial ignorando mayúsculas y minúsculas
        query = "SELECT * FROM tabla_2 WHERE FULLNAME LIKE %s"
        cur.execute(query, (f"%{search_query}%",))
    else:
        # Obtiene todos los clientes si no hay búsqueda
        cur.execute("SELECT * FROM tabla_2")
    fixed_clients = cur.fetchall()
    cur.close()
    
    return render_template('clientes_fijos.html', clients=fixed_clients)


@app.route('/add_fixed_client', methods=['GET', 'POST'])
def add_fixed_client():
    #Agrega un cliente fijo a tabla_2.
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO tabla_2 (FULLNAME, PHONE, EMAIL)
            VALUES (%s, %s, %s)
        """, (fullname, phone, email))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('clientes_fijos'))
    return render_template('add_client.html')


@app.route('/edit_fixed_client/<int:id>', methods=['GET', 'POST'])
def edit_fixed_client(id):
    # Obtiene los datos del cliente desde tabla_2 usando el ID
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tabla_2 WHERE ID = %s", (id,))
    client = cur.fetchone()  
    cur.close()

    if request.method == 'POST':
        # Obtén los datos del formulario
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        
        # Actualiza los datos del cliente en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE tabla_2
            SET FULLNAME = %s, EMAIL = %s, PHONE = %s
            WHERE ID = %s
        """, (fullname, email, phone, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('clientes_fijos'))

    return render_template('edit_clientefijo.html', client=client)

@app.route('/delete_fixed_client/<int:id>', methods=['POST'])
def delete_fixed_client(id):
    #Elimina un cliente fijo de tabla_2.
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM tabla_2 WHERE ID = %s", (id,))
        mysql.connection.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
    return redirect(url_for('clientes_fijos'))

# ------------------- Proyectos para Clientes Fijos -------------------

@app.route('/proyectos_cliente_fijo/<int:cliente_id>')
def proyectos_cliente_fijo(cliente_id):
    # Lista los proyectos asociados a un cliente fijo específico.
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM detalles_proyectos_clientes_fijos WHERE CLIENTE_FIJO_ID = %s", (cliente_id,))
    proyectos = cur.fetchall()
    cur.close()
    return render_template('proyectos_cliente_fijo.html', proyectos=proyectos, cliente_id=cliente_id)

@app.route('/add_proyecto/<int:cliente_id>', methods=['GET', 'POST'])
def add_proyecto(cliente_id):
    # Agrega un nuevo proyecto para un cliente fijo.
    if request.method == 'POST':
        proyecto = request.form['proyecto']
        fecha_entrega = request.form['fecha_entrega']
        monto_proyecto = request.form['monto_proyecto']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO detalles_proyectos_clientes_fijos (CLIENTE_FIJO_ID, PROYECTO, FECHA_ENTREGA, MONTO_PROYECTO)
            VALUES (%s, %s, %s, %s)
        """, (cliente_id, proyecto, fecha_entrega, monto_proyecto))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('proyectos_cliente_fijo', cliente_id=cliente_id))
    return render_template('add_proyecto.html', cliente_id=cliente_id)

@app.route('/delete_proyecto/<int:proyecto_id>', methods=['POST'])
def delete_proyecto(proyecto_id):
    # Elimina un proyecto basado en su ID.
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM detalles_proyectos_clientes_fijos WHERE ID = %s", (proyecto_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(request.referrer)

# ------------------- Dashboard -------------------

@app.route('/dashboard')
def dashboard():
    # Muestra un resumen de datos principales: número de contactos, clientes fijos, proyectos activos y un desglose de proyectos por cliente.
    cur = mysql.connection.cursor()
    
    # Obtener los datos de los contactos
    cur.execute("SELECT COUNT(*) FROM tabla_1")
    total_contacts = cur.fetchone()[0]

    # Obtener los datos de los clientes fijos
    cur.execute("SELECT COUNT(*) FROM tabla_2")
    total_fixed_clients = cur.fetchone()[0]

    # Obtener el número de proyectos activos
    cur.execute("SELECT COUNT(*) FROM detalles_proyectos_clientes_fijos")
    active_projects = cur.fetchone()[0]

    # Obtener los proyectos por cliente
    cur.execute("SELECT CLIENTE_FIJO_ID, COUNT(*) FROM detalles_proyectos_clientes_fijos GROUP BY CLIENTE_FIJO_ID")
    project_data = cur.fetchall()
    
    # Preparar los datos para el gráfico
    project_labels = [row[0] for row in project_data]
    project_counts = [row[1] for row in project_data]
    
    cur.close()
    
    return render_template('dashboard.html', total_contacts=total_contacts, 
                        total_fixed_clients=total_fixed_clients, 
                        active_projects=active_projects, 
                        project_labels=project_labels, 
                        project_data=project_counts)


# ------------------- ABM para Usuarios -------------------

@app.route('/usuarios')
def usuarios():
    #Lista todos los usuarios registrados en la base de datos.
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    users = cur.fetchall()
    cur.close()
    return render_template('usuarios.html', users=users)

@app.route('/add_usuario', methods=['GET', 'POST'])
def add_usuario():
    # Agrega un nuevo usuario al sistema.
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        rol = request.form['rol']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO usuarios (NOMBRE, EMAIL, ROL)
            VALUES (%s, %s, %s)
        """, (nombre, email, rol))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('usuarios'))
    return render_template('add_usuario.html')

@app.route('/edit_usuario/<int:id>', methods=['GET', 'POST'])
def edit_usuario(id):
    #Edita los datos de un usuario existente.
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE ID = %s", (id,))
    user = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        nombre = request.form['nombre']  # Cambié fullname a nombre
        email = request.form['email']
        rol = request.form['rol']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE usuarios
            SET NOMBRE = %s, EMAIL = %s, ROL = %s
            WHERE ID = %s
        """, (nombre, email, rol, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('usuarios'))
    return render_template('edit_usuario.html', user=user)

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    #Elimina un usuario del sistema.
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE ID = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('usuarios'))

# ------------------- Reportes -------------------

@app.route('/proyectos_por_cliente/<int:cliente_id>', methods=['GET'])
def proyectos_por_cliente(cliente_id):
    # Obtiene los proyectos asociados al cliente seleccionado
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT ID, PROYECTO 
        FROM detalles_proyectos_clientes_fijos 
        WHERE CLIENTE_FIJO_ID = %s
    """, (cliente_id,))
    proyectos = cur.fetchall()
    cur.close()

    # Convertir los resultados a JSON
    proyectos_json = [{'id': proyecto[0], 'nombre': proyecto[1]} for proyecto in proyectos]
    return jsonify(proyectos_json)


@app.route('/reportes', methods=['GET', 'POST'])
def reportes():
    # Genera reportes en formato .txt de los proyectos seleccionados
    if request.method == 'POST':
        proyecto_id = request.form['proyecto']
        estado = request.form['estado']
        
        # Actualizar el estado del proyecto seleccionado
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE detalles_proyectos_clientes_fijos 
            SET ESTADO = %s 
            WHERE ID = %s
        """, (estado, proyecto_id))
        mysql.connection.commit()

        # Consultar los datos del proyecto actualizado
        cur.execute("""
            SELECT * FROM detalles_proyectos_clientes_fijos 
            WHERE ID = %s
        """, (proyecto_id,))
        proyectos = cur.fetchall()
        cur.close()

        # Generar el reporte en un archivo .txt
        reporte = "Reporte de Proyecto\n\n"
        for proyecto in proyectos:
            reporte += f"Proyecto: {proyecto[2]}\n"
            reporte += f"Fecha de Entrega: {proyecto[3]}\n"
            reporte += f"Monto: {proyecto[4]}\n"
            reporte += f"Estado: {proyecto[5]}\n"
            reporte += "-" * 50 + "\n"
        
        # Guardar el reporte en un archivo .txt
        with open("reporte_proyecto.txt", "w") as file:
            file.write(reporte)
        
        # Descargar el archivo
        return send_file("reporte_proyecto.txt", as_attachment=True)
    
    # Obtener todos los clientes para que el usuario pueda seleccionarlos
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID, FULLNAME FROM tabla_2")
    clientes = cur.fetchall()
    cur.close()

    return render_template('reportes.html', clientes=clientes)

# ------------------- Configuración del Servidor -------------------

if __name__ == '__main__':
    app.run(debug=True)
