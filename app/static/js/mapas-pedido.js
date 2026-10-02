/* Mapa opcional. La clave y las consultas al proveedor quedan en Django. */
document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('formPedido');
    if (!form || typeof DATOS === 'undefined' || !DATOS.mapas) return;
    var config = DATOS.mapas;
    var address = document.getElementById('clienteDireccion');
    var distance = document.getElementById('distancia');
    var saved = document.getElementById('ubicacionPedido');
    var search = document.getElementById('buscarDireccion');
    var results = document.getElementById('resultadosDirecciones');
    var status = document.getElementById('estadoMapa');
    var detail = document.getElementById('detalleRecorrido');
    var toggle = document.getElementById('mostrarMapa');
    var panel = document.getElementById('panelMapa');
    var script = document.querySelector('script[data-route-url]');
    var map = null, marker = null, routeLayer = null, location = null;
    var controller = null, sequence = 0, busy = false, queryAddress = null;
    var lastAddress = address.value;

    function validGeometry(geometry) {
        if (!geometry) return true;
        if (geometry.type !== 'MultiLineString' || !Array.isArray(geometry.coordinates)
            || !geometry.coordinates.length) return false;
        var count = 0;
        return geometry.coordinates.every(function (line) {
            if (!Array.isArray(line) || line.length < 2 || (count += line.length) > 10000) return false;
            return line.every(function (point) { return Array.isArray(point) && point.length >= 2
                && Number.isFinite(point[0]) && Math.abs(point[0]) <= 180
                && Number.isFinite(point[1]) && Math.abs(point[1]) <= 90; });
        });
    }

    function delivery() { return !!form.querySelector('input[name="retiro_local"][value="false"]:checked'); }
    function off() { return document.body.classList.contains('system-off'); }
    function message(text, error) {
        status.textContent = text;
        status.classList.toggle('is-error', !!error);
    }
    function loading(value, text) {
        busy = value;
        if (off()) return;
        search.disabled = value || !config.habilitado;
        search.textContent = value ? (text || 'Consultando…') : 'Buscar dirección';
        results.setAttribute('aria-busy', String(value));
        results.querySelectorAll('button').forEach(function (button) { button.disabled = value; });
    }
    function cancel() {
        sequence++;
        if (controller) controller.abort();
        controller = null;
        queryAddress = null;
        loading(false);
    }
    function persist() {
        saved.value = location ? JSON.stringify(location) : '';
        document.dispatchEvent(new Event('pedido:actualizado'));
    }
    function eraseRoute() {
        if (map && routeLayer) map.removeLayer(routeLayer);
        routeLayer = null;
        detail.hidden = true;
        detail.textContent = '';
    }
    function clearLocation() {
        var calculated = location && location.km === distance.value;
        cancel();
        eraseRoute();
        if (map && marker) map.removeLayer(marker);
        marker = null;
        location = null;
        saved.value = '';
        results.replaceChildren();
        results.hidden = true;
        if (calculated) {
            distance.value = '';
            calcularTotal();
        }
    }
    function initMap() {
        if (map) { map.invalidateSize(); return true; }
        if (!window.L) {
            message('No se pudo abrir el mapa. Podés buscar la dirección y cargar los kilómetros manualmente.', true);
            return false;
        }
        map = L.map('mapaPedido', {scrollWheelZoom: false, minZoom: 10, maxZoom: 19,
            maxBounds: [[-27.95, -59.55], [-26.95, -58.35]], maxBoundsViscosity: 1}).setView(config.origen, 14);
        // Posicionar antes de agregar mosaicos: no descargar una vista que
        // inmediatamente se reemplaza por el recorrido recuperado del borrador.
        if (location) {
            var bounds = location.geometria ? L.geoJSON(location.geometria).getBounds()
                : [config.origen, [location.latitud, location.longitud]];
            map.fitBounds(bounds, {padding: [20, 20], maxZoom: 16, animate: false});
        }
        var tiles = L.tileLayer(config.tile_url, {minZoom: 10, maxZoom: 19, attribution: '', updateWhenIdle: true, keepBuffer: 0}).addTo(map);
        // Atribución configurable insertada como texto, nunca como HTML externo.
        var attribution = document.createElement('span');
        attribution.textContent = config.tile_attribution;
        var osm = document.createElement('a');
        osm.href = 'https://www.openstreetmap.org/copyright';
        osm.target = '_blank'; osm.rel = 'noopener';
        osm.textContent = 'OpenStreetMap';
        attribution.appendChild(document.createTextNode(' · ')); attribution.appendChild(osm);
        var provider = document.createElement('a');
        provider.href = 'https://www.geoapify.com/'; provider.target = '_blank'; provider.rel = 'noopener'; provider.textContent = 'Geoapify';
        attribution.appendChild(document.createTextNode(' · ')); attribution.appendChild(provider);
        map.attributionControl.getContainer().appendChild(attribution);
        tiles.on('tileerror', function () {
            var warning = document.getElementById('estadoMosaicos');
            warning.classList.add('is-error');
            warning.textContent = 'No se pudo cargar parte del mapa. El cálculo y la distancia manual siguen disponibles.';
        });
        L.circleMarker(config.origen, {radius: 8, color: '#102349', fillOpacity: 1, fillColor: '#102349'})
            .addTo(map).bindTooltip('Local · punto de salida configurado');
        map.on('click', function (event) {
            if (!config.habilitado || off() || !delivery()) return;
            var label = address.value.trim() || 'Punto en el mapa, Resistencia';
            choose({direccion: label, latitud: event.latlng.lat, longitud: event.latlng.lng, aproximada: true});
        });
        return true;
    }
    function showMap() {
        panel.hidden = false;
        toggle.setAttribute('aria-expanded', 'true');
        toggle.textContent = 'Ocultar mapa';
        return initMap();
    }
    function draw() {
        if (!map || !location) return;
        if (marker) map.removeLayer(marker);
        marker = L.marker([location.latitud, location.longitud], {
            draggable: true, title: 'Destino: arrastrá para ajustar',
            icon: L.divIcon({className: 'map-destination-pin', iconSize: [22, 22], iconAnchor: [11, 11]}),
        }).addTo(map).bindTooltip('Destino · verificá el punto de entrega');
        marker.on('dragend', function () {
            if (off() || !delivery()) return;
            var point = marker.getLatLng();
            choose({direccion: address.value, latitud: point.lat, longitud: point.lng, aproximada: true});
        });
        eraseRoute();
        if (location.geometria) {
            routeLayer = L.geoJSON(location.geometria, {style: {color: '#2455d6', weight: 4}}).addTo(map);
            map.fitBounds(routeLayer.getBounds(), {padding: [20, 20], maxZoom: 16, animate: false});
        } else {
            map.fitBounds([config.origen, [location.latitud, location.longitud]], {padding: [20, 20], maxZoom: 16, animate: false});
        }
        showDetail();
    }
    function showDetail() {
        detail.hidden = !location || !location.km || location.km !== distance.value;
        if (!detail.hidden) detail.textContent = 'Recorrido: ' + Number(location.metros).toLocaleString('es-AR', {maximumFractionDigits: 0})
            + ' metros → ' + location.km.replace('.', ',') + ' km para el envío.';
    }
    async function request(url, data, token) {
        controller = new AbortController();
        var currentController = controller;
        var timeout = window.setTimeout(function () { currentController.abort(); }, 18000);
        try {
            var response = await fetch(url, {
                method: 'POST', credentials: 'same-origin', cache: 'no-store',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': form.querySelector('[name="csrfmiddlewaretoken"]').value},
                body: JSON.stringify(data), signal: currentController.signal,
            });
            var payload;
            try { payload = await response.json(); } catch (error) { throw new Error('No se pudo consultar el mapa. Ingresá kilómetros manualmente.'); }
            if (!response.ok) throw new Error(payload.error || 'Servicio no disponible. Ingresá kilómetros manualmente.');
            if (token !== sequence || off() || !delivery()) return null;
            return payload;
        } finally { window.clearTimeout(timeout); }
    }
    async function find() {
        if (!config.habilitado || busy || off() || !delivery()) return;
        var text = address.value.trim();
        if (text.length < 3 || text.indexOf('://') !== -1) {
            message('Escribí calle y altura o un lugar. Para un enlace de Maps, usá distancia manual.', true); address.focus(); return;
        }
        cancel();
        var token = sequence;
        queryAddress = address.value;
        loading(true, 'Buscando…'); message('Buscando en Resistencia y alrededores…');
        results.replaceChildren(); results.hidden = true;
        try {
            var data = await request(search.dataset.url, {texto: text}, token);
            if (!data) return;
            if (!Array.isArray(data.resultados)) throw new Error('No llegó una respuesta válida. Probá de nuevo o cargá kilómetros manualmente.');
            data.resultados.forEach(function (result) {
                var button = document.createElement('button');
                button.type = 'button'; button.className = 'btn btn-secondary';
                button.textContent = result.direccion;
                var note = document.createElement('small');
                note.textContent = result.aproximada ? 'Punto aproximado: comprobá la altura en el mapa.' : 'Elegir dirección y calcular recorrido';
                button.appendChild(note);
                button.addEventListener('click', function () { choose(result); });
                results.appendChild(button);
            });
            results.hidden = !data.resultados.length;
            message(data.resultados.length ? 'Elegí una dirección para calcular el recorrido.' : 'No encontramos esa dirección. Probá calle y altura con la localidad, o ingresá kilómetros manualmente.');
        } catch (error) {
            if (token === sequence && !off()) message(error.name === 'AbortError' ? 'La consulta tardó demasiado. Podés cargar kilómetros manualmente.' : error.message, true);
        } finally { if (token === sequence) { queryAddress = null; loading(false); } }
    }
    async function choose(result) {
        if (!config.habilitado || off() || !delivery()) return;
        cancel();
        var token = sequence;
        eraseRoute();
        address.value = result.direccion;
        lastAddress = address.value;
        address.focus({preventScroll: true});
        distance.value = ''; // Una distancia anterior nunca se aplica al nuevo destino.
        location = {direccion: address.value, latitud: result.latitud, longitud: result.longitud, origen: config.origen};
        results.replaceChildren(); results.hidden = true;
        mostrarLinkMaps(); calcularTotal(); persist();
        showMap(); draw();
        queryAddress = address.value;
        loading(true, 'Calculando…'); message('Calculando recorrido por calles desde el local…');
        try {
            var data = await request(script.dataset.routeUrl, {latitud: result.latitud, longitud: result.longitud}, token);
            if (!data) return;
            if (typeof data.distancia_km !== 'string' || !/^\d{1,3}\.\d$/.test(data.distancia_km)
                || !Number.isFinite(data.distancia_metros) || data.distancia_metros < 0
                || !data.geometria || !validGeometry(data.geometria)) throw new Error('El recorrido no llegó en kilómetros y metros válidos. Ingresá la distancia manualmente.');
            distance.value = data.distancia_km;
            location.km = data.distancia_km; location.metros = data.distancia_metros; location.geometria = data.geometria;
            draw(); showDetail(); calcularTotal(); persist();
            message(result.aproximada ? 'Destino aproximado. Verificá el punto; tocá el mapa o arrastrá el destino para corregirlo.' : 'Recorrido calculado. Verificá el punto de entrega antes de crear el pedido.');
        } catch (error) {
            if (token === sequence && !off()) message(error.name === 'AbortError' ? 'No llegó el recorrido a tiempo. Ingresá kilómetros manualmente.' : error.message, true);
        } finally { if (token === sequence) { queryAddress = null; loading(false); } }
    }
    function changed() {
        if (off()) { cancel(); return; }
        if (address.value !== lastAddress || (queryAddress !== null && address.value !== queryAddress)) {
            lastAddress = address.value;
            clearLocation(); message('Dirección modificada. Buscala de nuevo o ingresá kilómetros manualmente.');
        }
        if (!delivery() && busy) cancel();
        if (location && location.km && distance.value !== location.km) {
            location.km = null; location.metros = null; eraseRoute(); saved.value = JSON.stringify(location);
            message('Distancia editada manualmente. El envío usa los kilómetros que ingresaste.');
        }
    }
    search.addEventListener('click', find);
    address.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') { event.preventDefault(); find(); }
    });
    address.addEventListener('input', changed);
    distance.addEventListener('input', function () {
        if (busy) cancel();
        changed();
        document.dispatchEvent(new Event('pedido:actualizado'));
    });
    form.addEventListener('change', changed);
    form.addEventListener('submit', function (event) {
        if (busy) { event.preventDefault(); message('Esperá el recorrido o ingresá la distancia por teclado para continuar.'); }
    });
    document.addEventListener('pedido:actualizado', changed);
    document.addEventListener('pedido:borrador-descartado', function () { clearLocation(); lastAddress = address.value; message(''); });
    toggle.addEventListener('click', function () {
        if (panel.hidden) { if (showMap()) draw(); }
        else { panel.hidden = true; toggle.setAttribute('aria-expanded', 'false'); toggle.textContent = 'Mostrar mapa'; }
    });
    new MutationObserver(function () { if (!panel.hidden && map) map.invalidateSize(); })
        .observe(document.getElementById('paso-entrega'), {attributes: true, attributeFilter: ['hidden']});
    new MutationObserver(function () { if (off()) cancel(); }).observe(document.body, {attributes: true, attributeFilter: ['class']});
    window.addEventListener('pagehide', cancel);
    try {
        var restored = saved.value ? JSON.parse(saved.value) : null;
        if (restored && saved.value.length <= 500000 && Number.isFinite(restored.latitud) && Math.abs(restored.latitud) <= 90
            && Number.isFinite(restored.longitud) && Math.abs(restored.longitud) <= 180 && validGeometry(restored.geometria)
            && (!restored.km || (typeof restored.km === 'string' && /^\d{1,3}\.\d$/.test(restored.km)
                && Number.isFinite(restored.metros) && restored.metros >= 0))
            && restored.direccion === address.value && JSON.stringify(restored.origen) === JSON.stringify(config.origen)) {
            location = restored; showDetail();
        } else if (restored) {
            if (restored.km === distance.value) { distance.value = ''; calcularTotal(); }
            saved.value = ''; message('Cambió el punto de salida o la dirección. Calculá nuevamente el recorrido.', true);
        }
    } catch (error) { saved.value = ''; }
});
