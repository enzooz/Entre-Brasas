"""
Interpreta un pedido escrito como mensaje de WhatsApp.

El que esta en la PC copia el mensaje del cliente, lo pega en "Nuevo pedido"
y esto trata de entenderlo para completar el formulario. Por ejemplo:

    Agostina
    1 pepi
    1 crispy doble sin cebolla
    Retira
    (Si podes agregar un dip de alioli)

queda como: nombre Agostina, 1 La Pepi, 1 Crispy doble con la nota
"sin cebolla", retira en el local, y la ultima linea como observacion.

No guarda nada: solo devuelve lo que entendio para que el formulario se
complete. La persona siempre revisa antes de crear el pedido, por eso lo
que no se entiende no se descarta: se devuelve aparte para mostrarlo.

La idea general es mirar el mensaje renglon por renglon y preguntarse
"que es este renglon": un link de Maps, un telefono, "retira", una
hamburguesa, el nombre del cliente, o un comentario.
"""
import re
import unicodedata
from difflib import SequenceMatcher

# Palabras que indican cada cosa. Se comparan ya "normalizadas": en
# minuscula y sin tildes (ver normalizar()).
PALABRAS_RETIRA = ['retira', 'retiro', 'retirar', 'retiramos', 'retiran', 'paso a buscar', 'pasamos a buscar',
                   'lo busco', 'la busco', 'los busco', 'las busco', 'take away', 'para llevar']
PALABRAS_ENVIO = ['envio', 'delivery', 'a domicilio', 'mandame', 'mandamelo', 'enviar', 'me lo traen']
PALABRAS_EFECTIVO = ['efectivo', 'cash']
PALABRAS_TRANSFERENCIA = ['transferencia', 'transfiero', 'transfer', 'mercado pago', 'mercadopago', 'qr', 'alias']

# Lo que suele acompaniar a un telefono: "cel 3624 555666", "mi numero es ...".
PALABRAS_DE_TELEFONO = {'cel', 'celular', 'tel', 'telefono', 'numero', 'nro', 'whatsapp',
                        'wsp', 'mi', 'es', 'el'}

# Renglones que no son parte del pedido: se saltean.
SALUDOS = ['hola', 'buenas', 'buenas noches', 'buenas tardes', 'buen dia', 'buenos dias',
           'gracias', 'muchas gracias', 'porfa', 'por favor', 'como estas', 'que tal']

# "Doble" es un medallon extra y "triple" son dos.
MEDALLONES_SEGUN_PALABRA = {'simple': 0, 'doble': 1, 'triple': 2}

CANTIDADES_EN_LETRAS = {'un': 1, 'una': 1, 'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4,
                        'cinco': 5, 'seis': 6}

# Palabras que no ayudan a reconocer un producto ("la" de "La Pepi").
PALABRAS_VACIAS = {'la', 'el', 'los', 'las', 'de', 'con', 'y', 'extra', 'x'}

# Lo que agrega WhatsApp Web al copiar varios mensajes juntos:
#   [21:30, 27/9/2026] Agostina: 1 pepi
PREFIJO_WHATSAPP = re.compile(r'^\[\d{1,2}:\d{2}[^\]]*\]\s*([^:]+):\s*')
# Un link (el de Google Maps que manda el cliente).
LINK = re.compile(r'https?://\S+')
# Un telefono: 8 numeros o mas, con espacios, guiones o + en el medio.
TELEFONO = re.compile(r'\+?\d[\d\s\-]{6,}\d')
# Una hora suelta, como las que quedan al copiar de WhatsApp: "23:43".
HORA = re.compile(r'\b\d{1,2}:\d{2}\b')
# El nombre dicho en una frase: "soy Carla", "me llamo Tony", "a nombre de Juan Perez".
NOMBRE_ESCRITO = re.compile(r'\b(?:soy|me llamo|a nombre de)\s+([^\W\d_]+(?: [^\W\d_]+)?)', re.IGNORECASE)
# Una direccion escrita despues de "envio a", "a domicilio en", "direccion:".
# Se queda con lo que sigue hasta la primera coma.
DIRECCION_ESCRITA = re.compile(
    r'\b(?:env[ií]o a|env[ií]alo a|a domicilio en|direcci[oó]n:?|dir:)\s*([^,]{3,})',
    re.IGNORECASE,
)


