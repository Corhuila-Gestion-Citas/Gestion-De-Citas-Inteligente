# 🏥 Gestión de Citas Inteligente

Sistema distribuido para la gestión de citas médicas, desarrollado como proyecto académico para la asignatura **Sistemas Distribuidos** del programa de Ingeniería de Sistemas en la **Corporación Universitaria del Huila (CORHUILA)**.

El sistema implementa una arquitectura basada en microservicios con **API Gateway**, frontend en **Angular**, bases de datos independientes por servicio (**PostgreSQL** y **MongoDB**), autenticación asimétrica **JWT (RS256)**, contenedorización con **Docker** y separación de ambientes (`develop`, `qa` y `main`).

---

## 📋 Tabla de contenido

- [Repositorios del ecosistema](#-repositorios-del-ecosistema)
- [Información general](#-información-general)
- [Arquitectura del sistema](#-arquitectura-del-sistema)
- [Microservicios y endpoints](#-microservicios-y-endpoints)
- [Seguridad implementada](#-seguridad-implementada)
- [Puertos por ambiente](#-puertos-por-ambiente)
- [Despliegue y ejecución](#-despliegue-y-ejecución)
- [Auditoría de seguridad y pruebas](#-auditoría-de-seguridad-y-pruebas)
- [Verificación de persistencia y Liquibase](#-verificación-de-persistencia-y-liquibase)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Stack tecnológico](#-stack-tecnológico)
- [Equipo de desarrollo](#-equipo-de-desarrollo)

---

## 🔗 Repositorios del ecosistema

> **Este es el Repositorio Principal (Monorepo integrado).** Los siguientes enlaces corresponden a los repositorios modulares de referencia:

| Módulo | Enlace |
| :--- | :--- |
| **Portal Web (Frontend)** | [Ver repositorio](https://github.com/sparyock/Gestion-De-Citas-Inteligente-portal) |
| **Aplicación** | [Ver repositorio](https://github.com/sparyock/Gestion-De-Citas-Inteligente-app) |
| **API / Microservicios** | [Ver repositorio](https://github.com/sparyock/Gestion-De-Citas-Inteligente-api) |
| **Base de Datos** | [Ver repositorio](https://github.com/sparyock/Gestion-De-Citas-Inteligente-db) |
| **API Gateway** | [Ver repositorio](https://github.com/Corhuila-Gestion-Citas/Gestion-De-Citas-Inteligente-gateway/tree/main) |
| **Documentación y ADRs** | [Ver repositorio](https://github.com/Corhuila-Gestion-Citas/Gestion-De-Citas-Inteligente-docs) |

---

## 📌 Información general

| Atributo | Detalle |
| :--- | :--- |
| **Proyecto** | Gestión de Citas Inteligente |
| **Asignatura** | Sistemas Distribuidos |
| **Institución** | Corporación Universitaria del Huila — CORHUILA |
| **Periodo** | 2026-1 / 2026-2 |
| **Arquitectura** | Microservicios + API Gateway + SPA Angular |
| **Estado** | MVP funcional con controles de seguridad endurecidos (`RS256`, RBAC/BOLA, cuentas de BD separadas y CSP) |

---

## 🧱 Arquitectura del sistema

El cliente **Angular** nunca se comunica directamente con los microservicios ni con las bases de datos; todo el tráfico externo entra a través del **API Gateway**, que enruta las peticiones hacia la red privada de contenedores:

```text
Usuario (Navegador)
       │
       ▼
Frontend Angular (Nginx :4200 / :4210 / :4220)
       │
       ▼
API Gateway (Spring Cloud Gateway :8080 / :8180 / :8280)
       │
       ├──► users-service         ──► PostgreSQL (usersdb)
       ├──► turnos-service        ──► PostgreSQL (turnosdb)
       ├──► notifications-service ──► PostgreSQL (notificationsdb)
       └──► audit-service         ──► MongoDB    (auditdb)
```

---

## 🧩 Microservicios y endpoints

### 1. `api-gateway`
Punto único de entrada al sistema. Centraliza el enrutamiento, gestiona las políticas de **CORS** y oculta los puertos internos de los microservicios.

```text
/users/**          ──► users-service
/turnos/**         ──► turnos-service
/notifications/**  ──► notifications-service
/audit/**          ──► audit-service
```

### 2. `users-service`
Gestión de identidad, registro, autenticación y perfiles de usuario (**PostgreSQL**, tabla `users`).

* **Roles válidos:** `CLIENTE`, `ADMIN` (el registro público asigna `CLIENTE` por defecto).
* **Endpoints:**
  ```http
  POST   /users            # Registro público (rol CLIENTE)
  POST   /users/login      # Autenticación y emisión de JWT RS256
  GET    /users/health     # Estado del servicio
  GET    /users            # Listado global (solo ADMIN)
  GET    /users/{id}       # Consulta de perfil (propietario o ADMIN)
  PUT    /users/{id}       # Actualización de perfil (propietario o ADMIN)
  DELETE /users/{id}       # Eliminación de usuario (propietario o ADMIN)
  ```

### 3. `turnos-service`
Gestión del ciclo de vida de citas médicas, especialidades, doctores y disponibilidad (**PostgreSQL**, tabla `turnos`).

* **Estados válidos:** `PENDIENTE`, `CANCELADO`
* **Endpoints:**
  ```http
  GET    /turnos/especialidades          # Catálogo público de especialidades
  GET    /turnos/doctores                # Listado de doctores
  GET    /turnos/doctores/{especialidad} # Doctores por especialidad
  GET    /turnos/horarios/{doctor}       # Horarios disponibles
  POST   /turnos                         # Crear turno (idUsuario extraído del JWT)
  GET    /turnos                         # Listado global (solo ADMIN)
  GET    /turnos/{id}                    # Detalle por ID (propietario o ADMIN)
  GET    /turnos/usuario/{idUsuario}     # Turnos del usuario (propietario o ADMIN)
  PUT    /turnos/{idTurno}               # Reprogramar turno (propietario o ADMIN)
  PUT    /turnos/cancelar/{idTurno}      # Cancelar turno (propietario o ADMIN)
  DELETE /turnos/{idTurno}               # Eliminar turno (propietario o ADMIN)
  ```

### 4. `notifications-service`
Gestión de alertas y notificaciones generadas por eventos del sistema (**PostgreSQL**, tabla `notifications`).

* **Endpoints:**
  ```http
  GET    /notifications                    # Listado global (solo ADMIN)
  POST   /notifications                    # Crear notificación
  GET    /notifications/usuario/{idUsuario}# Notificaciones del usuario (propietario o ADMIN)
  PUT    /notifications/{id}/leida         # Marcar como leída (propietario o ADMIN)
  DELETE /notifications/{id}               # Eliminar notificación (propietario o ADMIN)
  ```

### 5. `audit-service`
Registro inmutable y trazabilidad de operaciones críticas (**MongoDB**, colección `audit_logs`).

* **Eventos registrados:** `REGISTRO`, `CREAR_TURNO`, `TURNO_REPROGRAMADO`, `CANCELAR_TURNO`, `NOTIFICACION_LEIDA`, `NOTIFICACION_ELIMINADA`, `SESION_CERRADA`.
* **Endpoints:**
  ```http
  GET    /audit/health                   # Estado del servicio
  GET    /audit                          # Historial completo (solo ADMIN)
  POST   /audit                          # Registro de evento de auditoría
  GET    /audit/usuario/{idUsuario}      # Auditoría por usuario (propietario o ADMIN)
  GET    /audit/accion/{accion}          # Filtrar por tipo de acción (solo ADMIN)
  GET    /audit/servicio/{servicioOrigen}# Filtrar por microservicio (solo ADMIN)
  GET    /audit/stats                    # Estadísticas agregadas (solo ADMIN)
  ```

---

## 🔐 Seguridad implementada

* **Firma asimétrica JWT (`RS256`):** `users-service` firma los tokens con una clave privada RSA de 3072 bits y una vigencia de **15 minutos**; los demás microservicios reciben únicamente la clave pública para verificar autenticidad.
* **Control de acceso y propiedad (RBAC / BOLA):** Todos los endpoints con datos validan la identidad extraída del token JWT, impidiendo que un usuario consulte, edite o cancele recursos de terceros.
* **Prevención de escalamiento de privilegios:** El registro público fuerza el rol `CLIENTE` e ignora cualquier intento de inyectar `rol: ADMIN` en el payload.
* **Cuentas de base de datos separadas:** cada servicio PostgreSQL usa su propia cuenta y contraseña (`users_app`, `turnos_app`, `notifications_app`) y MongoDB usa un usuario `readWrite` exclusivo para `auditdb` (`database/init-mongo-app-user.sh`). **Limitación conocida:** en PostgreSQL esas cuentas siguen siendo superusuario dentro de su contenedor: la imagen oficial no permite quitar ese atributo al usuario que inicializa el servidor y `database/init-app-user.sh` no lo consigue (se verificó con PostgreSQL 16). El riesgo se mitiga porque en `qa` y `main` las bases de datos no se publican fuera de la red de Docker.
* **Aislamiento de red:** En los ambientes `qa` y `main` únicamente se exponen el **Frontend** y el **API Gateway**. En `develop`, los puertos internos se enlazan exclusivamente a `127.0.0.1`.
* **Frontend endurecido (Nginx + Angular):** Token JWT en `sessionStorage` (se borra al cerrar la pestaña; los datos de perfil no sensibles —id, nombre, correo y rol— quedan en `localStorage`), interceptor HTTP para cabeceras `Authorization: Bearer` y políticas HTTP estrictas (`Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` y `Permissions-Policy`).

### Preparar secretos locales (`.env`)

Antes de levantar cualquier ambiente por primera vez hay que crear el archivo `.env` en la raíz del proyecto. Contiene el par de claves RSA (JWT RS256) y contraseñas aleatorias para las bases de datos. **No se versiona** (está en `.gitignore`) y el script no sobrescribe un `.env` existente.

**Opción A: solo Docker (no hace falta instalar Node.js)**

```powershell
# Windows PowerShell
docker run --rm -v "${PWD}:/work" -w /work node:20-alpine node scripts/generate-env.js
```

```bash
# Linux / macOS / Git Bash / GitHub Codespaces
docker run --rm -v "$(pwd):/work" -w /work node:20-alpine node scripts/generate-env.js
```

**Opción B: con Node.js instalado**

```bash
node scripts/generate-env.js
```

Si el archivo ya existe y quieres regenerarlo, añade `--force` y después borra los volúmenes antiguos con `docker compose -f <archivo> down -v`.

> **Nota sobre volúmenes existentes:** Los scripts de inicialización en `database/` se ejecutan automáticamente cuando Docker crea volúmenes nuevos. Si reutilizas volúmenes creados antes de activar la autenticación, debes respaldarlos y migrar los roles manualmente.

---

## 🌐 Puertos por ambiente

| Componente | `develop` | `qa` | `main` |
| :--- | :---: | :---: | :---: |
| **Frontend Angular (Nginx)** | `4200` | `4210` | `4220` |
| **API Gateway** | `8080` | `8180` | `8280` |
| `users-service` | `127.0.0.1:8081` | No publicado | No publicado |
| `turnos-service` | `127.0.0.1:8082` | No publicado | No publicado |
| `notifications-service` | `127.0.0.1:8083` | No publicado | No publicado |
| `audit-service` | `127.0.0.1:8084` | No publicado | No publicado |
| `users-db` (PostgreSQL) | `127.0.0.1:5433` | No publicado | No publicado |
| `turnos-db` (PostgreSQL) | `127.0.0.1:5434` | No publicado | No publicado |
| `notifications-db` (PostgreSQL) | `127.0.0.1:5435` | No publicado | No publicado |
| `audit-db` (MongoDB) | `127.0.0.1:27017` | No publicado | No publicado |

---

## 🚀 Despliegue y ejecución

> **Recomendación:** Levanta un solo ambiente a la vez para optimizar el consumo de CPU y memoria RAM.

### Ambiente `develop` (Desarrollo local)
```bash
# Levantar servicios
docker compose -f docker-compose.develop.yml up -d --build

# Apagar servicios
docker compose -f docker-compose.develop.yml down
```
* **Frontend:** `http://localhost:4200`
* **API Gateway:** `http://localhost:8080/users/health`

### Ambiente `qa` (Pruebas)
```bash
# Levantar servicios
docker compose -f docker-compose.qa.yml up -d --build

# Apagar servicios
docker compose -f docker-compose.qa.yml down
```
* **Frontend:** `http://localhost:4210`
* **API Gateway:** `http://localhost:8180/users/health`

### Ambiente `main` (Demostración / Producción)
```bash
# Levantar servicios
docker compose -f docker-compose.main.yml up -d --build

# Apagar servicios
docker compose -f docker-compose.main.yml down
```
* **Frontend:** `http://localhost:4220`
* **API Gateway:** `http://localhost:8280/users/health`

---

## 🛡️ Auditoría de seguridad y pruebas

### 1. Batería automatizada de seguridad (`security_tests.py`)
El repositorio incluye un script en Python para validar controles de JWT, IDOR/BOLA, aislamiento de puertos, cabeceras HTTP y resistencia a inyección:

```bash
# Contra ambiente develop (puerto 8080)
python3 security_tests.py --base http://localhost:8080 --out resultados_develop.json

# Contra ambiente main (puerto 8280)
python3 security_tests.py --base http://localhost:8280 --out resultados_main.json
```

### 2. Flujo funcional de validación E2E
1. Registrar un usuario nuevo desde el portal web y verificar inicio de sesión.
2. Solicitar un turno médico seleccionando especialidad, doctor y horario.
3. Consultar, reprogramar y cancelar el turno desde **Mis Turnos**.
4. Verificar las notificaciones generadas automáticamente, marcarlas como leídas y eliminarlas.
5. Revisar la trazabilidad de cada evento en el módulo de **Historial / Auditoría**.

---

## ✅ Verificación de persistencia y Liquibase

### Consultas rápidas a las bases de datos (`develop`)

```bash
# PostgreSQL - Usuarios
docker exec -it users-db-develop psql -U users_app -d usersdb_develop -c "SELECT id_usuario, nombre, correo, rol FROM users ORDER BY id_usuario DESC;"

# PostgreSQL - Turnos
docker exec -it turnos-db-develop psql -U turnos_app -d turnosdb_develop -c "SELECT id_turno, id_usuario, especialidad, doctor, fecha_hora, estado FROM turnos ORDER BY id_turno DESC;"

# PostgreSQL - Notificaciones
docker exec -it notifications-db-develop psql -U notifications_app -d notificationsdb_develop -c "SELECT id, id_usuario, titulo, tipo, leida, fecha_creacion FROM notifications ORDER BY id DESC;"

# MongoDB - Últimos 10 eventos de auditoría
docker exec -it audit-db-develop mongosh --username audit_admin --authenticationDatabase admin --eval "db.getSiblingDB('auditdb_develop').audit_logs.find().sort({fechaCreacion:-1}).limit(10).pretty()"
```

### Verificación de migraciones Liquibase
Los microservicios `users-service`, `turnos-service` y `notifications-service` gestionan su esquema mediante **Liquibase**:

```bash
# Listar tablas creadas (esperado: databasechangelog, databasechangeloglock y tabla de dominio)
docker exec -it users-db-develop psql -U users_app -d usersdb_develop -c "\dt"

# Verificar estado de changesets (esperado: EXECUTED)
docker exec -it users-db-develop psql -U users_app -d usersdb_develop -c "SELECT id, author, filename, dateexecuted, exectype FROM databasechangelog;"

# Verificar ausencia de bloqueos (esperado: locked = f)
docker exec -it users-db-develop psql -U users_app -d usersdb_develop -c "SELECT * FROM databasechangeloglock;"
```

---

## 📁 Estructura del proyecto

```text
Gestion-De-Citas-Inteligente/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Integración continua (Maven, Angular build, npm audit, Compose)
├── backend/
│   ├── api-gateway/               # Spring Cloud Gateway + configuración CORS
│   ├── users-service/             # Autenticación RS256, usuarios y roles
│   ├── turnos-service/            # Gestión de citas médicas y catálogos
│   ├── notifications-service/     # Alertas y notificaciones por usuario
│   └── audit-service/             # Auditoría en MongoDB
├── database/
│   ├── init-app-user.sh           # Creación de roles PostgreSQL de mínimo privilegio
│   └── init-mongo-app-user.sh     # Creación de usuario readWrite en MongoDB
├── doc/
│   ├── ADR/                       # Registros de decisiones de arquitectura (ADR-001 a ADR-020)
│   ├── diagrams/                  # Diagramas UML, arquitectura y modelo de datos
│   ├── historias de usuario/      # Documentación funcional
│   ├── mockups/                   # Prototipos de interfaz
│   └── Presentacion/              # Material de sustentación
├── frontend/
│   └── gestion-citas-frontend/    # Aplicación SPA en Angular + Nginx endurecido
├── scripts/
│   └── generate-env.js            # Genera el .env (claves RSA y contraseñas)
├── docker-compose.develop.yml
├── docker-compose.qa.yml
├── docker-compose.main.yml
├── security_tests.py              # Suite automatizada de auditoría de seguridad
├── .gitattributes
└── README.md
```

---

## 🛠️ Stack tecnológico

* **Backend:** Java 17, Spring Boot 3, Spring Cloud Gateway, Spring Security (JWT RS256), Spring Data JPA / MongoDB, Liquibase, Maven.
* **Frontend:** Angular, TypeScript, CSS, Nginx Unprivileged (`1.27-alpine`).
* **Bases de datos:** PostgreSQL 16, MongoDB 7.
* **DevOps y Calidad:** Docker, Docker Compose, GitHub Actions (CI), Python 3 (pruebas de seguridad).

---

## 👥 Equipo de desarrollo

Proyecto desarrollado por estudiantes de Ingeniería de Sistemas — **CORHUILA**:

* **Yeison Andrés Scarpeta Díaz**
* **Nicolás Gabriel Álvarez Aguirre**



