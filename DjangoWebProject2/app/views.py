"""
Definition of views.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.db import connection
import json
import re

def paginaIndex(request):
    return render(request, 'index.html')

def validar_rut(rut):
    """Valida un RUT chileno"""
    rut = rut.replace(".", "").replace("-", "")  # Elimina puntos y guión

    if len(rut) < 2:
        return False

    cuerpo = rut[:-1]
    dv = rut[-1].upper()

    # Valida si el cuerpo contiene solo números
    if not cuerpo.isdigit():
        return False

    # Calcula el dígito verificador
    total = 0
    factor = 2
    for i in range(len(cuerpo) - 1, -1, -1):
        total += int(cuerpo[i]) * factor
        factor = factor + 1 if factor < 7 else 2

    resto = total % 11
    dv_calculado = 11 - resto
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'

    # Compara el dígito verificador calculado con el proporcionado
    return dv == str(dv_calculado)

def registro_cliente(request):
    regiones = []
    comunas = []
    registro_cliente_messages = []

    # PROC REGIONES
    try:
        with connection.cursor() as cursor:
            cursor.execute('EXEC REGION_SELECCIONA')
            rows = cursor.fetchall()
            regiones = [
                {'IdRegion': row[0], 'CodRegion': row[1], 'Region': row[2]}
                for row in rows
            ]
    except Exception as e:
        print(f"Error al obtener las regiones: {str(e)}")

    # REGISTRO CLIENTE
    if request.method == 'POST':
        rut_cliente = request.POST.get('rutCliente')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('mail')
        id_comuna = request.POST.get('comuna')
        direccion = request.POST.get('direccion')

        if not validar_rut(rut_cliente):
            registro_cliente_messages = [
                {"type": "error", "text": "RUT invalido. Por favor, ingrese un RUT valido."}
            ]
            # Volver a renderizar la página con los campos llenos excepto el RUT
            return render(request, 'home.html', {
                'regiones': regiones,
                'comunas': comunas,
                'registro_cliente_messages': registro_cliente_messages,
                'rut_cliente': rut_cliente, 
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'direccion': direccion,
            })
        else:
            try:
                # Llamar al procedimiento almacenado para insertar/actualizar el cliente
                with connection.cursor() as cursor:
                    cursor.execute(
                        'EXEC [dbo].[ValidarCliente] @RutCliente=%s, @Nombre=%s, @Apellido=%s, @Email=%s, @IdComuna=%s, @Direccion=%s',
                        [rut_cliente, nombre, apellido, email, id_comuna, direccion]
                    )
                    resultado = cursor.fetchone()

                    if resultado and resultado[0] == 'u':
                        registro_cliente_messages = [
                            {"type": "success", "text": "Cliente actualizado exitosamente."}
                        ]
                    elif resultado and resultado[0] == 'i':
                        registro_cliente_messages = [
                            {"type": "success", "text": "Cliente registrado exitosamente."}
                        ]
                    else:
                        registro_cliente_messages = [
                            {"type": "error", "text": "No se pudo completar la operacion. Intentalo nuevamente."}
                        ]
            except Exception as e:
                print(f"Error al ejecutar el procedimiento almacenado: {str(e)}")
                registro_cliente_messages = [
                    {"type": "error", "text": f"Error al registrar o actualizar el cliente: {str(e)}"}
                ]

    return render(request, 'home.html', {
        'regiones': regiones,
        'comunas': comunas,
        'registro_cliente_messages': registro_cliente_messages,
    })


# Vista para manejar la carga dinámica de comunas
def get_comunas(request):
    cod_region = request.GET.get('CodRegion')
    comunas = []
    try:
        if cod_region != 0:
            with connection.cursor() as cursor:
                cursor.execute('EXEC COMUNA_SELECCIONA @CodRegion=%s', [cod_region])
                rows = cursor.fetchall()
                comunas = [
                    {'IdComuna': row[0], 'CodRegion': row[1], 'CodComuna': row[2], 'Comuna': row[3]}
                    for row in rows
                ]
        else:
            print("No hay comunas")
            print(comunas)
    except Exception as e:
        print(f"Error al obtener las comunas: {str(e)}")

    return JsonResponse({'comunas': comunas})


def listar_clientes(request):
    clientes = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('EXEC [dbo].[ListarCliente]')
            rows = cursor.fetchall()
            clientes = [
                {
                    'id': row[0],
                    'rutCliente': row[1],
                    'nombre': row[2],
                    'apellido': row[3],
                    'email': row[4],
                    'region': row[8],
                    'comuna': row[7], 
                }
                for row in rows
            ]
    except Exception as e:
        print(f"Error al obtener los clientes: {str(e)}")
    return JsonResponse({'clientes': clientes})


def get_cliente(request, rutCliente):
    try:
        with connection.cursor() as cursor:
            cursor.execute('EXEC [dbo].[ObtenerCliente] @RutCliente=%s', [rutCliente])
            row = cursor.fetchone()
            if row:
                cliente = {
                    "rutCliente": row[1], 
                    "nombre": row[2],   
                    "apellido": row[3],  
                    "email": row[4],    
                    "direccion": row[6], 
                    "region": row[8],       
                    "comuna": row[7],
                    "IdComuna": row[5],
                    "CodRegion": row[9]  # Añadir CodRegion al objeto cliente
                }

                # Ahora, usamos el CodRegion para obtener las comunas
                cursor.execute('EXEC [dbo].[ObtenerComunas] @CodRegion=%s', [row[9]])  # Usar CodRegion de la fila obtenida
                comunas = cursor.fetchall()

                # Verificar si se obtienen comunas
                if comunas:
                    comunas_data = [{"Comuna": c[1], "IdComuna": c[0]} for c in comunas]
                else:
                    comunas_data = []
                    print("No se encontraron comunas para la region:", row[9])

                # Agregar las comunas al cliente
                cliente["comunas"] = comunas_data
                
                return JsonResponse(cliente)

            else:
                return JsonResponse({"error": "Cliente no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error al procesar la solicitud: {str(e)}"}, status=500)


def eliminar_cliente(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_cliente = data.get('idCliente')

            if not id_cliente:
                return JsonResponse({'success': False, 'registro_cliente_messages': [{"type": "error", "text": "No se proporciono el ID del cliente."}]}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("EXEC EliminarCliente @idCliente = %s", [id_cliente])

            # Mensaje de confirmación
            registro_cliente_messages = [
                {"type": "success", "text": "Cliente eliminado correctamente."}
            ]

            return JsonResponse({'success': True, 'registro_cliente_messages': registro_cliente_messages}, status=200)

        except Exception as e:
            # Mensaje de error
            registro_cliente_messages = [
                {"type": "error", "text": f"Error al eliminar el cliente: {str(e)}"}
            ]
            return JsonResponse({'success': False, 'registro_cliente_messages': registro_cliente_messages}, status=500)
