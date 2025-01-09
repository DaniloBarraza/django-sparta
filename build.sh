#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instalar las dependencias necesarias desde requirements.txt
pip install -r requirements.txt

# Navegar al directorio raíz del proyecto donde está manage.py
cd DjangoWebProject2

# Ejecutar collectstatic desde la ubicación de manage.py
python manage.py collectstatic --no-input

# Cambiar al directorio 'app' si es necesario (si tu proyecto tiene esa estructura)
cd app
