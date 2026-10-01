"""
Comando para hacer una copia de seguridad de la base de datos.

Se corre asi:
    python manage.py respaldar

iniciar.bat lo corre solo cada vez que se abre el sistema, antes de
levantar el servidor. Las copias quedan en COPIAS_DIR (ver settings.py),
con la fecha y la hora en el nombre:
    entre_brasas_2026-09-26_20-15-30-123456.sqlite3

Se guardan las ultimas 30 copias. Las mas viejas se borran solas para que
la carpeta no crezca para siempre.

Para recuperar una copia: cerrar el sistema, copiar el archivo de la copia
a la carpeta de datos y renombrarlo a db.sqlite3.
"""
import sqlite3
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

CANTIDAD_DE_COPIAS = 30


class Command(BaseCommand):
    help = 'Hace una copia de seguridad de la base de datos'

    def handle(self, *args, **options):
        base = settings.DATABASES['default']['NAME']

        # La primera vez que se instala todavia no hay base que copiar.
        if not base.exists():
            self.stdout.write('Todavia no hay base de datos: no se hace copia.')
            return

        settings.COPIAS_DIR.mkdir(parents=True, exist_ok=True)

        # Instalar y abrir enseguida no deben pisar la copia previa a migrar.
        fecha = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        destino = settings.COPIAS_DIR / f'entre_brasas_{fecha}.sqlite3'

        # SQLite trae su propia forma de copiar una base. Es mas segura que
        # copiar el archivo a mano, porque respeta cualquier escritura que
        # este a medio hacer.
        origen = sqlite3.connect(base)
        copia = sqlite3.connect(destino)
        origen.backup(copia)
        copia.close()
        origen.close()

        self.stdout.write(f'Copia de seguridad guardada en: {destino}')

        self.borrar_copias_viejas()

    def borrar_copias_viejas(self):
        """Deja solo las ultimas CANTIDAD_DE_COPIAS copias."""
        # Como el nombre empieza con la fecha en formato anio-mes-dia,
        # ordenarlos alfabeticamente es lo mismo que ordenarlos por fecha.
        copias = sorted(settings.COPIAS_DIR.glob('entre_brasas_*.sqlite3'))

        for copia_vieja in copias[:-CANTIDAD_DE_COPIAS]:
            copia_vieja.unlink()
