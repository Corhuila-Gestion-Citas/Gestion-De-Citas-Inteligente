## Este es el Repositorio Principal:
### Enlace Portal web: [ir](https://github.com/sparyock/Gestion-De-Citas-Inteligente-portal)
### Enlace app: [ir](https://github.com/sparyock/Gestion-De-Citas-Inteligente-app)
### Enlace api: [ir](https://github.com/sparyock/Gestion-De-Citas-Inteligente-api)
### Enlace db: [ir](https://github.com/sparyock/Gestion-De-Citas-Inteligente-db)
### Enlace Gateway: [ir](https://github.com/Corhuila-Gestion-Citas/Gestion-De-Citas-Inteligente-gateway/tree/main)
### Enlace docs: [ir](https://github.com/Corhuila-Gestion-Citas/Gestion-De-Citas-Inteligente-docs)

# 🏥 Gestión de Citas Inteligente

Sistema distribuido para la gestión de citas médicas, desarrollado como proyecto académico para la asignatura **Sistemas Distribuidos** de Ingeniería de Sistemas. El proyecto implementa una arquitectura basada en microservicios, API Gateway, frontend Angular, bases de datos independientes por servicio, contenedorización con Docker y separación de ambientes `develop`, `qa` y `main`.

---

## 📌 Información general

**Nombre del proyecto:** Gestión de Citas Inteligente  
**Asignatura:** Sistemas Distribuidos  
**Institución:** Corporación Universitaria del Huila - CORHUILA  
**Periodo:** 2026-1  
**Arquitectura:** Microservicios + API Gateway + Frontend Angular  
**Estado actual:** Proyecto académico; aplicar y validar la configuración de seguridad antes de exponerlo fuera del entorno local

---

## 🎯 Objetivo del proyecto

Desarrollar un sistema distribuido que permita a los usuarios registrarse, iniciar sesión, solicitar turnos médicos, reprogramar citas, cancelar turnos, recibir notificaciones y consultar el historial de auditoría de sus acciones.

El sistema busca demostrar conceptos clave de Sistemas Distribuidos, como:

- Separación por microservicios.
- Comunicación mediante API Gateway.
- Persistencia distribuida por servicio.
- Uso de bases de datos relacionales y NoSQL.
- Contenedorización con Docker.
- Ambientes separados de desarrollo, pruebas y producción.
- Integración frontend-backend.
- Auditoría de eventos del sistema.

---

## 🧱 Arquitectura general

El proyecto está organizado como un sistema de microservicios. El frontend Angular no se comunica directamente con cada microservicio, sino que consume todos los servicios a través del **API Gateway**.

```text
Usuario
  │
  ▼
Frontend Angular
  │
  ▼
API Gateway
  │
  ├── users-service          → PostgreSQL
  ├── turnos-service         → PostgreSQL
  ├── notifications-service  → PostgreSQL
  └── audit-service          → MongoDB
```

---

## 🧩 Microservicios del sistema

### 1. API Gateway

Servicio encargado de recibir las peticiones del frontend y redirigirlas hacia el microservicio correspondiente.

**Responsabilidades:**

- Centralizar el acceso a los microservicios.
- Configurar rutas hacia cada servicio.
- Manejar CORS para permitir la conexión con Angular.
- Evitar que el frontend consuma directamente los puertos internos de los microservicios.

**Rutas principales:**

```text
/users/**          → users-service
/turnos/**         → turnos-service
/notifications/**  → notifications-service
/audit/**          → audit-service
```

---

### 2. users-service

Microservicio encargado de la gestión de usuarios.

**Base de datos:** PostgreSQL  
**Tabla principal:** `users`

**Funcionalidades:**

- Registrar usuarios.
- Iniciar sesión.
- Consultar usuarios.
- Actualizar usuarios.
- Eliminar usuarios.
- Endpoint de salud.

**Endpoints principales:**

```http
GET    /users
POST   /users
GET    /users/{id}
PUT    /users/{id}
DELETE /users/{id}
POST   /users/login
GET    /users/health
```

