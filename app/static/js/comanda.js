// Copia la comanda de un pedido para pegarla en el WhatsApp de la cocina.
//
// Cada boton "Copiar" tiene un data-comanda con el id del <textarea>
// escondido donde esta el texto. Se usa en el detalle y en la cola.
function copiarComanda(boton) {
    var texto = document.getElementById(boton.dataset.comanda).value;
    var textoOriginal = boton.dataset.textoOriginal || boton.textContent;
    boton.dataset.textoOriginal = textoOriginal;

    function avisar(mensaje) {
        boton.textContent = mensaje;
        setTimeout(function () {
            boton.textContent = textoOriginal;
        }, 2000);
    }

    // Plan B, por si el navegador no deja usar el portapapeles moderno:
    // poner el texto en un campo, seleccionarlo y copiarlo.
    function copiarALaVieja() {
        var campo = document.createElement('textarea');
        campo.value = texto;
        document.body.appendChild(campo);
        campo.select();
        var salioBien = document.execCommand('copy');
        campo.remove();
        avisar(salioBien ? 'Copiado' : 'No se pudo copiar');
    }

    // La forma moderna de copiar. Funciona en 127.0.0.1 y localhost.
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(texto).then(function () {
            avisar('Copiado');
        }, copiarALaVieja);
        return;
    }

    copiarALaVieja();
}
