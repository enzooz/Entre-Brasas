"""
Vistas de la app Pedidos.

Una vista es una funcion que recibe un request (lo que pide el navegador)
y devuelve una respuesta (una pantalla HTML o una redireccion).

El patron que se repite en casi todas es este:
    si el metodo es POST  -> el usuario mando el formulario: guardamos y redirigimos
    si no                 -> el usuario esta entrando: mostramos la pantalla

Redirigir despues de guardar es a proposito: evita que si el usuario aprieta
F5 se vuelva a mandar el mismo pedido dos veces.

Las cuentas no estan aca, estan en calculos.py.
"""
from urllib.parse import quote
from django.conf import settings
from decimal import Decimal, InvalidOperation
from uuid import UUID

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.db.models import Q
import re

from menu.models import Hamburguesa, Adicional
from config.models import Configuracion
from inventario.models import formatear_cantidad

from .models import Cliente, Pedido, ItemPedido, AdicionalDeItem, HistorialEstado
from .clientes import cliente_para_pedido, normalizar_telefono
from .calculos import calcular_envio, calcular_total, descontar_stock, devolver_stock
from .comanda import armar_comanda
from .interpretar import interpretar_mensaje


@transaction.atomic
def crear_pedido(request):
    """
    Pantalla para cargar un pedido nuevo. Es la pantalla principal del sistema.

    Esta pensada para cargar rapido lo que llega por WhatsApp: si el cliente
    retira, alcanza con el nombre. Direccion y telefono solo se piden para
    los envios.
    """
    if request.method == 'POST':
        # El formulario manda "true" o "false" como texto, asi que lo
        # comparamos con el texto "true" para obtener un verdadero/falso.
        retiro_local = request.POST.get('retiro_local') == 'true'

        error = validar_pedido(request.POST, retiro_local)
        if error:
            # El formulario ya controla esto antes de mandar, asi que aca
            # solo se llega si algo se salteo ese control.
            messages.error(request, error)
            return redirect('pedidos:crear_pedido')

        # Si retira, la distancia no importa aunque haya quedado escrita.
        distancia_km = 0
        if not retiro_local:
            distancia_km = Decimal(request.POST['distancia_km'].replace(',', '.'))

        pedido = Pedido.objects.create(
            cliente=cliente_para_pedido(request.POST),
            cliente_nombre=request.POST.get('cliente_nombre', '').strip(),
            cliente_telefono=request.POST.get('cliente_telefono', '').strip(),
            cliente_direccion=request.POST.get('cliente_direccion', '').strip(),
            observaciones=request.POST.get('observaciones', '').strip(),
            metodo_pago=request.POST.get('metodo_pago', 'efectivo'),
            distancia_km=distancia_km,
            retiro_local=retiro_local,
            costo_envio=calcular_envio(distancia_km, retiro_local),
        )

        # El pedido ya existe pero esta vacio: ahora le agregamos las hamburguesas.
        crear_items_del_pedido(pedido, request.POST)

        # El total se calcula recien ahora, porque necesita los items ya creados.
        pedido.total = calcular_total(pedido)
        pedido.save()

        # Vamos al detalle, donde esta la comanda lista para mandar a cocina.
        messages.success(request, f'Pedido #{pedido.pk} creado. Mandale la comanda a la cocina.')
        respuesta = redirect('pedidos:detalle_pedido', pedido_id=pedido.pk)
        try:
            token = UUID(request.POST.get('borrador_token', ''))
        except (ValueError, TypeError, AttributeError):
            token = None
        if token:
            # Señal no secreta, emitida solo después de guardar correctamente.
            # Una cookie por token evita mezclar pedidos de pestañas distintas.
            respuesta.set_cookie('eb_pedido_creado_' + token.hex, '1', max_age=300, samesite='Strict')
        return respuesta

    # Si es GET mostramos el formulario con los productos disponibles.
    # Solo los activos: los dados de baja no se ofrecen.
    configuracion = Configuracion.get_config()

    return render(request, 'pedidos/crear_pedido.html', {
        'hamburguesas': Hamburguesa.objects.filter(activa=True),
        # Lo que necesita el JavaScript del formulario. El template lo
        # pasa con json_script, que lo escribe de forma segura.
        'datos_formulario': {
            'adicionales': [
                datos_de_adicional(adicional)
                for adicional in Adicional.objects.filter(activo=True, es_medallon_extra=False)
            ],
            # El medallon extra va aparte: se pueden sumar uno o dos a la
            # receta base. Si no hay ninguno disponible, es None.
            'medallon_extra': datos_de_adicional(
                Adicional.objects.filter(activo=True, es_medallon_extra=True).first()
            ),
            'tarifa_100m': str(configuracion.tarifa_100m),
            'distancia_minima': float(configuracion.distancia_minima),
            'costo_minimo_envio': configuracion.costo_minimo_envio,
            'mapas': {
                'habilitado': bool(configuracion.geoapify_api_key),
                'origen': [configuracion.local_latitud, configuracion.local_longitud],
                'tile_url': settings.MAPAS_TILE_URL,
                'tile_attribution': settings.MAPAS_TILE_ATTRIBUTION,
            },
        },
    })


