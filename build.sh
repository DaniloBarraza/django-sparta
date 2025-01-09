#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Navegar al directorio raíz del proyecto donde está manage.py
cd DjangoWebProject2

# Recolectar archivos estáticos, indicando el directorio correcto para los archivos estáticos
python manage.py collectstatic --no-input