**Roles válidos:**

```text
CLIENTE
ADMIN
```

---

### 3. turnos-service

Microservicio encargado de la gestión de turnos médicos.

**Base de datos:** PostgreSQL  
**Tabla principal:** `turnos`

**Funcionalidades:**

- Crear turnos.
- Consultar todos los turnos.
- Consultar turnos por usuario.
- Reprogramar turnos.
- Cancelar turnos.
- Consultar especialidades.
- Consultar doctores.
- Consultar horarios disponibles.

**Endpoints principales:**

```http
GET    /turnos
POST   /turnos
GET    /turnos/{id}
GET    /turnos/usuario/{idUsuario}
PUT    /turnos/{idTurno}
PUT    /turnos/cancelar/{idTurno}
DELETE /turnos/{idTurno}
GET    /turnos/especialidades
GET    /turnos/doctores
GET    /turnos/doctores/{especialidad}
GET    /turnos/horarios/{doctor}
```

**Estados del turno:**

```text
PENDIENTE
CANCELADO
```

---

### 4. notifications-service

Microservicio encargado de gestionar las notificaciones de los usuarios.

**Base de datos:** PostgreSQL  
**Tabla principal:** `notifications`

**Funcionalidades:**

- Crear notificaciones.
- Consultar notificaciones.
- Consultar notificaciones por usuario.
- Marcar notificaciones como leídas.
- Eliminar notificaciones.

**Endpoints principales:**

```http
GET    /notifications
POST   /notifications
GET    /notifications/usuario/{idUsuario}
PUT    /notifications/{id}/leida
DELETE /notifications/{id}
```

---

### 5. audit-service

Microservicio encargado de registrar eventos importantes del sistema.

**Base de datos:** MongoDB  
**Colección principal:** `audit_logs`

**Funcionalidades:**

- Registrar auditoría de acciones del usuario.
- Consultar auditorías.
- Consultar auditoría por usuario.
- Consultar auditoría por acción.
- Consultar auditoría por servicio.
- Consultar estadísticas.
- Eliminar registros de auditoría.

**Endpoints principales:**

```http
GET    /audit/health
GET    /audit
POST   /audit
GET    /audit/usuario/{idUsuario}
GET    /audit/accion/{accion}
GET    /audit/servicio/{servicioOrigen}
GET    /audit/stats
DELETE /audit/{id}
```

**Acciones de auditoría usadas:**

```text
REGISTRO
CREAR_TURNO
TURNO_REPROGRAMADO
CANCELAR_TURNO
NOTIFICACION_LEIDA
NOTIFICACION_ELIMINADA
SESION_CERRADA
```

---

## 🅰️ Frontend Angular

El frontend se encuentra en:

```text
frontend/gestion-citas-frontend
```

El frontend consume los microservicios mediante el API Gateway. No debe consumir directamente los puertos internos de los servicios.

**Funcionalidades implementadas:**

- Registro de usuarios.
- Inicio de sesión.
- Panel de inicio.
- Solicitud de turnos.
- Consulta de turnos del usuario.
- Reprogramación de turnos.
- Cancelación de turnos.
- Consulta de notificaciones.
- Marcar notificaciones como leídas.
- Eliminación de notificaciones.
- Historial de auditoría.
- Perfil del usuario.
- Cierre de sesión.

---

## 🐳 Docker y ambientes

El proyecto cuenta con tres ambientes separados:

```text
develop → Desarrollo local
qa      → Pruebas
main    → Producción local / demostración
```

Cada ambiente cuenta con sus propios contenedores, puertos, redes y volúmenes.

## 🔐 Seguridad

