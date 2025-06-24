set -o errexit  # para que el script falle si algún comando falla
set -o pipefail
set -o nounset

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Aplicando migraciones..."
python manage.py migrate --no-input

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "Build y migraciones completadas correctamente."