@never_cache
@require_GET
def buscar_clientes(request):
    """Consulta local acotada; no crea clientes ni cambia pedidos."""
    consulta = request.GET.get('q', '').strip()[:100]
    if len(consulta) < 2:
        return JsonResponse({'clientes': []})
    filtro = Q(nombre__icontains=consulta)
    digitos = re.sub(r'[^0-9]', '', consulta)
    if len(digitos) >= 2:
        filtro |= Q(telefono_clave__contains=digitos)
    clientes = Cliente.objects.filter(filtro).values('id', 'nombre', 'telefono', 'direccion')[:8]
    return JsonResponse({'clientes': list(clientes)})


@require_POST
def interpretar_mensaje_view(request):
    """
    Recibe el mensaje de WhatsApp que pego el usuario y devuelve lo que se
    entendio, para que el formulario de Nuevo pedido se complete solo.

    No guarda nada. Responde JSON (datos, no una pantalla) porque lo pide
    el JavaScript del formulario sin recargar la pagina.
    """
    adicionales = Adicional.objects.filter(activo=True)

    resultado = interpretar_mensaje(
        request.POST.get('mensaje', ''),
        hamburguesas=Hamburguesa.objects.filter(activa=True),
        adicionales=adicionales.filter(es_medallon_extra=False),
        medallon_extra=adicionales.filter(es_medallon_extra=True).first(),
    )

    return JsonResponse(resultado)


def datos_de_adicional(adicional):
    """Los datos de un adicional que usa el formulario, como diccionario."""
    if adicional is None:
        return None

    return {
        'id': adicional.pk,
        'nombre': adicional.nombre,
        'precio': adicional.precio,
        # En que hamburguesas se ofrece.
        'hamburguesas': list(adicional.hamburguesas.values_list('pk', flat=True)),
    }