- Registro e inicio de sesión son públicos; el resto de las operaciones requiere JWT firmado con **RS256**, con una vigencia predeterminada de 15 minutos.
- Las operaciones sobre usuarios, turnos, notificaciones y auditorías se limitan al propietario del recurso; las consultas globales y acciones administrativas requieren `ADMIN`.
- El registro público siempre crea usuarios `CLIENTE`; no se acepta que el cliente se asigne el rol `ADMIN`.
- `users-service` firma tokens con la clave privada. Los demás microservicios solo reciben la clave pública para validarlos.
- Las contraseñas se almacenan con BCrypt. No reutilizar claves o contraseñas entre ambientes, ni guardar `.env`, claves privadas o respaldos en Git.
- El frontend conserva el token en `sessionStorage` y lo envía como `Authorization: Bearer`. Esto reduce su persistencia frente a `localStorage`, pero **no protege contra XSS**; mantener dependencias actualizadas y no insertar HTML no confiable.
- En QA y main solo se publican frontend y API Gateway. En develop, las bases y microservicios publicados se enlazan únicamente a `127.0.0.1`.
- Los servicios de aplicación usan cuentas PostgreSQL separadas; MongoDB usa una cuenta `readWrite` limitada a la base de auditoría, distinta de su administrador. Los volúmenes MongoDB creados antes de activar la autenticación no se migran automáticamente.

### Preparar secretos locales

Requiere Node.js. Ejecutar en PowerShell desde la raíz; `.env` está ignorado por Git. Este comando genera claves RSA de 3072 bits en los formatos que esperan los servicios y contraseñas aleatorias, sin imprimir sus valores:

```powershell
node -e "const fs=require('fs');const crypto=require('crypto');const keys=crypto.generateKeyPairSync('rsa',{modulusLength:3072,publicKeyEncoding:{type:'spki',format:'der'},privateKeyEncoding:{type:'pkcs8',format:'der'}});const secret=()=>crypto.randomBytes(32).toString('hex');const values={JWT_PRIVATE_KEY_BASE64:keys.privateKey.toString('base64'),JWT_PUBLIC_KEY_BASE64:keys.publicKey.toString('base64'),USERS_DB_PASSWORD:secret(),TURNOS_DB_PASSWORD:secret(),NOTIFICATIONS_DB_PASSWORD:secret(),MONGODB_ROOT_PASSWORD:secret(),MONGODB_APP_PASSWORD:secret()};fs.writeFileSync('.env',Object.entries(values).map(([key,value])=>key+'='+value).join('\n'),{encoding:'utf8'});console.log('Archivo .env creado.')"
```

La clave privada solo debe estar disponible para `users-service`; ambas claves deben corresponder. Para producción real, inyectar estos valores desde un gestor de secretos, usar HTTPS y no guardar claves privadas en archivos de despliegue. No borrar o reemplazar volúmenes para activar MongoDB autenticado sin primero hacer backup y planear la migración.

El script `database/init-app-user.sh` limita privilegios de las cuentas PostgreSQL en volúmenes nuevos. En volúmenes existentes, respaldar los datos y aplicar manualmente `ALTER ROLE <usuario> WITH NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;` a cada cuenta (`users_app`, `turnos_app`, `notifications_app`). MongoDB con volúmenes antiguos también requiere una migración autenticada respaldada; las variables `MONGO_INITDB_*` no crean usuarios en un volumen previamente inicializado.

---

## 🌐 Puertos por ambiente

### Ambiente develop

| Componente | Puerto |
|---|---:|
| Frontend Angular | `4200` |
| API Gateway | `8080` |
| users-service (solo localhost) | `8081` |
| turnos-service (solo localhost) | `8082` |
| notifications-service (solo localhost) | `8083` |
| audit-service (solo localhost) | `8084` |
| users-db PostgreSQL (solo localhost) | `5433` |
| turnos-db PostgreSQL (solo localhost) | `5434` |
| notifications-db PostgreSQL (solo localhost) | `5435` |
| audit-db MongoDB (solo localhost) | `27017` |

### Ambiente QA

| Componente | Puerto |
|---|---:|
| Frontend Angular | `4210` |
| API Gateway | `8180` |
| Microservicios y bases de datos | No publicados |

### Ambiente main

