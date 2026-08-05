document.addEventListener('DOMContentLoaded', function() {
    const order = OrderService.getById(ORDER_ID);
    if (!order) {
        document.getElementById('orderDetail').innerHTML = '<div class="empty-state"><p>Pedido no encontrado.</p></div>';
        return;
    }

    document.getElementById('orderId').textContent = order.id;

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

    const statusEl = document.getElementById('currentStatus');
    statusEl.textContent = order.estado;
    statusEl.className = `badge ${getBadgeClass(order.estado)}`;

    // Render order detail
    let html = `
        <h2>Datos del Cliente</h2>
        <p><strong>Nombre:</strong> ${order.cliente.nombre}</p>
        <p><strong>Telefono:</strong> ${order.cliente.telefono}</p>
        <p><strong>Direccion:</strong> ${order.cliente.direccion}</p>
        ${order.observaciones ? `<p><strong>Observaciones:</strong> ${order.observaciones}</p>` : ''}

        <h2>Productos</h2>
        <table>
            <tr><th>#</th><th>Producto</th><th>Cant</th><th>Precio</th><th>Subtotal</th></tr>
    `;

    let subtotalProductos = 0;
    let subtotalAdicionales = 0;

    order.productos.forEach((prod, idx) => {
        const prodSubtotal = prod.precio_base * prod.cantidad;
        subtotalProductos += prodSubtotal;
        html += `<tr>
            <td>${idx + 1}</td>
            <td>${prod.nombre}</td>
            <td>${prod.cantidad}</td>
            <td>$${prod.precio_base.toLocaleString('es-AR')}</td>
            <td>$${prodSubtotal.toLocaleString('es-AR')}</td>
        </tr>`;

        prod.adicionales.forEach(adic => {
            const adicSubtotal = adic.precio * prod.cantidad;
            subtotalAdicionales += adicSubtotal;
            html += `<tr>
                <td></td>
                <td style="padding-left:30px;">${adic.nombre}</td>
                <td>${prod.cantidad}</td>
                <td>$${adic.precio.toLocaleString('es-AR')}</td>
                <td>$${adicSubtotal.toLocaleString('es-AR')}</td>
            </tr>`;
        });
    });

    html += `</table>

        <div class="cost-summary">
            <p>Productos: $${subtotalProductos.toLocaleString('es-AR')}</p>
            <p>Adicionales: $${subtotalAdicionales.toLocaleString('es-AR')}</p>
            <p>Envio: $${order.envio.costo_envio.toLocaleString('es-AR')}</p>
            <p class="total-highlight">TOTAL: $${order.total.toLocaleString('es-AR')}</p>
            <p>Metodo de pago: ${order.metodo_pago}</p>
        </div>
    `;

    document.getElementById('orderDetail').innerHTML = html;

    // Render history
    let historyHtml = '<table><tr><th>Fecha</th><th>Estado</th><th>Observacion</th></tr>';
    order.historial.forEach(h => {
        const fecha = new Date(h.fecha);
        historyHtml += `<tr>
            <td>${fecha.toLocaleDateString('es-AR')} ${fecha.toLocaleTimeString('es-AR', {hour: '2-digit', minute:'2-digit'})}</td>
            <td><span class="badge ${getBadgeClass(h.estado)}">${h.estado}</span></td>
            <td>${h.observacion || '-'}</td>
        </tr>`;
    });
    historyHtml += '</table>';
    document.getElementById('historyList').innerHTML = historyHtml;

    // Status actions
    const isFinished = ['Entregado', 'Cancelado'].includes(order.estado);
    document.getElementById('statusSection').style.display = isFinished ? 'none' : 'block';

    document.getElementById('btnAdvance').addEventListener('click', function() {
        let nextStatus = '';
        switch(order.estado) {
            case 'Pendiente': nextStatus = 'En preparacion'; break;
            case 'En preparacion': nextStatus = 'En camino'; break;
            case 'En camino': nextStatus = 'Entregado'; break;
        }
        if (nextStatus) {
            OrderService.updateStatus(order.id, nextStatus, document.getElementById('observation').value);
            window.location.reload();
        }
    });

    document.getElementById('btnCancel').addEventListener('click', function() {
        if (order.estado === 'Pendiente') {
            OrderService.cancel(order.id, document.getElementById('observation').value);
            window.location.reload();
        } else {
            document.getElementById('cancelModal').style.display = 'flex';
        }
    });

    document.getElementById('btnReturnStock').addEventListener('click', function() {
        order.productos.forEach(prod => {
            const recipe = RecipeService.getRecipe(prod.hamburguesa_id);
            recipe.forEach(item => {
                InventoryService.addAutomaticEntry(
                    item.ingrediente_id,
                    item.cantidad * prod.cantidad,
                    `Cancelacion de pedido N° ${order.id}`
                );
            });
        });
        OrderService.cancel(order.id, document.getElementById('observation').value + ' - Stock devuelto');
        window.location.href = '/pedidos/cola/';
    });

    document.getElementById('btnNoReturn').addEventListener('click', function() {
        OrderService.cancel(order.id, document.getElementById('observation').value + ' - Stock como perdida');
        window.location.href = '/pedidos/cola/';
    });
});
