# Crear entorno virtual

python -m venv venv 

# Activar entorno virtual

venv\Scripts\activate

# Instalar dependencias dentro del entorno virtual

pip install -r requirements.txt

# Correr FastApi

uvicorn backend_api:app --reload

# Ejecutar frontend

cd front
npm install
npm run dev