from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import uuid

# Simulación de base de datos local en memoria
data_list = []

# Añadiendo algunos datos de ejemplo para probar el GET
data_list.append({'id': str(uuid.uuid4()), 'name': 'User01', 'email': 'user01@example.com', 'is_active': True})
data_list.append({'id': str(uuid.uuid4()), 'name': 'User02', 'email': 'user02@example.com', 'is_active': True})
data_list.append({'id': str(uuid.uuid4()), 'name': 'User03', 'email': 'user03@example.com', 'is_active': False}) # Ejemplo de item inactivo

class DemoRestApi(APIView):
    name = "Demo REST API"

    def get(self, request):
        """
        Maneja solicitudes GET para obtener todos los elementos activos.
        
        Retorna:
            Response: Lista de elementos activos con código de estado HTTP 200 OK
        """
        # Filtra la lista para incluir solo los elementos donde 'is_active' es True
        active_items = [item for item in data_list if item.get('is_active', False)]
        return Response(active_items, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Maneja solicitudes POST para crear un nuevo elemento.
        
        Validaciones:
            - Campos requeridos: 'name' y 'email'
        
        Retorna:
            Response: Mensaje de éxito con los datos guardados (HTTP 201) o error (HTTP 400)
        """
        data = request.data

        # Validación mínima
        if 'name' not in data or 'email' not in data:
            return Response({'error': 'Faltan campos requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        data['id'] = str(uuid.uuid4())
        data['is_active'] = True
        data_list.append(data)

        return Response({'message': 'Dato guardado exitosamente.', 'data': data}, status=status.HTTP_201_CREATED)


class DemoRestApiItem(APIView):
    name = "Demo REST API Item"

    def _find_item(self, item_id):
        """
        Busca un elemento por su identificador.
        
        Argumentos:
            item_id: El identificador del elemento a buscar
        
        Retorna:
            tuple: (elemento, índice) o (None, -1) si no se encuentra
        """
        for index, item in enumerate(data_list):
            if item['id'] == item_id:
                return item, index
        return None, -1

    def get(self, request, id):
        """
        Maneja solicitudes GET para obtener un elemento específico.
        
        Argumentos:
            id: El identificador del elemento a recuperar
        
        Retorna:
            Response: Elemento encontrado (HTTP 200) o error (HTTP 404)
        """
        item, _ = self._find_item(id)
        if not item:
            return Response({'error': 'Elemento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(item, status=status.HTTP_200_OK)

    def put(self, request, id):
        """
        Maneja solicitudes PUT para reemplazar completamente un elemento.
        
        Nota: El identificador no puede ser modificado en el cuerpo de la solicitud.
        
        Argumentos:
            id: El identificador del elemento a reemplazar
        
        Retorna:
            Response: Elemento actualizado (HTTP 200) o error (HTTP 404 o 400)
        """
        data = request.data
        item, index = self._find_item(id)

        if not item:
            return Response({'error': 'Elemento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Validación mínima
        if 'name' not in data or 'email' not in data:
            return Response({'error': 'Faltan campos requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        # Reemplazar completamente el elemento, manteniendo el id
        data['id'] = id
        data_list[index] = data

        return Response({'message': 'Dato actualizado exitosamente.', 'data': data}, status=status.HTTP_200_OK)

    def patch(self, request, id):
        """
        Maneja solicitudes PATCH para actualizar parcialmente un elemento.
        
        Solo actualiza los campos proporcionados en el cuerpo de la solicitud.
        
        Argumentos:
            id: El identificador del elemento a actualizar
        
        Retorna:
            Response: Elemento actualizado (HTTP 200) o error (HTTP 404)
        """
        data = request.data
        item, index = self._find_item(id)

        if not item:
            return Response({'error': 'Elemento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualización parcial: solo actualizar los campos proporcionados
        for key, value in data.items():
            if key != 'id':  # El id no puede ser modificado
                item[key] = value

        data_list[index] = item

        return Response({'message': 'Dato actualizado parcialmente.', 'data': item}, status=status.HTTP_200_OK)

    def delete(self, request, id):
        """
        Maneja solicitudes DELETE para eliminar lógicamente un elemento.
        
        La eliminación es lógica: marca el elemento como inactivo.
        
        Argumentos:
            id: El identificador del elemento a eliminar
        
        Retorna:
            Response: Mensaje de éxito (HTTP 204) o error (HTTP 404)
        """
        item, index = self._find_item(id)

        if not item:
            return Response({'error': 'Elemento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Eliminación lógica: marcar como inactivo
        item['is_active'] = False
        data_list[index] = item

        return Response({'message': 'Dato eliminado exitosamente.'}, status=status.HTTP_204_NO_CONTENT)
