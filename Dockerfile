# Etapa 1: Compilar frontend (Vite)
FROM node:18 AS frontend-builder

WORKDIR /frontend
COPY front/ /frontend/

RUN echo "Contenido de /frontend:" && ls -la /frontend && echo "Contenido de /frontend/src:" && ls -la /frontend/src

RUN npm install
RUN npm run build

# Etapa 2: Backend con FastAPI
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY . .

# Copiar frontend compilado al backend
RUN mkdir -p /app/templates/static
COPY --from=frontend-builder /frontend/dist/assets /app/templates/static
COPY --from=frontend-builder /frontend/dist/index.html /app/templates/static/index.html

EXPOSE 8000

# ✅ Usa el CMD como string en lugar de lista JSON (más compatible)
CMD uvicorn backend_api:app --host 0.0.0.0 --port 8000 --reload
