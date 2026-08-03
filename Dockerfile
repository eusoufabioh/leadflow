# Stage 1: Build frontend
FROM node:18-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Backend + Frontend
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY ia/ ./ia/
COPY automacoes/ ./automacoes/

# Copy frontend build
COPY --from=frontend-build /frontend/out ./static

EXPOSE ${PORT:-8000}

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
