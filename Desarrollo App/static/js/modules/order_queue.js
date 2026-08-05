document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('ordersContainer');
    const searchInput = document.getElementById('searchCliente');
    const filterSelect = document.getElementById('filterEstado');

    function getStatusClass(estado) {
        switch(estado) {
            case 'Pendiente': return 'card-pendiente';
            case 'En preparacion': return 'card-preparacion';
            case 'En camino': return 'card-camino';
            case 'Entregado': return 'card-entregado';
            case 'Cancelado': return 'card-cancelado';
            default: return '';
        }
    }

    function getBadgeClass(estado) {
        switch(estado) {
            case 'Pendiente': return 'badge-pendiente';
            case 'En preparacion': return 'badge-preparacion';
            case 'En camino': return 'badge-camino';
            case 'Entregado': return 'badge-entregado';
            case 'Cancelado': return 'badge-cancelado';
            default: return '';
        }
    }

    function getNextStatus(estado) {
        switch(estado) {
            case 'Pendiente': return 'En preparacion';
            case 'En preparacion': return 'En camino';
            case 'En camino': return 'Entregado';
            default: return null;
        }
    }

    function renderOrders() {
        const filters = {};
        if (filterSelect.value) filters.estado = filterSelect.value;
        if (searchInput.value) filters.cliente = searchInput.value;

        const orders = OrderService.getAll(filters).filter(o =>
            ['Pendiente', 'En preparacion', 'En camino'].includes(o.estado)
        );

        container.innerHTML = '';

        if (orders.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No hay pedidos en la cola.</p></div>';
            return;
        }

        orders.forEach(order => {
            const div = document.createElement('div');
            div.className = `card ${getStatusClass(order.estado)}`;
            div.innerHTML = `
                <div class="order-card">
                    <div class="order-info">
                        <span class="badge ${getBadgeClass(order.estado)}">${order.estado}</span>
                        <h3>${order.cliente.nombre}</h3>
                        <p>${order.productos.map(p => `${p.cantidad} ${p.nombre}`).join(', ')}</p>
                        <p><strong>Total: $${order.total.toLocaleString('es-AR')}</strong></p>
                        <p>${new Date(order.fecha_creacion).toLocaleTimeString('es-AR', {hour: '2-digit', minute:'2-digit'})}</p>
                    </div>
                    <div class="order-actions">
                        <a href="/pedidos/${order.id}/" class="btn btn-info">Ver detalle</a>
                        ${getNextStatus(order.estado) ? `
                            <button class="btn btn-success btn-advance" data-id="${order.id}">
                                Avanzar a ${getNextStatus(order.estado)}
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
            container.appendChild(div);
        });

        document.querySelectorAll('.btn-advance').forEach(btn => {
            btn.addEventListener('click', function() {
                const orderId = parseInt(this.dataset.id);
                const order = OrderService.getById(orderId);
                const nextStatus = getNextStatus(order.estado);
                if (nextStatus) {
                    OrderService.updateStatus(orderId, nextStatus);
                    renderOrders();
                }
            });
        });
    }

    searchInput.addEventListener('input', renderOrders);
    filterSelect.addEventListener('change', renderOrders);

    renderOrders();
});
