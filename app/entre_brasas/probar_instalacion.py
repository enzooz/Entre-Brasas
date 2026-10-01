r"""Prueba real del instalador en una carpeta temporal, nunca en datos del local.

Desde la raíz: app\venv\Scripts\python.exe app\entre_brasas\probar_instalacion.py
Requiere Windows e internet para instalar dependencias en un entorno NUEVO.
"""
from contextlib import closing
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile


def main():
    if os.name != 'nt':
        raise SystemExit('Esta prueba verifica el instalador de Windows.')
    origen = Path(__file__).resolve().parents[2]
    with tempfile.TemporaryDirectory(prefix='entre-brasas-instalar-') as temporal:
        raiz = Path(temporal).resolve()
        proyecto = raiz / 'Programa'
        proyecto.mkdir()
        # Copiar SOLO código. No transportar la base, el entorno ni respaldos.
        destino = (proyecto / 'app').resolve()
        if not destino.is_relative_to(raiz):
            raise RuntimeError('Destino de prueba fuera de su carpeta aislada.')
        shutil.copytree(origen / 'app', destino, ignore=shutil.ignore_patterns(
            'venv', '__pycache__', '*.sqlite3', '*.log', '*.lock', 'copias_de_seguridad',
        ))
        shutil.copy2(origen / 'instalar.bat', proyecto / 'instalar.bat')
        escritorio = raiz / 'Escritorio'
        escritorio.mkdir()
        env = os.environ.copy()
        env['LOCALAPPDATA'] = str(raiz / 'Datos')
        env['ENTRE_BRASAS_ESCRITORIO'] = str(escritorio)
        env['DJANGO_SETTINGS_MODULE'] = 'entre_brasas.settings_pruebas_servidor'
        env['PATH'] = str(origen / 'app' / 'venv' / 'Scripts') + os.pathsep + env['PATH']
        env.pop('PYTHONPATH', None)
        env['PIP_DEFAULT_TIMEOUT'] = '20'
        base = Path(env['LOCALAPPDATA']) / 'EntreBrasas' / 'db.sqlite3'

        def instalar():
            resultado = subprocess.run(['cmd.exe', '/d', '/c', 'instalar.bat', '--sin-pausa'],
                cwd=proyecto, env=env, capture_output=True, text=True, errors='replace', timeout=180,
                creationflags=subprocess.CREATE_NO_WINDOW)
            if resultado.returncode:
                raise RuntimeError(resultado.stdout + resultado.stderr)

        instalar()
        with closing(sqlite3.connect(base)) as conexion:
            assert conexion.execute('SELECT COUNT(*) FROM menu_hamburguesa WHERE activa=1').fetchone()[0] == 8
            assert conexion.execute('SELECT COUNT(*) FROM inventario_ingrediente WHERE stock_actual <> 0').fetchone()[0] == 0
        acceso = escritorio / 'Entre Brasas.lnk'
        env['ENTRE_BRASAS_ACCESO_PRUEBA'] = str(acceso)
        leer = "$s=(New-Object -ComObject WScript.Shell).CreateShortcut($env:ENTRE_BRASAS_ACCESO_PRUEBA); @{target=$s.TargetPath; arguments=$s.Arguments; working=$s.WorkingDirectory} | ConvertTo-Json -Compress"
        resultado = subprocess.run(['powershell.exe', '-NoProfile', '-Command', leer], env=env, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        shortcut = json.loads(resultado.stdout)
        assert Path(shortcut['target']).resolve() == (destino / 'venv' / 'Scripts' / 'pythonw.exe').resolve()
        assert str(destino / 'iniciar.py') in shortcut['arguments']
        assert Path(shortcut['working']).resolve() == destino
        python = destino / 'venv' / 'Scripts' / 'python.exe'
        preparar = "from pedidos.models import Cliente,Pedido; from config.models import Configuracion; from menu.models import Hamburguesa; c=Cliente.objects.create(nombre='Cliente de instalación',telefono='3621234567',telefono_clave='3621234567'); Pedido.objects.create(cliente=c,cliente_nombre=c.nombre,total=12345); Configuracion.objects.update(tarifa_100m=123.45); Hamburguesa.objects.filter(nombre='Cheese').update(precio=14200)"
        env['ENTRE_BRASAS_PRODUCCION'] = '1'
        subprocess.run([str(python), 'manage.py', 'shell', '-c', preparar], cwd=destino, env=env, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        instalar()  # Actualizar no recarga menú ni pisa pedidos, clientes o tarifas.
        with closing(sqlite3.connect(base)) as conexion:
            assert conexion.execute('SELECT total FROM pedidos_pedido').fetchall() == [(12345,)]
            assert conexion.execute('SELECT COUNT(*) FROM pedidos_cliente').fetchone()[0] == 1
            assert conexion.execute('SELECT tarifa_100m FROM config_configuracion').fetchone()[0] == 123.45
            assert conexion.execute("SELECT precio FROM menu_hamburguesa WHERE nombre='Cheese'").fetchone()[0] == 14200
        assert list((base.parent / 'copias').glob('*.sqlite3'))
        print('OK: instalación limpia, menú, stock inicial 0, acceso sin consola y actualización conservando datos.')


if __name__ == '__main__':
    main()
