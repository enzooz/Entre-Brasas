document.addEventListener('DOMContentLoaded', function() {
    const summarySection = document.getElementById('summarySection');
    const dailySales = document.getElementById('dailySales');
    const paymentMethods = document.getElementById('paymentMethods');
    const topProducts = document.getElementById('topProducts');
    const topAddons = document.getElementById('topAddons');
    const comparison = document.getElementById('comparison');

    function filterOrders() {
        const desde = document.getElementById('fechaDesde').value;
        const hasta = document.getElementById('fechaHasta').value;
        let orders = OrderService.getDelivered();

        if (desde) orders = orders.filter(o => new Date(o.fecha_creacion) >= new Date(desde));
        if (hasta) orders = orders.filter(o => new Date(o.fecha_creacion) <= new Date(hasta + 'T23:59:59'));

        return orders;
    }

    function renderReports() {
        const orders = filterOrders();

        // Summary
        const totalVentas = orders.reduce((sum, o) => sum + o.total, 0);
        const totalEnvios = orders.reduce((sum, o) => sum + o.envio.costo_envio, 0);
        const ticketPromedio = orders.length > 0 ? totalVentas / orders.length : 0;

        summarySection.innerHTML = `
            <div class="summary-card">
                <div class="value">$${totalVentas.toLocaleString('es-AR')}</div>
                <div class="label">Ventas totales</div>
            </div>
            <div class="summary-card">
                <div class="value">${orders.length}</div>
                <div class="label">Pedidos entregados</div>
            </div>
            <div class="summary-card">
                <div class="value">$${ticketPromedio.toLocaleString('es-AR')}</div>
                <div class="label">Ticket promedio</div>
            </div>
            <div class="summary-card">
                <div class="value">$${totalEnvios.toLocaleString('es-AR')}</div>
                <div class="label">Envios cobrados</div>
            </div>
        `;

        // Daily sales
        const dailyMap = {};
        orders.forEach(o => {
            const day = o.fecha_creacion.split('T')[0];
            if (!dailyMap[day]) dailyMap[day] = { total: 0, count: 0 };
            dailyMap[day].total += o.total;
            dailyMap[day].count++;
        });
        let dailyHtml = '<table><tr><th>Fecha</th><th>Total</th><th>Pedidos</th></tr>';
        Object.keys(dailyMap).sort().reverse().forEach(day => {
            dailyHtml += `<tr><td>${day}</td><td>$${dailyMap[day].total.toLocaleString('es-AR')}</td><td>${dailyMap[day].count}</td></tr>`;
        });
        dailyHtml += '</table>';
        dailySales.innerHTML = dailyHtml;

        // Payment methods
        const paymentMap = {};
        orders.forEach(o => {
            if (!paymentMap[o.metodo_pago]) paymentMap[o.metodo_pago] = { total: 0, count: 0 };
            paymentMap[o.metodo_pago].total += o.total;
            paymentMap[o.metodo_pago].count++;
        });
        let paymentHtml = '';
        Object.keys(paymentMap).forEach(method => {
            paymentHtml += `
                <div class="summary-card">
                    <div class="value">$${paymentMap[method].total.toLocaleString('es-AR')}</div>
                    <div class="label">${method} (${paymentMap[method].count} pedidos)</div>
                </div>
            `;
        });
        paymentMethods.innerHTML = paymentHtml || '<div class="empty-state"><p>No hay datos</p></div>';

        // Top products
        const productMap = {};
        orders.forEach(o => {
            o.productos.forEach(p => {
                if (!productMap[p.nombre]) productMap[p.nombre] = { qty: 0, total: 0 };
                productMap[p.nombre].qty += p.cantidad;
                productMap[p.nombre].total += p.precio_base * p.cantidad;
            });
        });
        const sortedProducts = Object.entries(productMap).sort((a, b) => b[1].qty - a[1].qty);
        let prodHtml = '<table><tr><th>#</th><th>Producto</th><th>Vendidos</th><th>Total</th></tr>';
        sortedProducts.slice(0, 5).forEach(([name, data], idx) => {
            prodHtml += `<tr><td>${idx + 1}</td><td><strong>${name}</strong></td><td>${data.qty} uds</td><td>$${data.total.toLocaleString('es-AR')}</td></tr>`;
        });
        prodHtml += '</table>';
        topProducts.innerHTML = prodHtml;

        // Top addons
        const addonMap = {};
        orders.forEach(o => {
            o.productos.forEach(p => {
                p.adicionales.forEach(a => {
                    if (!addonMap[a.nombre]) addonMap[a.nombre] = 0;
                    addonMap[a.nombre] += p.cantidad;
                });
            });
        });
        const sortedAddons = Object.entries(addonMap).sort((a, b) => b[1] - a[1]);
        let addonHtml = '<table><tr><th>#</th><th>Adicional</th><th>Veces solicitado</th></tr>';
        sortedAddons.slice(0, 5).forEach(([name, qty], idx) => {
            addonHtml += `<tr><td>${idx + 1}</td><td><strong>${name}</strong></td><td>${qty}</td></tr>`;
        });
        addonHtml += '</table>';
        topAddons.innerHTML = addonHtml;

        // Comparison
        const allDelivered = OrderService.getDelivered();
        const currentTotal = totalVentas;
        const currentCount = orders.length;
        const prevOrders = allDelivered.filter(o => {
            const f = new Date(o.fecha_creacion);
            return f >= new Date('2026-07-14') && f < new Date('2026-07-21');
        });
        const prevTotal = prevOrders.reduce((sum, o) => sum + o.total, 0);
        const prevCount = prevOrders.length;

        comparison.innerHTML = `
            <table>
                <tr><th>Periodo</th><th>Ventas</th><th>Pedidos</th></tr>
                <tr><td><strong>Actual</strong></td><td>$${currentTotal.toLocaleString('es-AR')}</td><td>${currentCount}</td></tr>
                <tr><td>Anterior</td><td>$${prevTotal.toLocaleString('es-AR')}</td><td>${prevCount}</td></tr>
            </table>
        `;
    }

    document.getElementById('btnFilter').addEventListener('click', renderReports);
    renderReports();
});
