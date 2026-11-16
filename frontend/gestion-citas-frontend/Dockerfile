# Etapa 1: compilar Angular
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# URL del API Gateway según el ambiente
# Por defecto usa develop
ARG API_GATEWAY_URL=http://localhost:8080

# Reemplaza la URL del gateway antes de compilar Angular
RUN sed -i "s|https://api-gateway-main.onrender.com|${API_GATEWAY_URL}|g" src/app/config/api.config.ts

RUN npm run build

# Etapa 2: servir archivos estáticos con nginx
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build --chown=nginx:nginx /app/dist/gestion-citas-frontend/browser /usr/share/nginx/html

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]