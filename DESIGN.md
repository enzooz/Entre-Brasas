---
name: Entre Brasas
description: Un sistema claro para operar el local.
colors:
  primary: '#2455d6'
  primary-dark: '#1942ad'
  primary-light: '#eaf0ff'
  navigation: '#102349'
  background: '#f5f6fa'
  surface: '#ffffff'
  text: '#202c42'
  text-secondary: '#647086'
  border: '#e2e6ee'
  success: '#16724c'
  danger: '#b43242'
  warning: '#956400'
  info: '#087584'
typography:
  headline:
    fontFamily: 'Manrope, Segoe UI, sans-serif'
    fontSize: '27px'
    fontWeight: 800
    lineHeight: 1.3
    letterSpacing: '-0.8px'
  title:
    fontFamily: 'Manrope, Segoe UI, sans-serif'
    fontSize: '17px'
    fontWeight: 800
    lineHeight: 1.4
  body:
    fontFamily: 'Manrope, Segoe UI, sans-serif'
    fontSize: '14px'
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: 'Manrope, Segoe UI, sans-serif'
    fontSize: '12px'
    fontWeight: 700
rounded:
  sm: '8px'
  md: '12px'
  lg: '18px'
spacing:
  compact: '8px'
  field: '12px'
  component: '20px'
  panel: '24px'
  content: '36px'
components:
  button-primary:
    backgroundColor: '{colors.primary}'
    textColor: '{colors.surface}'
    rounded: '{rounded.sm}'
    padding: '10px 16px'
  button-secondary:
    backgroundColor: '{colors.surface}'
    textColor: '{colors.text}'
    rounded: '{rounded.sm}'
    padding: '10px 16px'
  input:
    backgroundColor: '{colors.surface}'
    textColor: '{colors.text}'
    rounded: '{rounded.sm}'
    padding: '11px 13px'
    height: '44px'
  panel:
    backgroundColor: '{colors.surface}'
    textColor: '{colors.text}'
    rounded: '{rounded.md}'
    padding: '24px'
---

# Design System: Entre Brasas

## Overview

Un puesto de trabajo para el local: la tarea principal se encuentra primero y cada pantalla explica cómo seguir. Se conserva el azul, con navegación marina, superficies claras y lenguaje cotidiano en español argentino. La personalidad aparece en la marca y en los textos; la operación mantiene controles familiares.

La fuente visual es `app/static/css/sistema.css`, cargada después de las utilidades originales de `estilo.css`. Los componentes compartidos están en `templates/base.html`, `templates/components/icon.html` e `interfaz.js`.

## Colors

El azul identifica acciones principales y la ubicación actual. El fondo gris frío separa las superficies blancas; los textos secundarios conservan contraste. Los estados combinan texto y color: pendiente amarillo, preparación turquesa, en camino ámbar, entregado verde y cancelado rojo. Un botón que avanza toma el color del estado de destino.

**Una acción, un significado.** Usar azul para la acción principal y rojo para cancelar. No comunicar un estado solo por color.

## Typography

Manrope se sirve desde archivos locales, con pesos 400, 500, 600, 700 y 800; no depende de Google Fonts durante el uso. Su licencia OFL acompaña los archivos. Los títulos de pantalla usan headline; las secciones, title. En celular el título principal baja a 24px. Etiquetas y botones usan label; texto auxiliar y metadatos pueden ser más compactos. Las cantidades usan cifras tabulares.

## Layout

Navegación fija de 248px en escritorio y contenido con márgenes de 36px, reducidos a 25px en anchos intermedios. La navegación agrupa día a día, menú y recetas, stock y negocio. La página actual se marca visualmente y con `aria-current`.

A 760px o menos, el menú se convierte en un panel desplegable y el contenido tiene márgenes de 20px. El fondo queda inactivo al abrirlo; Escape cierra y devuelve el foco. Las tablas se desplazan dentro de un contenedor accesible, con una indicación visible en celular cuando no entran. Inicio y formularios reorganizan sus columnas; nunca esconder información para que una tabla entre.

