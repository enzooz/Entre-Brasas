# Pruebas

Las pruebas de JavaScript están juntas en `javascript/`, separadas del código
Python de las aplicaciones. Ejecutan los controladores con Node.js y dobles del
DOM; no reemplazan una prueba visual en un navegador real.

Desde `app/`:

```powershell
node --test tests/javascript/*.cjs
```

Cubren borradores, clientes, envío, mapas, pasos del formulario y estado del
sistema. No requieren instalar paquetes npm ni crear pedidos reales.

Las pruebas Python permanecen junto a cada aplicación (`tests.py`,
`tests_clientes.py`, `tests_mapas.py` y `test_servidor_local.py`), donde Django
las descubre. Con el entorno virtual activado, desde `app/`:

```powershell
python manage.py test
```

La prueba aislada del instalador sigue en
`entre_brasas/probar_instalacion.py`; su ejecución está explicada en el README
principal y requiere Windows e internet. No forma parte del comando Node.