| Componente | Puerto |
|---|---:|
| Frontend Angular | `4220` |
| API Gateway | `8280` |
| Microservicios y bases de datos | No publicados |

---

## 🚀 Ejecución del proyecto

> **Importante:** No se recomienda levantar los tres ambientes al mismo tiempo en equipos con pocos recursos. Probar uno por uno.

---

## Ejecutar ambiente develop

Antes de iniciar cualquier ambiente, crear el archivo `.env` siguiendo **Preparar secretos locales**.

```powershell
docker compose -f .\docker-compose.develop.yml up -d --build
```

Abrir frontend:

```text
http://localhost:4200
```

Probar Gateway:

```text
http://localhost:8080/users/health
http://localhost:8080/turnos/especialidades
http://localhost:8080/audit/health
```

Las rutas de usuarios, turnos, notificaciones y auditoría que contienen datos requieren el JWT recibido al iniciar sesión.

Apagar ambiente develop:

```powershell
docker compose -f .\docker-compose.develop.yml down
```

---

## Ejecutar ambiente QA

```powershell
docker compose -f .\docker-compose.qa.yml up -d --build
```

Abrir frontend:

```text
http://localhost:4210
```

Probar Gateway:

```text
http://localhost:8180/users/health
http://localhost:8180/turnos/especialidades
http://localhost:8180/audit/health
```

Apagar ambiente QA:

```powershell
docker compose -f .\docker-compose.qa.yml down
```

---

## Ejecutar ambiente main

```powershell
docker compose -f .\docker-compose.main.yml up -d --build
```

Abrir frontend:

```text
http://localhost:4220
```

Probar Gateway:

```text
http://localhost:8280/users/health
http://localhost:8280/turnos/especialidades
http://localhost:8280/audit/health
```

Apagar ambiente main:

```powershell
docker compose -f .\docker-compose.main.yml down
```

---

## 🧪 Pruebas funcionales recomendadas

Para validar el sistema completo desde el frontend:

1. Registrar un usuario.
2. Iniciar sesión.
3. Solicitar un turno.
4. Consultar el turno en “Mis Turnos”.
5. Reprogramar el turno.
6. Cancelar el turno.
7. Ver las notificaciones generadas.
8. Marcar una notificación como leída.
9. Consultar el historial de auditoría.
10. Revisar el perfil del usuario.
11. Cerrar sesión.

---

## ✅ Verificación de persistencia

### Usuarios

```powershell
docker exec -it users-db-develop psql -U users_app -d usersdb_develop -c "SELECT id_usuario, nombre, correo, rol FROM users ORDER BY id_usuario DESC;"
```

### Turnos

```powershell
docker exec -it turnos-db-develop psql -U turnos_app -d turnosdb_develop -c "SELECT id_turno, id_usuario, especialidad, doctor, fecha_hora, estado FROM turnos ORDER BY id_turno DESC;"
```

### Notificaciones

```powershell
docker exec -it notifications-db-develop psql -U notifications_app -d notificationsdb_develop -c "SELECT id, id_usuario, titulo, tipo, leida, fecha_creacion FROM notifications ORDER BY id DESC;"
```

### Auditoría en MongoDB

```powershell
docker exec -it audit-db-develop mongosh --username audit_admin --authenticationDatabase admin
```

Dentro de MongoDB:

```javascript
use auditdb_develop
show collections
db.audit_logs.find().sort({fechaCreacion:-1}).limit(10).pretty()
```

---

## 🧬 Verificación de Liquibase

Liquibase se usa para gestionar las migraciones en los microservicios que utilizan PostgreSQL.

Microservicios con Liquibase:

```text
users-service
turnos-service
notifications-service
```

### Verificar tablas creadas

```powershell
docker exec -it users-db-develop psql -U users_app -d usersdb_develop -c "\dt"
docker exec -it turnos-db-develop psql -U turnos_app -d turnosdb_develop -c "\dt"
docker exec -it notifications-db-develop psql -U notifications_app -d notificationsdb_develop -c "\dt"
```