## Elevation & Depth

Superficies planas con bordes y capas de color. Las cards de acceso muestran una sombra suave solamente al pasar el puntero. Las transiciones duran 160–180ms y responden a acciones, sin animaciones de entrada. Se respeta movimiento reducido.

## Shapes

Los controles usan esquinas pequeñas; paneles y cards, medianas; los dos bloques principales de Inicio, grandes. Los iconos son SVG de línea, de una sola familia visual, con trazo 1.7 y tamaño habitual de 20px.

## Components

- Botón principal: verbo y objeto concretos, por ejemplo “Crear pedido” o “Guardar movimiento”. El secundario tiene fondo blanco y borde. Estados de espera deshabilitan el control e indican qué está pasando.
- Campos: etiqueta siempre visible, área de 44px y foco azul. Los errores se muestran cerca del campo; no reemplazar etiquetas con placeholders.
- Cards de acceso: toda la superficie navega a una tarea. Su texto explica para qué sirve; las flechas acompañan y no sustituyen el nombre.
- Etiquetas: tono suave, texto oscuro y descripción de estado. Las tarjetas de pedidos usan una línea superior con el mismo significado.
- Nuevo pedido: pasos enlazados, autocompletado de WhatsApp desplegable y resumen lateral en escritorio. Cada toque en el menú agrega un bloque numerado por unidad, con extras y nota propios. No repetir el botón para agregar dentro de cada bloque. Nombre, cantidades, total y próximo paso se actualizan mientras se completa el formulario.
- Menú e inventario: los listados operativos muestran productos activos; el stock y sus avisos consideran solo ingredientes de hamburguesas activas y adicionales activos disponibles en ellas. Conservar los registros anteriores para el historial, sin mezclarlos con la operación actual.
- Envío: tarifa por 100 metros, distancia expresada en kilómetros con hasta un decimal y ayuda con equivalencias. Si no es gratis, sumar el envío mínimo (importe base) a la tarifa por toda la distancia. No redondear los kilómetros; solo el importe final a pesos. Rechazar más precisión al cargar nuevos pedidos, sin modificar el historial.
- Movimiento de stock: tres elecciones concretas sincronizan el selector existente; conteo pide cantidad real y esconde precio de compra.
- Vacíos: explican qué falta y ofrecen una acción. Una búsqueda sin resultados permite limpiar los filtros.
- Sistema apagado: toda pantalla abierta pasa a escala de grises, sin controles editables ni enlaces operativos. Un aviso accesible explica cómo reabrir; una pérdida de conexión se nombra de forma distinta. Al reabrir, no enviar borradores automáticamente: volver al inicio con datos actuales.
- Borrador de nuevo pedido: guardado automático local por pestaña al modificar campos o unidades. Recuperar datos, extras y notas al volver, recalculando con el menú actual. Mostrar confirmación de guardado y aviso si cambió la disponibilidad. Limpiar solo después de una creación confirmada o un descarte explícito; nunca al enviar un formulario que puede fallar.

## Do's and Don'ts

- Usar los componentes comunes antes de crear un estilo nuevo.
- Explicar el siguiente paso con una frase corta.
- Elegir cards para accesos y tablas para comparar filas.
- Mantener navegación, etiquetas y nombres de acciones coherentes entre pantallas.
- No mostrar cifras ficticias para llenar un panel; los ceros son información real.
- No convertir cada párrafo en una card ni anidar contenedores decorativos.
- No hacer depender el uso del sistema de tipografías o iconos externos.

Verificación: pruebas de Django ejecutadas con Python 3.12, compatible con Django 4.2. El Python 3.14 del entorno original falla al copiar contextos durante la instrumentación de pruebas. La vista previa usa el entorno existente y se verificó en navegador.
