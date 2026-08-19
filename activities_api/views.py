from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import db
from datetime import datetime
import uuid


class ActivitiesListCreate(APIView):
    """
    Vista para listar todas las actividades académicas (GET) 
    y crear nuevas actividades (POST).
    
    Esta vista actúa como punto de entrada central para la gestión
    de actividades en la organización educativa.
    """
    
    name = "Activities List and Create"
    collection_name = "actividades"

    def get(self, request):
        """
        Maneja solicitudes GET para obtener todas las actividades académicas.
        
        Retorna:
            Response: Lista limpia de actividades sin claves de Firebase,
                     con código de estado HTTP 200 OK
        """
        try:
            # Referencia a la colección de actividades en Firebase
            ref = db.reference(f'{self.collection_name}')
            
            # Obtiene todos los elementos de la colección
            activities_dict = ref.get()
            
            # Convertir a lista limpia sin claves de Firebase
            if activities_dict is None:
                activities_list = []
            else:
                activities_list = [activity for activity in activities_dict.values()]
            
            return Response(activities_list, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error al obtener actividades: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Maneja solicitudes POST para crear una nueva actividad académica.
        
        Valida campos requeridos:
            - titulo (string): Título de la actividad
            - descripcion (string): Descripción detallada de la actividad
            - responsable (string): Persona responsable de la actividad
        
        Agrega automáticamente:
            - id: Identificador único (UUID)
            - fecha_creacion: Timestamp de creación en formato personalizado
        
        Retorna:
            Response: Objeto con ID y datos de la actividad creada (HTTP 201 Created),
                     o error si faltan campos requeridos (HTTP 400) o error del servidor (HTTP 500)
        """
        try:
            data = request.data
            
            # Validar campos requeridos
            campos_requeridos = ['titulo', 'descripcion', 'responsable']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in data]
            
            if campos_faltantes:
                return Response(
                    {
                        'error': 'Faltan campos requeridos.',
                        'campos_faltantes': campos_faltantes
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Referencia a la colección
            ref = db.reference(f'{self.collection_name}')
            
            # Generar ID único para la actividad
            activity_id = str(uuid.uuid4())
            
            # Obtener fecha y hora actual formateada
            current_time = datetime.now()
            formatted_date = current_time.strftime("%d/%m/%Y, %I:%M:%S %p").lower().replace('am', 'a. m.').replace('pm', 'p. m.')
            
            # Construir objeto de actividad
            activity_data = {
                'id': activity_id,
                'titulo': data['titulo'],
                'descripcion': data['descripcion'],
                'responsable': data['responsable'],
                'fecha_creacion': formatted_date
            }
            
            # Guardar en Firebase usando push para generar una clave automática
            new_activity = ref.push(activity_data)
            
            # Retornar respuesta de éxito (sin mostrar el ID de Firebase)
            return Response(
                {
                    'mensaje': 'Actividad registrada exitosamente.',
                    'actividad': activity_data
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {'error': f'Error al crear actividad: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ActivityDetail(APIView):
    """
    Vista para obtener detalles de una actividad específica (GET),
    actualizar una actividad existente (PUT/PATCH) y eliminar una actividad (DELETE).
    """
    
    name = "Activity Detail"
    collection_name = "actividades"

    def _find_activity_by_id(self, activity_id):
        """
        Busca una actividad por su ID en Firebase.
        
        Argumentos:
            activity_id: ID de la actividad a buscar
        
        Retorna:
            tuple: (clave_firebase, datos_actividad) o (None, None) si no se encuentra
        """
        try:
            ref = db.reference(f'{self.collection_name}')
            activities = ref.get()
            
            if activities is None:
                return None, None
            
            # Buscar por ID en los datos
            for firebase_key, activity_data in activities.items():
                if activity_data.get('id') == activity_id:
                    return firebase_key, activity_data
            
            return None, None
        except Exception:
            return None, None

    def get(self, request, activity_id):
        """
        Maneja solicitudes GET para obtener una actividad específica.
        
        Argumentos:
            activity_id: ID único de la actividad
        
        Retorna:
            Response: Datos de la actividad con ID al principio (HTTP 200) o error (HTTP 404 o 500)
        """
        try:
            firebase_key, activity = self._find_activity_by_id(activity_id)
            
            if activity is None:
                return Response(
                    {'error': 'Actividad no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Construir respuesta con ID al principio
            response_data = {
                'id': activity.get('id'),
                'titulo': activity.get('titulo'),
                'descripcion': activity.get('descripcion'),
                'responsable': activity.get('responsable'),
                'fecha_creacion': activity.get('fecha_creacion')
            }
            
            # Agregar campos opcionales si existen
            if 'fecha_actualizacion' in activity:
                response_data['fecha_actualizacion'] = activity.get('fecha_actualizacion')
            if 'activa' in activity:
                response_data['activa'] = activity.get('activa')
            if 'fecha_eliminacion' in activity:
                response_data['fecha_eliminacion'] = activity.get('fecha_eliminacion')
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error al obtener actividad: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, activity_id):
        """
        Maneja solicitudes PUT para reemplazar completamente una actividad.
        
        Requiere todos los campos:
            - titulo (requerido)
            - descripcion (requerido)
            - responsable (requerido)
        
        Nota: El ID de la actividad no puede ser modificado.
        
        Argumentos:
            activity_id: ID único de la actividad a actualizar
        
        Retorna:
            Response: Datos actualizados con ID al principio (HTTP 200) o error (HTTP 400, 404 o 500)
        """
        try:
            data = request.data
            firebase_key, existing_activity = self._find_activity_by_id(activity_id)
            
            if existing_activity is None:
                return Response(
                    {'error': 'Actividad no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validar campos requeridos
            campos_requeridos = ['titulo', 'descripcion', 'responsable']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in data]
            
            if campos_faltantes:
                return Response(
                    {
                        'error': 'Faltan campos requeridos para actualizar.',
                        'campos_faltantes': campos_faltantes
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Preparar datos actualizados (mantener ID y fecha de creación original)
            # No incluir fecha_actualizacion
            updated_data = {
                'id': activity_id,
                'titulo': data['titulo'],
                'descripcion': data['descripcion'],
                'responsable': data['responsable'],
                'fecha_creacion': existing_activity.get('fecha_creacion')
            }
            
            # Actualizar en Firebase
            ref = db.reference(f'{self.collection_name}/{firebase_key}')
            ref.set(updated_data)
            
            return Response(
                {
                    'mensaje': 'Actividad actualizada exitosamente.',
                    'actividad': updated_data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': f'Error al actualizar actividad: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, activity_id):
        """
        Maneja solicitudes PATCH para actualizar parcialmente una actividad.
        
        Solo actualiza los campos proporcionados, manteniendo los demás valores.
        Campos que pueden actualizarse: titulo, descripcion, responsable
        
        Ejemplo de JSON:
        {
            "titulo": "Nuevo título"
        }
        
        Argumentos:
            activity_id: ID único de la actividad a actualizar
        
        Retorna:
            Response: Datos actualizados parcialmente con ID al principio (HTTP 200) o error (HTTP 404 o 500)
        """
        try:
            data = request.data
            firebase_key, existing_activity = self._find_activity_by_id(activity_id)
            
            if existing_activity is None:
                return Response(
                    {'error': 'Actividad no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Actualizar solo los campos proporcionados
            updated_data = existing_activity.copy()
            
            # Campos que pueden actualizarse parcialmente
            campos_actualizables = ['titulo', 'descripcion', 'responsable']
            for campo in campos_actualizables:
                if campo in data:
                    updated_data[campo] = data[campo]
            
            # No guardar fecha_actualizacion
            # Eliminar si existe algún campo de control temporal
            updated_data.pop('fecha_actualizacion', None)
            
            # Actualizar en Firebase
            ref = db.reference(f'{self.collection_name}/{firebase_key}')
            ref.set(updated_data)
            
            # Construir respuesta ordenada
            response_data = {
                'id': updated_data.get('id'),
                'titulo': updated_data.get('titulo'),
                'descripcion': updated_data.get('descripcion'),
                'responsable': updated_data.get('responsable'),
                'fecha_creacion': updated_data.get('fecha_creacion')
            }
            
            return Response(
                {
                    'mensaje': 'Actividad actualizada parcialmente.',
                    'actividad': response_data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': f'Error al actualizar actividad: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, activity_id):
        """
        Maneja solicitudes DELETE para eliminar una actividad.
        
        Nota: La eliminación es física - el registro se elimina completamente de Firebase.
        
        Argumentos:
            activity_id: ID único de la actividad a eliminar
        
        Retorna:
            Response: Mensaje de éxito (HTTP 204) o error (HTTP 404 o 500)
        """
        try:
            firebase_key, existing_activity = self._find_activity_by_id(activity_id)
            
            if existing_activity is None:
                return Response(
                    {'error': 'Actividad no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Eliminación física: borrar completamente de Firebase
            ref = db.reference(f'{self.collection_name}/{firebase_key}')
            ref.delete()
            
            return Response(
                {'mensaje': 'Actividad eliminada exitosamente.'},
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Exception as e:
            return Response(
                {'error': f'Error al eliminar actividad: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