Resultado esperado:

```text
databasechangelog
databasechangeloglock
users / turnos / notifications
```

### Verificar changesets ejecutados

```powershell
docker exec -it users-db-develop psql -U users_app -d usersdb_develop -c "SELECT id, author, filename, dateexecuted, exectype FROM databasechangelog;"
docker exec -it turnos-db-develop psql -U turnos_app -d turnosdb_develop -c "SELECT id, author, filename, dateexecuted, exectype FROM databasechangelog;"
docker exec -it notifications-db-develop psql -U notifications_app -d notificationsdb_develop -c "SELECT id, author, filename, dateexecuted, exectype FROM databasechangelog;"
```

Resultado esperado:

```text
EXECUTED
```

### Verificar que Liquibase no esté bloqueado

```powershell
docker exec -it users-db-develop psql -U users_app -d usersdb_develop -c "SELECT * FROM databasechangeloglock;"
docker exec -it turnos-db-develop psql -U turnos_app -d turnosdb_develop -c "SELECT * FROM databasechangeloglock;"
docker exec -it notifications-db-develop psql -U notifications_app -d notificationsdb_develop -c "SELECT * FROM databasechangeloglock;"
```

Resultado esperado:

```text
locked = f
```

---

## 🔎 Comandos útiles de diagnóstico

### Ver contenedores activos

```powershell
docker ps
```

### Ver todos los contenedores

```powershell
docker ps -a
```

### Ver logs del API Gateway

```powershell
docker logs api-gateway-develop
```

### Ver logs del frontend

```powershell
docker logs frontend-develop
```

### Ver logs de servicios

```powershell
docker logs users-service-develop
docker logs turnos-service-develop
docker logs notifications-service-develop
docker logs audit-service-develop
```

Para QA o main, cambiar `develop` por `qa` o `main`.

---

## 🔀 Flujo de trabajo con Git

El repositorio maneja tres ramas principales:

```text
develop → desarrollo activo
qa      → pruebas
main    → versión estable / producción
```

Flujo sugerido:

```text
feature/* → develop → qa → main
```

Para actualizar la rama develop:

```powershell
git checkout develop
git pull origin develop
```

---

## 📁 Estructura principal del proyecto

```text
Gestion-De-Citas-Inteligente/
│
├── backend/
│   ├── api-gateway/
│   ├── users-service/
│   ├── turnos-service/
│   ├── notifications-service/
│   └── audit-service/
│
├── frontend/
│   └── gestion-citas-frontend/
│
├── docker-compose.develop.yml
├── docker-compose.qa.yml
├── docker-compose.main.yml
├── README.md
└── READMERULES.md
```

---

## 🛠️ Tecnologías utilizadas

### Backend

- Java 17
- Spring Boot
- Spring Cloud Gateway
- Spring Data JPA
- Maven
- Liquibase

### Frontend

- Angular
- TypeScript
- HTML
- CSS
- Nginx para servir el build en Docker

### Bases de datos

- PostgreSQL
- MongoDB

### Infraestructura

- Docker
- Docker Compose
- Git
- GitHub

---

## 📌 Estado actual del sistema

Actualmente el sistema permite:

```text
✅ Registro de usuarios
✅ Inicio de sesión
✅ Solicitud de turnos
✅ Reprogramación de turnos
✅ Cancelación de turnos
✅ Notificaciones por acción
✅ Historial de auditoría
✅ Persistencia en PostgreSQL
✅ Auditoría en MongoDB
✅ Migraciones con Liquibase
✅ Frontend dockerizado
✅ Ambientes develop, qa y main
```

---

## 👥 Equipo de trabajo

Proyecto académico desarrollado por el equipo de Gestión de Citas Inteligente para la asignatura Sistemas Distribuidos, el cuál está conformado por:
Yeison Andres Scarpeta Diaz, Nicolás Gabriel Álvarez Aguirre, Dayana Sofía Mendes Perafán y Andrea Catalina Cortés Ramires.

---

