document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('historyContainer');
    const searchInput = document.getElementById('searchCliente');
    const filterSelect = document.getElementById('filterEstado');
    const fechaDesde = document.getElementById('fechaDesde');
    const fechaHasta = document.getElementById('fechaHasta');

    function getBadgeClass(estado) {
        switch(estado) {
            case 'Entregado': return 'badge-entregado';
            case 'Cancelado': return 'badge-cancelado';
            default: return '';
        }
    }

    function renderHistory() {
        let orders = OrderService.getFinished();

        if (filterSelect.value) {
            orders = orders.filter(o => o.estado === filterSelect.value);
        }
        if (searchInput.value) {
            const search = searchInput.value.toLowerCase();
            orders = orders.filter(o => o.cliente.nombre.toLowerCase().includes(search));
        }
        if (fechaDesde.value) {
            orders = orders.filter(o => new Date(o.fecha_creacion) >= new Date(fechaDesde.value));
        }
        if (fechaHasta.value) {
            orders = orders.filter(o => new Date(o.fecha_creacion) <= new Date(fechaHasta.value + 'T23:59:59'));
        }

        container.innerHTML = '';

        if (orders.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No hay pedidos en el historial.</p></div>';
            return;
        }

        orders.forEach(order => {
            const div = document.createElement('div');
            div.className = `card ${order.estado === 'Entregado' ? 'card-entregado' : 'card-cancelado'}`;
            div.innerHTML = `
                <div class="order-card">
                    <div class="order-info">
                        <span class="badge ${getBadgeClass(order.estado)}">${order.estado}</span>
                        <h3>#${order.id} - ${order.cliente.nombre}</h3>
                        <p>${order.productos.map(p => `${p.cantidad} ${p.nombre}`).join(', ')}</p>
                        <p><strong>Total: $${order.total.toLocaleString('es-AR')}</strong></p>
                        <p>${new Date(order.fecha_creacion).toLocaleDateString('es-AR')}</p>
                    </div>
                    <div class="order-actions">
                        <a href="/pedidos/${order.id}/" class="btn btn-info">Ver detalle</a>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    }

    searchInput.addEventListener('input', renderHistory);
    filterSelect.addEventListener('change', renderHistory);
    document.getElementById('btnFilter').addEventListener('click', renderHistory);

    renderHistory();
});
