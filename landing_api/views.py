from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import db
from datetime import datetime


class LandingAPI(APIView):
    """
    Vista basada en clases para manejar las operaciones CRUD en Firebase Realtime Database.
    Proporciona acceso a la colección de datos de landing a través de una API REST.
    """
    
    name = "Landing API"
    collection_name = "landing"

    def get(self, request):
        """
        Maneja solicitudes GET para obtener todos los elementos de la colección.
        
        Retorna:
            Response: Arreglo JSON con los datos de la colección y código de estado HTTP 200 OK
        """
        try:
            # Referencia a la colección
            ref = db.reference(f'{self.collection_name}')

            # get: Obtiene todos los elementos de la colección
            data = ref.get()

            # Devuelve un arreglo JSON
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error al obtener datos: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Maneja solicitudes POST para crear un nuevo elemento en la colección.
        
        Agrega automáticamente un timestamp formateado al objeto guardado.
        
        Retorna:
            Response: ID del objeto guardado con código de estado HTTP 201 Created, 
                     o error (HTTP 400 o 500)
        """
        try:
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

            # Referencia a la colección
            ref = db.reference(f'{self.collection_name}')

            # Obtener la fecha y hora actual formateada
            current_time = datetime.now()
            custom_format = current_time.strftime("%d/%m/%Y, %I:%M:%S %p").lower().replace('am', 'a. m.').replace('pm', 'p. m.')
            data['timestamp'] = custom_format

            # push: Guarda el objeto en la colección
            new_resource = ref.push(data)

            # Devuelve el id del objeto guardado
            return Response(
                {"id": new_resource.key, "data": data}, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Error al guardar datos: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
