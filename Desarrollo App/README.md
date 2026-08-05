# Entre Brasas — Cómo correr el sistema

## Requisitos previos
- Python 3.10+

## 1. Ir a la carpeta del proyecto
```bash
cd "ruta\Desarrollo App"
```

## 2. Crear entorno virtual
```bash
python -m venv venv
```

## 3. Activar entorno virtual
```bash
venv\Scripts\activate
```

## 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 5. Aplicar migraciones
```bash
python manage.py migrate
```

## 6. Cargar datos iniciales
```bash
python manage.py seed_data
```

## 7. Levantar servidor
```bash
python manage.py runserver
```

## 8. Abrir en el navegador
Abrir http://localhost:8000/

---

## Usar PostgreSQL (opcional)

Si preferís PostgreSQL en vez de SQLite, seteá la variable de entorno `DATABASE_URL` antes de correr el servidor:

```bash
set DATABASE_URL=postgres://postgres:tu_password@localhost:5432/entre_brasas
```

Reemplazá `tu_password` con la contraseña de tu PostgreSQL. La base de datos `entre_brasas` debe existir.
