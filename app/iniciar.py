"""
Arranca Entre Brasas en la compu del cliente.

Lo corre iniciar.bat (el acceso directo del escritorio). Hace, en orden:

    1. Si el sistema ya esta abierto, solo abre el navegador y termina.
    2. Hace una copia de seguridad de la base.
    3. Aplica las migraciones pendientes (por si se instalo una version nueva).
    4. Abre el navegador en la pantalla del sistema.
    5. Levanta el servidor, que queda andando mientras la ventana este abierta.

Usa waitress en vez de "runserver": runserver es para desarrollar, y
waitress es un servidor pensado para dejar andando todo el dia.
"""
import os
import socket
import threading
import webbrowser

# Esto tiene que ir antes de cargar Django: activa el modo local del
# cliente en settings.py (datos aparte, DEBUG apagado, etc.).
os.environ['ENTRE_BRASAS_PRODUCCION'] = '1'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entre_brasas.settings')

import django  # noqa: E402
from django.core.management import call_command  # noqa: E402

PUERTO = 8765
DIRECCION = f'http://127.0.0.1:{PUERTO}'


def ya_esta_abierto():
    """True si ya hay algo escuchando en el puerto del sistema."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:
        return conexion.connect_ex(('127.0.0.1', PUERTO)) == 0


def main():
    # Si el cliente le hace doble clic al icono con el sistema ya abierto,
    # no se levanta un segundo servidor: se le abre otra pestania y listo.
    if ya_esta_abierto():
        webbrowser.open(DIRECCION)
        return

    django.setup()

    call_command('respaldar')
    call_command('migrate', verbosity=0)

    # El navegador se abre un segundo despues, cuando el servidor ya arranco.
    threading.Timer(1.5, webbrowser.open, args=[DIRECCION]).start()

    print()
    print('=' * 60)
    print('  ENTRE BRASAS esta funcionando.')
    print(f'  Direccion: {DIRECCION}')
    print()
    print('  Podes minimizar esta ventana, pero NO la cierres:')
    print('  si la cerras, el sistema se apaga.')
    print('=' * 60)
    print()

    from waitress import serve
    from entre_brasas.wsgi import application

    serve(application, host='127.0.0.1', port=PUERTO)


if __name__ == '__main__':
    main()
