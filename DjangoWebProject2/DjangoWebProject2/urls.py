"""
Definition of urls for DjangoWebProject2.
"""

from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.paginaIndex, name='index'),  # Página principal
    path('home/', views.registro_cliente, name='home'),  # Ruta para registro de clientes (principal)
    path('registro_cliente/', views.registro_cliente, name="registro_cliente"),  # Registro de cliente
    path('listar_clientes/', views.listar_clientes, name='listar_clientes'),  # Listado de clientes
    path('get_cliente/<str:rutCliente>/', views.get_cliente, name='get_cliente'),  # Obtener un cliente por RUT
    path('get_comunas/', views.get_comunas, name='get_comunas'),  # Obtener comunas de una región
    path('eliminar_cliente/', views.eliminar_cliente, name='eliminar_cliente'),  # Eliminar cliente
]