def normalizar(texto):
    """
    Pasa el texto a minuscula y le saca las tildes: "Medallón" -> "medallon".

    Asi "Medallón", "medallon" y "MEDALLON" se comparan igual.
    """
    texto = unicodedata.normalize('NFKD', texto.lower())
    return ''.join(letra for letra in texto if not unicodedata.combining(letra))


def palabras_de(texto):
    """Las palabras de un texto normalizado, sin signos: "1 crispy, doble" -> ['1', 'crispy', 'doble']."""
    return re.findall(r'[a-z0-9]+', normalizar(texto))


def se_parecen(palabra, otra):
    """
    True si dos palabras son la misma aunque este mal escrita.

    "crispi" y "crispy" se parecen; "tradicional" empieza con "tradi".
    """
    if palabra == otra:
        return True
    if len(otra) >= 4 and palabra.startswith(otra):
        return True
    return len(palabra) >= 4 and SequenceMatcher(None, palabra, otra).ratio() >= 0.8


def contiene_alguna(texto_normalizado, lista):
    """True si en el texto aparece alguna de las palabras o frases de la lista."""
    return any(re.search(r'\b' + re.escape(frase) + r'\b', texto_normalizado) for frase in lista)


def buscar_hamburguesa(palabras, hamburguesas):
    """
    Busca que hamburguesa del menu se nombra en estas palabras.

    Una hamburguesa se reconoce si aparecen todas las palabras importantes de
    su nombre ("pepi" para "La Pepi"). Si se nombran dos ("sagrada con cebolla
    crispy"), gana la que aparece primero: la otra seguro es un ingrediente.

    Devuelve la hamburguesa, las palabras que uso y en que posicion aparece
    (sirve para buscar la cantidad justo antes). Si no encontro ninguna,
    devuelve (None, [], 0).
    """
    mejor, mejores_usadas, mejor_posicion = None, [], len(palabras)

    for hamburguesa in hamburguesas:
        claves = [p for p in palabras_de(hamburguesa.nombre) if p not in PALABRAS_VACIAS]
        posiciones = []

        for clave in claves:
            posicion = next((i for i, p in enumerate(palabras) if se_parecen(p, clave)), None)
            if posicion is None:
                break
            posiciones.append(posicion)
        else:
            # El for termino sin "break": se encontraron todas las claves.
            if claves and min(posiciones) < mejor_posicion:
                mejor = hamburguesa
                mejores_usadas = [palabras[i] for i in posiciones]
                mejor_posicion = min(posiciones)

    if mejor is None:
        return None, [], 0

    return mejor, mejores_usadas, mejor_posicion


def buscar_adicionales(palabras, texto_normalizado, adicionales, hamburguesa):
    """
    Busca los adicionales que se piden en estas palabras ("con panceta").

    Cada adicional se reconoce por la primera palabra de su nombre
    ("panceta", "huevo", "cheddar"). Las papas son un caso aparte: si la
    hamburguesa ya incluye papas, "con papas" no es un adicional, asi que
    solo se cuenta si dice "extra" o "+".
    """
    encontrados = []

    for adicional in adicionales:
        claves = [p for p in palabras_de(adicional.nombre) if p not in PALABRAS_VACIAS]
        if not claves or not any(se_parecen(p, claves[0]) for p in palabras):
            continue

        if claves[0] == 'papas' and hamburguesa and hamburguesa.incluye_papas:
            if 'extra' not in palabras and '+' not in texto_normalizado:
                continue

        encontrados.append(adicional)

    return encontrados


def leer_cantidad(palabras, posicion_hamburguesa):
    """
    Cuantas hamburguesas pide: "2 crispy", "dos crispy", "crispy x2". Si no dice, 1.

    Primero se fija si dice "x2", que es lo mas claro ("una tradicional x2"
    son dos). Si no, busca el numero justo antes del nombre de la
    hamburguesa (hasta dos palabras antes), asi "me mandas 2 cheese" da 2.
    """
    for palabra in palabras:
        coincide = re.fullmatch(r'x(\d+)|(\d+)x', palabra)
        if coincide:
            return int(coincide.group(1) or coincide.group(2))

    for palabra in reversed(palabras[max(0, posicion_hamburguesa - 2):posicion_hamburguesa]):
        if palabra.isdigit() and 0 < int(palabra) <= 50:
            return int(palabra)
        if palabra in CANTIDADES_EN_LETRAS:
            return CANTIDADES_EN_LETRAS[palabra]

    return 1


