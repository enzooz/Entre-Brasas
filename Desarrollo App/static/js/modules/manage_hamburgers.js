document.addEventListener('DOMContentLoaded', function() {
    const tbody = document.getElementById('hamburgersTable');

    function renderHamburgers() {
        const hamburgers = HamburgerService.getAll();
        tbody.innerHTML = '';

        hamburgers.forEach(h => {
            const tr = document.createElement('tr');
            tr.className = h.activa ? '' : 'highlight';
            tr.innerHTML = `
                <td><strong>${h.nombre}</strong></td>
                <td>${h.descripcion}</td>
                <td>$${h.precio_base.toLocaleString('es-AR')}</td>
                <td>${h.incluye_papas ? 'Si' : 'No'}</td>
                <td><span class="badge ${h.activa ? 'badge-entregado' : 'badge-cancelado'}">${h.activa ? 'Activa' : 'Inactiva'}</span></td>
                <td>
                    ${h.activa ? `
                        <a href="/menu/hamburguesas/${h.id}/editar/" class="btn btn-info">Editar</a>
                        <button class="btn btn-danger btn-deactivate" data-id="${h.id}">Desactivar</button>
                    ` : '<span class="badge badge-cancelado">Inactiva</span>'}
                </td>
            `;
            tbody.appendChild(tr);
        });

        document.querySelectorAll('.btn-deactivate').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = parseInt(this.dataset.id);
                if (confirm('Esta seguro de desactivar esta hamburguesa?')) {
                    HamburgerService.deactivate(id);
                    renderHamburgers();
                }
            });
        });
    }

    renderHamburgers();
});
