# Entre Brasas — Cómo correr el sistema

## Comandos para instalar y correr

### 1. Ir a la carpeta del proyecto
```bash
cd "ruta\Desarrollo App"
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual
```bash
venv\Scripts\activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Crear la base de datos
```bash
$env:PGPASSWORD="entrebrasasjujuy87"; & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE entre_brasas;"
```

### 6. Aplicar migraciones
```bash
python manage.py migrate
```

### 7. Cargar datos iniciales
```bash
python manage.py seed_data
```

### 8. Levantar servidor
```bash
python manage.py runserver
```

### 9. Abrir en el navegador
Abrir http://localhost:8000/menu/hamburguesas/
