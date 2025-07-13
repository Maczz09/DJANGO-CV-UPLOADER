#!/bin/bash

# Script de despliegue para Django CV Uploader
set -e

echo "🚀 Iniciando despliegue de Django CV Uploader..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    error "Python 3 no está instalado"
    exit 1
fi

# Crear entorno virtual
log "Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
log "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurar base de datos
log "Configurando base de datos..."
python manage.py makemigrations
python manage.py migrate

# Crear superusuario (opcional)
log "¿Desea crear un superusuario? (y/n)"
read -r create_superuser
if [[ $create_superuser == "y" || $create_superuser == "Y" ]]; then
    python manage.py createsuperuser
fi

# Recopilar archivos estáticos
log "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear directorios necesarios
log "Creando directorios..."
mkdir -p media/cvs
mkdir -p logs

# Configurar permisos
chmod 755 media/cvs
chmod 755 logs

log "✅ Despliegue completado exitosamente!"
log "Para ejecutar el servidor de desarrollo:"
log "  source venv/bin/activate"
log "  python manage.py runserver"
log ""
log "Para producción con Gunicorn:"
log "  gunicorn --bind 0.0.0.0:8000 cv_uploader.wsgi:application"
