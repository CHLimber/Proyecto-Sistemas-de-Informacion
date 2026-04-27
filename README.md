# ServiControl

Plataforma web para gestión de empresas de seguridad electrónica.

**Stack:** Flask + SQLAlchemy (backend) · React + Vite (frontend) · MySQL

---

## Requisitos previos

- Python 3.10+
- Node.js 18+
- MySQL 8.0+ con la base de datos creada (ver `scrip creacion BD.txt`)

---

## Instalación

### 1. Base de datos

Ejecutar en MySQL el script `backend/scrip creacion BD.txt` para crear la base de datos y las tablas.

Opcionalmente ejecutar `backend/scrip poblacion.txt` para cargar datos de prueba.

### 2. Backend

```bash
cd backend

# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac
# Editar .env con tus credenciales de MySQL

# Iniciar servidor (puerto 5000)
python run.py
```

### 3. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar (opcional, por defecto apunta a localhost:5000)
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac

# Iniciar servidor de desarrollo (puerto 5173)
npm run dev
```

### 4. Acceder

Abrir [http://localhost:5173](http://localhost:5173) en el navegador.

Credenciales por defecto (si se ejecutó el script de población):
- Usuario: `admin`
- Contraseña: ver `scrip poblacion.txt`

---

## Estructura del proyecto

```
Proyecto/
├── backend/
│   ├── app/
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── routes/       # Blueprints Flask (API REST)
│   │   └── ...
│   ├── migrations/       # Migraciones Alembic
│   ├── scrip creacion BD.txt
│   ├── scrip poblacion.txt
│   ├── seed_railway.py   # Seed automático en Railway
│   ├── Procfile
│   ├── railway.json
│   ├── requirements.txt
│   └── run.py
└── frontend/
    ├── src/
    │   ├── api/          # Clientes Axios por módulo
    │   ├── pages/        # Páginas React
    │   └── ...
    ├── railway.json
    └── package.json
```

---

## Despliegue en Railway

### Backend (servicio Python)

1. Crear servicio desde el repo, **Root Directory: `backend`**.
2. Conectar plugin **MySQL** → autoinyecta `MYSQL_URL`.
3. Definir variables de entorno:
   - `SECRET_KEY` (valor aleatorio largo)
   - `JWT_SECRET_KEY` (valor aleatorio largo)
   - `FLASK_ENV=production`
   - `ALLOWED_ORIGINS=https://<frontend-domain>.up.railway.app`
   - `MAIL_USERNAME`, `MAIL_PASSWORD` (opcional, para envío de correos)
4. Build y start los maneja `railway.json` automáticamente:
   - El `buildCommand` corre `seed_railway.py` (idempotente, solo puebla si la BD está vacía).
   - El `startCommand` levanta gunicorn en `$PORT`.

### Frontend (servicio Node)

1. Crear servicio desde el mismo repo, **Root Directory: `frontend`**.
2. Definir variable:
   - `VITE_API_URL=https://<backend-domain>.up.railway.app/api`
   - **Importante:** debe estar definida antes del build, ya que Vite la inlinea.
3. Build y start los maneja `railway.json`.

### Credenciales de prueba (después del seed)

| Usuario           | Contraseña     | Rol               |
|-------------------|----------------|-------------------|
| admin.mendoza     | Admin123!      | Administrador     |
| marco.ibanez      | Tecnico123!    | Técnico Superior  |
| ana.quispe        | Atencion123!   | Atención Cliente  |
| roberto.flores    | Campo123!      | Técnico de Campo  |

---

## Módulos implementados

- Autenticación (JWT)
- Productos
- Entidades (clientes y proveedores)
- Cotizaciones
- Proyectos
- Órdenes de trabajo
- Mantenimiento
- Finanzas (pagos, gastos, cuentas por cobrar)
- Usuarios y roles
