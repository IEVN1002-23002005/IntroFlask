from flask import Flask, jsonify, request 
from flask_mysqldb import MySQL
from flask_cors import CORS #establecer oconexiones servidor cliente

from config import config

app = Flask(__name__)
app.config.from_object(config['development'])

CORS(app)

con = MySQL(app)

@app.route("/alumnos",methods=['GET'])
def lista_alumnos():
    try:
        cursor=con.connection.cursor()
        sql="select * from alumnos"
        cursor.execute(sql)
        datos=cursor.fetchall()
        alumnos=[]
        for fila in datos:
            alumno={"matricula":fila[0],"nombre":fila[1],
                    "apaterno":fila[2],"amaterno":fila[3],
                    "correo":fila[4]}
            alumnos.append(alumno)
        return  jsonify({'alumnos':alumnos,'mensaje':'Lista de alumnos',
                         'exito':True})
 
    except Exception as ex:
        return jsonify({"message": "error {}".format(ex),'exito':False})


def leer_alumno_bd(matricula):
    try:
        cursor=con.connection.cursor()
        sql="SELECT * FROM alumnos WHERE matricula={0}".format(matricula)
        cursor.execute(sql)
        datos=cursor.fetchone()


        if datos != None:
            alumno={"matricula":datos[0],"nombre":datos[1],
                    "apaterno":datos[2],"amaterno":datos[3],
                    "correo":datos[4]}
            return alumno
        else:
            return None
    except Exception as ex:
        raise ex


@app.route("/alumnos/<mat>", methods=['GET'])
def leer_alumno(mat):
    try:
        alumno=leer_alumno_bd(mat)
        if alumno !=None:
            return jsonify({'alumno':alumno,
                            'mensaje':'Alumno encontrado', 'exito':True})
        else:
            return jsonify({'alumno':alumno,
                            'mensaje':'Alumno no encontrado', 'exito':False})
        
    except Exception as ex:
            return jsonify({"message": "error {}".format(ex),'exito':False})


@app.route("/alumnos", methods=["POST"])
def registra_alumno():
    cursor = None
    try:
        datos = request.get_json(silent=True)
        campos = ('matricula', 'nombre', 'apaterno', 'amaterno', 'correo')

        if not isinstance(datos, dict) or any(campo not in datos for campo in campos):
            return jsonify({'mensaje': 'Completa todos los datos del alumno.', 'exito': False}), 400

        matricula = str(datos['matricula']).strip()
        nombre = str(datos['nombre']).strip()
        apaterno = str(datos['apaterno']).strip()
        amaterno = str(datos['amaterno']).strip()
        correo = str(datos['correo']).strip()

        if not matricula.isdigit() or not nombre or not apaterno or not correo:
            return jsonify({'mensaje': 'Matrícula, nombre, apellido paterno y correo son obligatorios.', 'exito': False}), 400

        cursor = con.connection.cursor()
        cursor.execute('SELECT matricula FROM alumnos WHERE matricula = %s', (matricula,))
        if cursor.fetchone() is not None:
            return jsonify({'mensaje': 'La matrícula ya está registrada.', 'exito': False}), 409

        cursor.execute(
            '''INSERT INTO alumnos (matricula, nombre, apaterno, amaterno, correo)
               VALUES (%s, %s, %s, %s, %s)''',
            (matricula, nombre, apaterno, amaterno, correo)
        )
        con.connection.commit()
        return jsonify({'mensaje': 'Alumno registrado correctamente.', 'exito': True}), 201
    except Exception as ex:
        if con.connection:
            con.connection.rollback()
        return jsonify({'mensaje': 'No fue posible registrar el alumno: {}'.format(ex), 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()


@app.route("/alumnos/<mat>", methods=["PUT"])
def actualizar_cursor(mat):
    try:
        alumno=leer_alumno_bd(mat)
        if alumno != None:
            cursor=con.connection.cursor()
            sql="""UPDATE alumnos SET nombre='{0}', 
            apaterno='{1}',
            amaterno='{2}',
            correo='{3}'
            WHERE matricula='{4}'
            """.format(
                request.json['nombre'],
                request.json['apaterno'],
                request.json['amaterno'],
                request.json['correo'],mat)
            cursor.execute(sql)
            con.connection.commit()
            return jsonify({'alumno':alumno,'mensaje':'Alumno actualizado', 'exito':True})
        else:
            return jsonify({'alumno':alumno,'mensaje':'Alumno no encontrado', 'exito':False})                
    except Exception as ex:
        return jsonify({"message": "error {}".format(ex),'exito':False})


@app.route("/alumnos/<mat>", methods=['DELETE'])
def eliminar_alumno(mat):
    try:
        alumno=leer_alumno_bd(mat)
        if alumno != None:
            cursor=con.connection.cursor()
            sql="DELETE FROM alumnos WHERE matricula = {0}".format(mat)
            cursor.execute(sql)
            con.connection.commit()
            return jsonify({'mensaje': "Alumno eliminado",
                            'exito': True})
        else:
            return jsonify({'mensaje': "Alumno no encontrado",
                                        'exito': False})
    except Exception as ex:
        return jsonify({"message": "error {}".format(ex),'exito':False})
        

def pagina_no_encontrada(error):
    return "<h1>Pagina no encontrada</h1>"


if __name__=="__main__":
    app.register_error_handler(404,pagina_no_encontrada)
    app.run(host='0.0.0.0',port=5000)