def leer_nota(texto_normalizado):
    """Lo que el cliente pide sacar: "sin cebolla" -> la nota para la cocina."""
    pedidos_sin = re.findall(r'\bsin [a-z ]+?(?=,| y |$| con )', texto_normalizado)
    return ', '.join(pedido.strip() for pedido in pedidos_sin)


def interpretar_mensaje(texto, hamburguesas, adicionales, medallon_extra=None):
    """
    Lee el mensaje y devuelve un diccionario con lo que entendio:

        nombre, telefono, direccion, entrega ('retira', 'envio' o ''),
        pago ('efectivo', 'transferencia' o ''), observaciones,
        items (lista de {hamburguesa_id, cantidad, medallones,
               adicionales, nota}) y no_entendido (renglones sueltos).

    hamburguesas y adicionales son las del menu (las activas). El medallon
    extra se pasa aparte porque no se lista como adicional: se usa para
    "doble" y "triple".
    """
    resultado = {
        'nombre': '', 'telefono': '', 'direccion': '', 'entrega': '', 'pago': '',
        'observaciones': '', 'items': [], 'no_entendido': [],
    }
    observaciones = []
    nombre_de_whatsapp = ''

    for renglon in texto.splitlines():
        # Si vino copiado de WhatsApp Web, el renglon empieza con la hora y
        # el nombre del contacto. El nombre sirve si el cliente no lo escribio.
        prefijo = PREFIJO_WHATSAPP.match(renglon)
        if prefijo:
            nombre_de_whatsapp = nombre_de_whatsapp or prefijo.group(1).strip()
            renglon = renglon[prefijo.end():]

        renglon = HORA.sub('', renglon).strip()
        if not renglon:
            continue

        # 1. Un link: es la ubicacion de Google Maps, o sea que es un envio.
        link = LINK.search(renglon)
        if link:
            resultado['direccion'] = resultado['direccion'] or link.group(0)
            resultado['entrega'] = resultado['entrega'] or 'envio'
            continue

        normalizado = normalizar(renglon)

        # Un saludo o un "gracias" solo no aporta nada al pedido. Los mas
        # largos van primero, asi "buenas noches" se saca entero.
        saludos = sorted(SALUDOS, key=len, reverse=True)
        sin_saludos = re.sub(r'\b(' + '|'.join(saludos) + r')\b', '', normalizado)
        if not palabras_de(sin_saludos):
            continue

        # 2. Retira, envio y forma de pago. Pueden venir solas o dentro de
        #    un renglon con mas cosas, asi que no cortamos: seguimos leyendo.
        if contiene_alguna(normalizado, PALABRAS_RETIRA):
            resultado['entrega'] = 'retira'
        elif contiene_alguna(normalizado, PALABRAS_ENVIO):
            resultado['entrega'] = resultado['entrega'] or 'envio'

        if contiene_alguna(normalizado, PALABRAS_TRANSFERENCIA):
            resultado['pago'] = 'transferencia'
        elif contiene_alguna(normalizado, PALABRAS_EFECTIVO):
            resultado['pago'] = 'efectivo'

        # 3. Un telefono. Se saca del renglon y se sigue leyendo lo que
        #    queda ("362 4915616, pago con transferencia").
        telefono = TELEFONO.search(renglon)
        if telefono and len(re.sub(r'\D', '', telefono.group(0))) >= 8:
            resultado['telefono'] = resultado['telefono'] or telefono.group(0).strip()
            renglon = (renglon[:telefono.start()] + renglon[telefono.end():]).strip(' ,.-:')
            normalizado = normalizar(renglon)

            # Si lo unico que quedaba era "cel", "mi numero es", etc., listo.
            if all(p in PALABRAS_DE_TELEFONO for p in palabras_de(renglon)):
                continue

        # Una direccion escrita: "envio a Jujuy 87", "direccion: Jujuy 87".
        # Se saca del renglon, asi lo que queda se sigue leyendo.
        direccion = DIRECCION_ESCRITA.search(renglon)
        if direccion:
            resultado['direccion'] = resultado['direccion'] or direccion.group(1).strip()
            resultado['entrega'] = resultado['entrega'] or 'envio'
            normalizado = normalizar(renglon[:direccion.start()] + renglon[direccion.end():])

        # 4. Hamburguesas. Un renglon puede traer varias: "1 pepi y 2 cheese".
        if leer_hamburguesas_del_renglon(normalizado, hamburguesas, adicionales,
                                         medallon_extra, resultado['items']):
            continue

        if direccion:
            continue

        solo_palabras_clave = contiene_alguna(
            normalizado, PALABRAS_RETIRA + PALABRAS_ENVIO + PALABRAS_EFECTIVO + PALABRAS_TRANSFERENCIA
        ) and len(palabras_de(renglon)) <= 4
        if solo_palabras_clave:
            continue

        # 5. El nombre del cliente: dicho ("soy Carla", "a nombre de Tony")
        #    o un renglon corto solo con letras ("Agostina", "tony").
        nombre_dicho = NOMBRE_ESCRITO.search(renglon)
        if nombre_dicho and not resultado['nombre']:
            resultado['nombre'] = nombre_dicho.group(1).title()
            continue

        # "con papas", "sin sal", "extra cheddar" no son nombres.
        empieza_como_pedido = re.match(r'(con|sin|extra|mas|y)\b', normalizado)
        es_nombre = not empieza_como_pedido and re.fullmatch(r'[^\W\d_]+( [^\W\d_]+){0,2}', renglon)
        if es_nombre and not resultado['nombre']:
            resultado['nombre'] = renglon.title()
            continue

        # 6. Lo demas es un comentario del cliente. Va a observaciones y
        #    tambien se avisa, para que la persona lo mire.
        comentario = renglon.strip('()[] ')
        observaciones.append(comentario)
        resultado['no_entendido'].append(comentario)

    resultado['nombre'] = resultado['nombre'] or nombre_de_whatsapp.title()
    resultado['observaciones'] = '. '.join(observaciones)

    return resultado


