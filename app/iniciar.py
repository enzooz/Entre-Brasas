"""Arranque sin consola. El servidor se apaga desde la aplicación web."""
import argparse
from contextlib import contextmanager
from pathlib import Path
import os
import socket
import sys
import threading
import traceback
import webbrowser

def ya_esta_abierto(puerto):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:
        conexion.settimeout(1)
        return conexion.connect_ex(('127.0.0.1', puerto)) == 0


@contextmanager
def bloquear_arranque(carpeta, puerto):
    """Un doble clic no crea dos servidores ni migraciones simultáneas."""
    import msvcrt
    with (carpeta / f'arranque-{puerto}.lock').open('a+b') as archivo:
        if archivo.tell() == 0:
            archivo.write(b'0')
            archivo.flush()
        archivo.seek(0)
        try:
            msvcrt.locking(archivo.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            yield False
            return
        try:
            yield True
        finally:
            archivo.seek(0)
            msvcrt.locking(archivo.fileno(), msvcrt.LK_UNLCK, 1)


def ejecutar_servidor(application, puerto, abrir_navegador=True):
    from waitress import create_server, wasyncore
    from entre_brasas import servidor_local
    conexiones = {}
    # Mapas permite hasta ocho consultas en espera; quedan trabajadores libres
    # para cargar pedidos, comprobar el estado y apagar aunque Internet esté lento.
    servidor = create_server(application, host='127.0.0.1', port=puerto, map=conexiones, threads=16)
    detener = threading.Event()
    servidor_local.registrar(detener)
    direccion = f'http://127.0.0.1:{servidor.effective_port}'
    print(f'Entre Brasas disponible en {direccion}', flush=True)
    if abrir_navegador:
        webbrowser.open(direccion)
    try:
        while not detener.is_set():
            wasyncore.loop(timeout=0.1, count=1, map=conexiones)
    finally:
        servidor.accepting = False
        # Seguimos enviando respuestas mientras terminan las peticiones.
        # No usamos taskkill ni detenemos otros procesos de Python.
        limpieza = threading.Thread(target=servidor.task_dispatcher.shutdown, kwargs={'timeout': 30})
        limpieza.start()
        while limpieza.is_alive():
            wasyncore.loop(timeout=0.1, count=1, map=conexiones)
        wasyncore.loop(timeout=0.1, count=1, map=conexiones)
        wasyncore.close_all(conexiones)
        servidor_local.registrar(None)
        print('Entre Brasas apagado.', flush=True)


def main():
    parser = argparse.ArgumentParser(description='Entre Brasas en segundo plano')
    parser.add_argument('--puerto', type=int, default=8765)
    parser.add_argument('--sin-navegador', action='store_true')
    parser.add_argument('--desarrollo', action='store_true', help='Usa la base del proyecto para la vista previa')
    opciones = parser.parse_args()
    if not 0 <= opciones.puerto <= 65535:
        parser.error('El puerto debe estar entre 0 y 65535.')
    os.environ['ENTRE_BRASAS_PRODUCCION'] = '0' if opciones.desarrollo else '1'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entre_brasas.settings')
    if opciones.puerto and ya_esta_abierto(opciones.puerto):
        if not opciones.sin_navegador:
            webbrowser.open(f'http://127.0.0.1:{opciones.puerto}')
        return
    # pythonw no tiene stdout/stderr: registramos respaldos y errores.
    carpeta = Path(__file__).resolve().parent if opciones.desarrollo else Path(os.environ['LOCALAPPDATA']) / 'EntreBrasas'
    carpeta.mkdir(parents=True, exist_ok=True)
    with bloquear_arranque(carpeta, opciones.puerto) as adquirido:
        if not adquirido:
            if not opciones.sin_navegador:
                webbrowser.open(f'http://127.0.0.1:{opciones.puerto}')
            return
        with (carpeta / 'servidor.log').open('a', encoding='utf-8', buffering=1) as registro:
            original_out, original_err = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = registro
            try:
                import django
                from django.core.management import call_command
                django.setup()
                call_command('respaldar')
                call_command('migrate', verbosity=0)
                from entre_brasas.wsgi import application
                ejecutar_servidor(application, opciones.puerto, not opciones.sin_navegador)
            except Exception:
                traceback.print_exc()
                if not opciones.sin_navegador:
                    import ctypes
                    ctypes.windll.user32.MessageBoxW(
                        None, f'No se pudo abrir Entre Brasas.\nEl detalle está en:\n{carpeta / "servidor.log"}',
                        'Entre Brasas', 0x10,
                    )
                raise
            finally:
                sys.stdout, sys.stderr = original_out, original_err


if __name__ == '__main__':
    main()
