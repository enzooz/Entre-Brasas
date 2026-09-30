/* Todas las pantallas quedan sin interacción cuando se cierra el servidor. */
document.addEventListener('DOMContentLoaded', function () {
    var body = document.body;
    var instance = body.dataset.systemInstance;
    var notice = document.getElementById('system-off-notice');
    var title = document.getElementById('system-off-title');
    var message = document.getElementById('system-off-message');
    var reconnect = document.getElementById('system-reconnect');
    var key = 'entre-brasas-apagado';
    var locked = false;
    var confirmedOff = false;
    var checking = false;
    var reachable = false;

    function lock(confirmed) {
        confirmedOff = confirmedOff || confirmed;
        var first = !locked;
        locked = true;
        reachable = false;
        reconnect.disabled = true;
        reconnect.textContent = 'Esperando que abras el sistema…';
        body.classList.add('system-off');
        body.classList.remove('nav-open');
        document.querySelector('.nav-scrim').hidden = true;
        document.querySelector('.menu-toggle').setAttribute('aria-expanded', 'false');
        document.querySelector('.sidebar').inert = true;
        document.querySelector('.app-main').inert = true;
        document.querySelector('.skip-link').inert = true;
        document.querySelectorAll('.app-main input, .app-main textarea, .app-main select, .app-main button').forEach(function (control) {
            control.disabled = true;
        });
        notice.hidden = false;
        title.textContent = confirmedOff ? 'Sistema apagado' : 'Sistema sin conexión';
        message.textContent = confirmedOff
            ? 'Las pantallas están bloqueadas. Los datos guardados se conservan. Para volver a trabajar, abrí Entre Brasas desde el icono del escritorio.'
            : 'No podemos conectar con Entre Brasas. Las pantallas están bloqueadas para evitar cambios que no se puedan guardar. Comprobá que el sistema esté abierto.';
        if (first) notice.focus();
    }

    function broadcastOff() {
        try { window.localStorage.setItem(key, instance); } catch (error) { /* Sigue funcionando sin almacenamiento. */ }
        lock(true);
    }

    function blockInteraction(event) {
        if (locked && !notice.contains(event.target)) {
            event.preventDefault();
            event.stopImmediatePropagation();
        }
    }
    ['click', 'submit', 'keydown', 'beforeinput', 'change'].forEach(function (type) {
        document.addEventListener(type, blockInteraction, true);
    });

    async function check() {
        if (checking) return;
        checking = true;
        var controller = new AbortController();
        var timeout = window.setTimeout(function () { controller.abort(); }, 2500);
        try {
            var response = await fetch(body.dataset.systemStatusUrl, {cache: 'no-store', signal: controller.signal});
            if (!response.ok) throw new Error('Estado no disponible');
            var state = await response.json();
            if (typeof state.instancia !== 'string' || typeof state.apagando !== 'boolean') throw new Error('Estado inválido');
            if (state.apagando && state.instancia === instance) broadcastOff();
            else if (state.instancia !== instance) lock(true);
            // Una respuesta vieja de esta ejecución no habilita la reapertura.
            reachable = !state.apagando && (!confirmedOff || state.instancia !== instance);
            if (locked && reachable) {
                message.textContent = 'Entre Brasas ya está disponible. Esta pantalla quedó bloqueada: volvé al inicio para cargar los datos actuales. Los cambios sin guardar no se enviaron.';
            }
        } catch (error) {
            reachable = false;
            lock(false);
        } finally {
            window.clearTimeout(timeout);
            checking = false;
            reconnect.disabled = !reachable;
            reconnect.textContent = reachable ? 'Volver al inicio' : 'Esperando que abras el sistema…';
        }
    }

    reconnect.addEventListener('click', function () { if (reachable) window.location.assign('/'); });
    window.addEventListener('storage', function (event) {
        if (event.key === key && event.newValue === instance) broadcastOff();
    });
    window.addEventListener('pageshow', check);
    window.addEventListener('focus', check);
    document.addEventListener('visibilitychange', function () { if (!document.hidden) check(); });
    if (body.dataset.systemOff === 'true') broadcastOff();
    try { if (window.localStorage.getItem(key) === instance) lock(true); } catch (error) { /* Verificamos por red. */ }
    check();
    window.setInterval(check, 1500);
});
