
============== 
Amortizaciones
==============

Configuración
=============

Para poder contabilizar activos y su amortización es necesario definir productos 
de tipo Activo y en la pestaña Contabilidad marcar la casilla Depreciable, 
indicando opcionalmente los meses que durará la amortización y estas 4 cuentas 
contables:

 * Cuenta de activo es la cuenta que será utilizada por la factura de proveedor 
 para anotar la compra del activo.
 * Cuenta de amortización es la cuenta donde se anota la depreciación del 
 activo en el haber, y el gasto en el debe de la cuenta de gastos.
 * (opcional) Cuenta de ingresos se utilizará para reflejar los posibles 
ingresos generados por la venta del activo (en función de la depreciación ya 
realizada y el precio de venta).

Por ejemplo:

 * Cuenta de activo: 213000 - Maquinaria
 * Cuenta de amortización: 281300 - Amortización acumulada de maquinaria
 * Cuenta de gastos: 681000 - Amortización del inmovilizado material
 * Cuenta de ingresos: 771000 - Beneficios procedentes del inmovilizado material

El producto sirve solamente para que el sistema pueda obtener en qué cuentas 
contables debe realizar los apuntes. No es necesario, por tanto, crear un nuevo 
producto para cada item que queramos amortizar sinó solamente si queremos 
cambiar alguna de las cuentas que intervienen en la compra, amortización o 
venta.

Per ejemplo, podemos tener un sólo producto “Vehículo” y disponer de varios 
vehículos a amortizar en la empresa, siempre y cuando deseemos que todos 
utilicen la misma cuenta de activo, de amortización, de gastos y de ingresos (en 
caso que la vendamos.

Creación de activos
===================

Para crear un activo debemos ir a la opción Contabilidad -> Activos -> Activos.  
En esta pantalla debemos introducir la información del activo, del que cabe 
destacar la siguiente información:

 * Producto: Producto a amortizar.
 * Diario: Diario contable donde se realizarán los apuntes relacionados con el 
 activo. 
 * Valor: Valor del activo en la fecha inicial de la amortización
 * Valor residual: Valor del activo en la fecha final de la amortización.
 * Fecha de compra: Fecha de cuando se compró el activo
 * Fecha inicial: Fecha en que se realizará el primer apunte de amortización. 
 * Fecha final: Fecha en que se terminará la amortización del activo. Si hemos 
 rellenado el número de meses que durá la amortización del producto, este campo 
 se calculará en función de la fecha inicial, aunque podremos modificarlo a 
 posteriori. 

Para previsualizar las líneas de amortización podemos utilizar el botón *Crear 
Líneas*. Podemos cambiar el método de amortización y la frequencia de 
amortización desde la pestaña *Información adicional*.  Las líneas se pueden 
volver a calcular pulsando el botón *Borrar Lineas* y *Crear Lineas*. 

Una vez finalizado la definición del activo, podemos fijar sus líneas utilizando 
el botón ejecutar. A partir de este momento se fijarán las líneas y sólo se 
podrá modificar el comentario del activo

Creación desde facturas
-----------------------

Si introducimos una línea de factura de proveedor en el campo *Línea de factura 
de proveedor* el programa se encargará de rellenar todos los datos del activo a 
partir de la línea de factura. Los campos que se rellenarán son los siguientes:

 * Fecha de compra: Se utilizará la fecha de la factura.
 * Valor: Se utilizará el importe de la línea de factura
 * Cantidad: Se utilizará el campo cantidad de la línea de factura. 
 * Unidad: Se utilizará la unidad de medida de la línea de factura

Procesar amortizaciones
=======================

Para generar los apuntes correspondientes a las amortizaciones debemos acceder a 
la opción |menu_asset|.

Se nos abrirá un asistente que nos preguntará hasta que fecha queremos crear los 
apuntes. Los apuntes se crearán en estado confirmado. Podemos consultar los 
apuntes creados en las líneas de las amortizaciones. 

Actualización de activos
========================

Para cambiar el valor del activo, el valor residual o la fecha final de la 
amortización debemos seleccionar el activo por el que queremos cambiar y 
utilizar el botón *Actualizar activo*. Se nos abrirá una pestaña donde podremos 
seleccionar los nuevos valores para el activo. Una vez modificados los valores 
se recalcularán las líneas de de amortización con los nuevos valores. 

.. note:: Este proceso no modificará las líneas ya asentadas, sino que sólo 
afectará a las líneas pendientes de amortizar. 


Finalización de activos
=======================

Podemos finalizar la amortización de un activo utilizando el botón Cerrar de la 
pantalla de activos. Antes de finalizar un activo debemos asegurarnos de haber 
generado todos los apuntes de amortización pendiente ya que este proceso 
eliminará todas las líneas que no hayan sido asentadas, y generará un apunte 
reflejando el cierre del mismo. 

Venta de activos
================

La venta de un activo implica la finalización del mismo. Podemos registrar la 
venta de un activo directamente desde una factura de cliente. Para ello debemos 
seleccionar el producto del activo y nos aparecerá un nuevo campo llamado 
activo. En este campo debemos seleccionar el activo a vender. Una vez confirmada 
la factura de venta, se finalizará el activo. 

.. |menu_asset| tryref:: ir.menu_account_asset/complete_name


