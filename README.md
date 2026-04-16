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

Ejecutar en MySQL el script `scrip creacion BD.txt` para crear la base de datos y las tablas.

Opcionalmente ejecutar `scrip poblacion.txt` para cargar datos de prueba.

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
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/          # Clientes Axios por módulo
│   │   ├── pages/        # Páginas React
│   │   └── ...
│   └── package.json
├── scrip creacion BD.txt
└── scrip poblacion.txt
```

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
