/* Navegación móvil y tablas compartidas; no altera pedidos ni inventario. */
document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.querySelector('.menu-toggle');
    var scrim = document.querySelector('.nav-scrim');
    var nav = document.getElementById('navegacion');
    var mobile = window.matchMedia('(max-width: 760px)');
    function cambiarMenu(abierto, devolverFoco) {
        document.body.classList.toggle('nav-open', abierto);
        toggle.setAttribute('aria-expanded', String(abierto));
        toggle.setAttribute('aria-label', abierto ? 'Cerrar menú' : 'Abrir menú');
        scrim.hidden = !abierto;
        nav.inert = document.body.classList.contains('system-off') || (mobile.matches && !abierto);
        document.querySelector('.app-main').inert = abierto || document.body.classList.contains('system-off');
        if (abierto) nav.querySelector('a').focus();
        else if (devolverFoco) toggle.focus();
    }
    toggle.addEventListener('click', function () { cambiarMenu(true); });
    scrim.addEventListener('click', function () { cambiarMenu(false, true); });
    document.addEventListener('keydown', function (event) {
        if (!document.body.classList.contains('nav-open')) return;
        if (event.key === 'Escape') cambiarMenu(false, true);
        if (event.key === 'Tab') {
            var links = nav.querySelectorAll('a');
            var first = links[0], last = links[links.length - 1];
            if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
            else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
        }
    });
    mobile.addEventListener('change', function () { cambiarMenu(false); });
    cambiarMenu(false);
    document.querySelectorAll('table').forEach(function (table) {
        if (table.parentElement.classList.contains('table-scroll')) return;
        var wrapper = document.createElement('div');
        wrapper.className = 'table-scroll';
        wrapper.tabIndex = 0;
        wrapper.setAttribute('role', 'region');
        wrapper.setAttribute('aria-label', 'Tabla: desplazá horizontalmente para ver todas las columnas');
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
        if (wrapper.scrollWidth > wrapper.clientWidth) {
            var hint = document.createElement('p');
            hint.className = 'table-hint';
            hint.textContent = 'Deslizá la tabla hacia los costados para ver todas las columnas.';
            wrapper.parentNode.insertBefore(hint, wrapper);
        }
    });
});