def validar_pedido(datos, retiro_local):
    """
    Revisa que el pedido tenga lo minimo para poder cargarse.

    Devuelve el mensaje de error, o None si esta todo bien.
    """
    if not datos.get('cliente_nombre', '').strip():
        return 'Falta el nombre del cliente.'
    for campo, limite in [('cliente_nombre', 200), ('cliente_telefono', 50), ('cliente_direccion', 300)]:
        if len(datos.get(campo, '').strip()) > limite:
            return f'El campo {campo.replace("cliente_", "")} admite hasta {limite} caracteres.'
    if datos.get('cliente_telefono', '').strip() and not normalizar_telefono(datos['cliente_telefono']):
        return 'Ingresá un teléfono de entre 7 y 20 dígitos; puede incluir espacios, + y guiones.'
    elegido = datos.get('cliente_id', '')
    if elegido and (not elegido.isascii() or not elegido.isdigit() or len(elegido) > 18 or not Cliente.objects.filter(pk=elegido).exists()):
        return 'Ese cliente ya no está disponible. Buscalo otra vez o cargá un cliente nuevo.'

    filas = datos.getlist('filas[]')
    if not any(datos.get(f'hamburguesa_{fila}') for fila in filas):
        return 'El pedido no tiene ninguna hamburguesa.'

    if len(filas) > 100 or len(set(filas)) != len(filas):
        return 'El pedido admite hasta 100 hamburguesas, cada una en su propia fila.'
    cantidad_total = 0
    for fila in filas:
        try:
            cantidad = int(datos.get(f'cantidad_{fila}') or 1)
            medallones = int(datos.get(f'medallones_{fila}') or 0)
            producto_id = int(datos.get(f'hamburguesa_{fila}') or 0)
            extras = [int(pk) for pk in datos.getlist(f'adicionales_{fila}[]')]
        except (ValueError, TypeError):
            return 'Revisá las hamburguesas y los adicionales del pedido.'
        cantidad_total += cantidad
        if cantidad < 1 or cantidad_total > 100 or medallones not in (0, 1, 2):
            return 'Revisá las cantidades: hasta 100 hamburguesas y hasta 2 medallones extra por unidad.'
        if not Hamburguesa.objects.filter(pk=producto_id, activa=True).exists():
            return 'Una hamburguesa ya no está disponible. Volvé a elegirla del menú.'
        permitidos = Adicional.objects.filter(activo=True, es_medallon_extra=False, hamburguesas=producto_id)
        if len(extras) != len(set(extras)) or permitidos.filter(pk__in=extras).count() != len(extras):
            return 'Un adicional no está disponible para esa hamburguesa.'
        if medallones and not Adicional.objects.filter(activo=True, es_medallon_extra=True, hamburguesas=producto_id).exists():
            return 'Esa hamburguesa no admite medallones extra.'
        if len(datos.get(f'nota_{fila}', '').strip()) > 200:
            return 'La nota de cada hamburguesa admite hasta 200 caracteres.'

    if not retiro_local:
        if not datos.get('cliente_direccion', '').strip():
            return 'Para un envio hace falta la direccion o el link de Maps.'
        if not datos.get('cliente_telefono', '').strip():
            return 'Para un envio hace falta el telefono.'
        try:
            distancia = Decimal(datos.get('distancia_km', '').replace(',', '.'))
            if not distancia.is_finite() or distancia < 0 or distancia > Decimal('999.9'):
                return 'Ingresá una distancia entre 0 y 999,9 km.'
            if distancia != distancia.quantize(Decimal('0.1')):
                return 'Ingresá la distancia con hasta un decimal, por ejemplo 5,4 km.'
        except InvalidOperation:
            return 'Ingresá la distancia en kilómetros, por ejemplo 5,4.'

    return None


def crear_items_del_pedido(pedido, datos):
    """
    Crea las lineas del pedido a partir de lo que mando el formulario.

    No es una vista: es una funcion de ayuda que usa crear_pedido() para
    no quedar demasiado larga.

    Cada hamburguesa del pedido es una "fila" del formulario, y cada fila
    tiene un numero. Todos los campos de esa fila llevan su numero en el
    nombre:

        filas[]         = ['0', '1']        las filas que hay
        hamburguesa_0   = '4'               que hamburguesa es
        cantidad_0      = '1'
        medallones_0    = '1'               cantidad de medallones extra
        adicionales_0[] = ['7', '9']        los demas adicionales
        nota_0          = 'dip de alioli'

    Van por numero de fila y no por hamburguesa a proposito: asi dos filas
    de la misma hamburguesa (una doble y otra simple) no se mezclan.
    """
    medallon_extra = Adicional.objects.filter(es_medallon_extra=True, activo=True).first()

    # getlist() trae TODOS los valores de un campo que se repite.
    # Si usaramos .get() nos traeria solo el ultimo.
    for fila in datos.getlist('filas[]'):
        id_hamburguesa = datos.get(f'hamburguesa_{fila}')

        # Si quedo una fila sin hamburguesa, la salteamos.
        if not id_hamburguesa:
            continue

        hamburguesa = get_object_or_404(Hamburguesa, pk=id_hamburguesa)

        # Cada medallon extra es una linea
        # de adicional, asi se cobra y se descuenta del stock como cualquier otro.
        adicionales = []
        if medallon_extra:
            medallones = int(datos.get(f'medallones_{fila}') or 0)
            adicionales = adicionales + [medallon_extra] * medallones

        for id_adicional in datos.getlist(f'adicionales_{fila}[]'):
            if id_adicional:
                adicionales.append(get_object_or_404(Adicional, pk=id_adicional))

        # También separamos unidades de clientes antiguos que manden cantidad
        # mayor a 1. Nunca se agrupan items de hamburguesas diferentes.
        for unidad in range(int(datos.get(f'cantidad_{fila}') or 1)):
            item = ItemPedido.objects.create(
                pedido=pedido, hamburguesa=hamburguesa, cantidad=1,
                precio_unitario=hamburguesa.precio,
                nota=datos.get(f'nota_{fila}', '').strip(),
            )
            for adicional in adicionales:
                AdicionalDeItem.objects.create(
                    item=item, adicional=adicional, precio=adicional.precio,
                )