def leer_hamburguesas_del_renglon(normalizado, hamburguesas, adicionales, medallon_extra, items):
    """
    Busca las hamburguesas de un renglon y las agrega a items.

    Separa el renglon por comas y por " y ". Si un pedazo no nombra ninguna
    hamburguesa pero pide un adicional ("crispy con panceta y huevo"), el
    adicional es de la hamburguesa anterior, aunque este en otro renglon
    ("1 crispy" y abajo "con panceta").

    Devuelve True si entendio algo del renglon (una hamburguesa, o algo que
    le agrego a la anterior).
    """
    encontro = False
    item_anterior = items[-1] if items else None

    for pedazo in re.split(r',| y |\+', normalizado):
        # Lo que va despues de "sin" es para sacar, no para agregar: queda
        # como nota y no se usa para buscar hamburguesas ni adicionales.
        # Asi "sin panceta" no suma panceta y "sin pepinillos" no es La Pepi.
        nota = leer_nota(pedazo.strip())
        palabras = palabras_de(re.sub(r'\bsin [a-z ]+?(?=,| y |$| con )', '', pedazo.strip()))
        if not palabras and not nota:
            continue

        hamburguesa, usadas, posicion = buscar_hamburguesa(palabras, hamburguesas)
        resto = [p for p in palabras if p not in usadas]

        if hamburguesa:
            medallones = 0
            for palabra in resto:
                if palabra in MEDALLONES_SEGUN_PALABRA:
                    medallones = MEDALLONES_SEGUN_PALABRA[palabra]

            item_anterior = {
                'hamburguesa_id': hamburguesa.pk,
                'cantidad': leer_cantidad(palabras, posicion),
                'medallones': medallones,
                'adicionales': [a.pk for a in buscar_adicionales(resto, normalizado, adicionales, hamburguesa)],
                'nota': nota,
            }
            items.append(item_anterior)
            encontro = True

        elif item_anterior:
            # Un pedazo sin hamburguesa: puede ser un adicional, un "doble"
            # o un "sin ..." de la hamburguesa anterior.
            hamburguesa_anterior = next(
                (h for h in hamburguesas if h.pk == item_anterior['hamburguesa_id']), None
            )
            for adicional in buscar_adicionales(palabras, normalizado, adicionales, hamburguesa_anterior):
                if adicional.pk not in item_anterior['adicionales']:
                    item_anterior['adicionales'].append(adicional.pk)
                    encontro = True

            if medallon_extra and any(se_parecen(p, 'medallon') for p in palabras):
                item_anterior['medallones'] = min(item_anterior['medallones'] + 1, 2)
                encontro = True

            for palabra in palabras:
                if palabra in ('doble', 'triple'):
                    item_anterior['medallones'] = MEDALLONES_SEGUN_PALABRA[palabra]
                    encontro = True

            if nota:
                item_anterior['nota'] = ', '.join(filter(None, [item_anterior['nota'], nota]))
                encontro = True

    return encontro
