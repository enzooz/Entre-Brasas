document.addEventListener('DOMContentLoaded', function() {
    const tbody = document.getElementById('addonsTable');

    function renderAddons() {
        const addons = AddonService.getAll();
        tbody.innerHTML = '';

        addons.forEach(a => {
            const nombres = a.productos_ids.map(id => {
                const h = HamburgerService.getById(id);
                return h ? h.nombre : '';
            }).filter(n => n).join(', ');

            const tr = document.createElement('tr');
            tr.className = a.activo ? '' : 'highlight';
            tr.innerHTML = `
                <td><strong>${a.nombre}</strong></td>
                <td>$${a.precio.toLocaleString('es-AR')}</td>
                <td>${nombres}</td>
                <td><span class="badge ${a.activo ? 'badge-entregado' : 'badge-cancelado'}">${a.activo ? 'Activo' : 'Inactivo'}</span></td>
                <td>
                    ${a.activo ? `
                        <a href="/menu/adicionales/${a.id}/editar/" class="btn btn-info">Editar</a>
                        <button class="btn btn-danger btn-deactivate" data-id="${a.id}">Desactivar</button>
                    ` : '<span class="badge badge-cancelado">Inactivo</span>'}
                </td>
            `;
            tbody.appendChild(tr);
        });

        document.querySelectorAll('.btn-deactivate').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = parseInt(this.dataset.id);
                if (confirm('Esta seguro de desactivar este adicional?')) {
                    AddonService.deactivate(id);
                    renderAddons();
                }
            });
        });
    }

    renderAddons();
});