def cola_pedidos(request):
    """
    La cola de cocina: los pedidos que todavia estan en curso.

    exclude() es lo contrario de filter(): trae todo MENOS lo que le pasamos.
    """
    pedidos = Pedido.objects.exclude(estado__in=['entregado', 'cancelado'])

    # Filtros opcionales, vienen en la direccion: ?busqueda=juan&estado=pendiente
    busqueda = request.GET.get('busqueda', '')
    estado = request.GET.get('estado', '')

    # Cada filter() le agrega una condicion mas a la busqueda.
    if busqueda:
        # icontains quiere decir "que contenga", sin diferenciar mayusculas.
        pedidos = pedidos.filter(cliente_nombre__icontains=busqueda)

    if estado:
        pedidos = pedidos.filter(estado=estado)

    # Cada tarjeta tiene un boton para volver a copiar la comanda, por si
    # hay que reenviarsela a la cocina. list() arma la lista una sola vez,
    # asi el texto que le agregamos a cada pedido llega al template.
    pedidos = list(pedidos)
    for pedido in pedidos:
        pedido.comanda = armar_comanda(pedido)

    return render(request, 'pedidos/cola_pedidos.html', {
        'pedidos': pedidos,
        # Devolvemos los filtros para que los campos queden completados.
        'busqueda': busqueda,
        'estado': estado,
        'estados': Pedido.ESTADOS,
    })


def detalle_pedido(request, pedido_id):
    """
    La ficha de un pedido: que se pidio, cuanto sale y en que estado esta.

    pedido_id llega desde la direccion (ver urls.py).
    """
    # get_object_or_404: si el pedido no existe muestra una pagina de
    # "no encontrado" en vez de romperse.
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    # Estas dos cuentas se hacen aca y no en la pantalla porque los
    # templates de Django no saben sumar ni multiplicar.
    total_hamburguesas = 0
    total_adicionales = 0

    for item in pedido.items.all():
        total_hamburguesas = total_hamburguesas + item.subtotal

        for adicional in item.adicionales.all():
            total_adicionales = total_adicionales + (adicional.precio * item.cantidad)

    comanda = armar_comanda(pedido)

    # Si esta cargado el WhatsApp de la cocina, armamos el link que abre
    # WhatsApp con la comanda ya escrita. quote() convierte el texto al
    # formato de las direcciones web (los espacios pasan a %20, etc.).
    link_whatsapp = ''
    numero_cocina = Configuracion.get_config().whatsapp_cocina
    if numero_cocina:
        link_whatsapp = f'https://wa.me/{numero_cocina}?text={quote(comanda)}'

    return render(request, 'pedidos/detalle_pedido.html', {
        'pedido': pedido,
        'total_hamburguesas': total_hamburguesas,
        'total_adicionales': total_adicionales,
        'comanda': comanda,
        'link_whatsapp': link_whatsapp,
    })


