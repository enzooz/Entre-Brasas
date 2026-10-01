"""Control del servidor iniciado por iniciar.py, sin matar otros procesos."""
import threading
from uuid import uuid4

_evento = None
_apagando = False
_lock = threading.Lock()
_instancia = uuid4().hex


def registrar(evento):
    global _evento, _apagando
    with _lock:
        _evento = evento
        _apagando = False


def disponible():
    with _lock:
        return _evento is not None and not _apagando


def estado():
    """Identifica esta ejecución para no bloquear una reapertura nueva."""
    with _lock:
        return {'apagando': _apagando, 'instancia': _instancia}


def solicitar_apagado():
    """Espera un segundo para enviar la pantalla de despedida."""
    global _apagando
    with _lock:
        if _evento is None or _apagando:
            return False
        _apagando = True
        timer = threading.Timer(1, _evento.set)
        timer.daemon = True
        timer.start()
        return True