def avanzar_pedido(request, pedido_id):
    """
    Pasa el pedido al siguiente estado.

    El recorrido es:
        pendiente -> en preparacion -> en camino -> entregado
    """
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    # El recorrido de los estados esta en el modelo (Pedido.SIGUIENTE_ESTADO).
    nuevo_estado = pedido.siguiente_estado

    # None quiere decir que el pedido ya estaba entregado o cancelado.
    if not nuevo_estado:
        messages.error(request, 'Este pedido ya no se puede avanzar')
        return redirect('pedidos:cola_pedidos')

    # El stock se descuenta cuando el pedido entra en preparacion, no antes:
    # un pedido pendiente todavia no consumio nada.
    # Nunca frena el pedido: si algun ingrediente queda en negativo, avisa
    # para que se haga un conteo, pero el pedido sigue.
    if nuevo_estado == 'en_preparacion':
        quedaron_en_negativo = descontar_stock(pedido)

        if quedaron_en_negativo:
            detalle = ', '.join(
                f'{ingrediente.nombre} (quedo en {formatear_cantidad(ingrediente.stock_actual)} {ingrediente.unidad})'
                for ingrediente in quedaron_en_negativo
            )
            messages.warning(
                request,
                f'Ojo: segun el sistema se uso mas de lo que habia de {detalle}. '
                'Cuando puedas, conta lo que hay y cargalo en Inventario > Registrar movimiento > Conteo.'
            )

    # Guardamos el cambio en el historial ANTES de pisar el estado,
    # porque despues ya no vamos a saber cual era el anterior.
    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior=pedido.estado,
        estado_nuevo=nuevo_estado
    )

    pedido.estado = nuevo_estado
    pedido.save()

    # get_estado_display() devuelve el texto lindo ("En preparacion")
    # en lugar del valor que se guarda ("en_preparacion").
    messages.success(request, f'Pedido #{pedido.pk} pasa a {pedido.get_estado_display()}')
    return redirect('pedidos:cola_pedidos')


def cancelar_pedido(request, pedido_id):
    """
    Cancela un pedido y, si corresponde, devuelve el stock al inventario.
    """
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    # Un pedido ya cerrado no se puede volver a cancelar.
    if pedido.estado in ['entregado', 'cancelado']:
        messages.error(request, 'Este pedido ya esta cerrado y no se puede cancelar')
        return redirect('pedidos:cola_pedidos')

    # Solo tiene sentido devolver stock si el pedido llego a descontarlo,
    # o sea si estaba en preparacion o en camino. Un pedido pendiente
    # nunca toco el inventario.
    if pedido.estado in ['en_preparacion', 'en_camino']:
        if request.POST.get('devolver_stock') == 'si':
            devolver_stock(pedido)
            messages.success(request, f'Se devolvio el stock del pedido #{pedido.pk}')
        else:
            messages.warning(
                request,
                f'El pedido #{pedido.pk} se cancela sin devolver stock (se registra como perdida)'
            )

    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior=pedido.estado,
        estado_nuevo='cancelado',
        observacion=request.POST.get('motivo', '')
    )

    pedido.estado = 'cancelado'
    pedido.save()

    messages.success(request, f'Pedido #{pedido.pk} cancelado')
    return redirect('pedidos:cola_pedidos')


def historial_pedidos(request):
    """
    Los pedidos que ya terminaron, entregados o cancelados.

    Es el espejo de cola_pedidos(): aquella trae los abiertos, esta los cerrados.
    Ademas permite filtrar por rango de fechas.
    """
    pedidos = Pedido.objects.filter(estado__in=['entregado', 'cancelado'])

    busqueda = request.GET.get('busqueda', '')
    estado = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    if busqueda:
        pedidos = pedidos.filter(cliente_nombre__icontains=busqueda)

    if estado:
        pedidos = pedidos.filter(estado=estado)

    if fecha_desde:
        # __date se queda solo con la fecha e ignora la hora.
        # __gte quiere decir "mayor o igual que".
        pedidos = pedidos.filter(fecha_creacion__date__gte=fecha_desde)

    if fecha_hasta:
        # __lte quiere decir "menor o igual que".
        pedidos = pedidos.filter(fecha_creacion__date__lte=fecha_hasta)

    return render(request, 'pedidos/historial_pedidos.html', {
        'pedidos': pedidos,
        'busqueda': busqueda,
        'estado': estado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })
