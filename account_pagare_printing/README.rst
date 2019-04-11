.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========================
Pagare Payment and Printing
===========================

Este módulo permite realizar cobros y pagos con pagaré.
Para los pagarés emitidos (pago a proveedores) permite realizar la impresión
del documento de pago en formato bancario prenumerado.

Permite indicar la cuenta puente a emplear, normalmente:

* 401000 para pagos a proveedor
* 431000 para cobros de cliente

Si no se indica una cuenta puente se realizará un asiento contable de
cobro/pago estándar a la cuenta del diario.

Se pueden crear nuevos formatos a través de módulos complementarios y
asignarlos a un diario bancario seleccionando el formato adecuado en la
configuración.


Configuración
=============

En el diario del banco se puede seleccionar el modo de pago y cobro Pagaré
(pagare_printing)

Una vez seleccionado, nos permitirá indicar la cuenta puente para el asiento
y, en el caso de pagarés emitidos, asignar un contador para la numeración
manual de los pagarés. Si no se numeran con el contador, al realizar la
impresión del documento bancario solicitará el número preimpreso en el mismo.


Uso
===

La opción de pago con pagaré estará disponible entre los modos de pago del
diario bancario correspondiente, integrándose con el mecanismo de cobros y
pagos estándar de Odoo.


Incidencias conocidas / Hoja de ruta
====================================

* Implementar la gestión de cobro y del riesgo en los pagarés recibidos


Gestión de errores
==================

Los errores/fallos se gestionan a través de `incidencias de GitHub <https://github.com/fenix-es/odoo-addons/issues>`_.
En caso de problemas, compruebe por favor si su incidencia ha sido ya
reportada. Si fue el primero en descubrirla, ayúdenos a solucionarla suministrando
información detallada de la misma
`aquí <https://github.com/fenix-es/odoo-addons/issues/new?body=module:%20account_pagare_printing%0AVersion:%20...%0A%0A**Pasos%20para%20reproducirlo**%0A-%20...%0A%0A**Comportamiento%20actual**%0A%0A**Comportamiento%20esperado**>`_.


Créditos
========

Contribuidores
--------------

* Fenix Engineering Solutions - Jose F. Fernández

Maintainer
----------

.. image:: https://www.fenix-es.com/logo.png?_22321
   :alt: Fenix Engineering Solutions
   :target: https://www.fenix-es.com

This module is maintained by Fenix Engineering Solutions.

.. image:: https://odoo-community.org/website/image/ir.attachment/32626_5ec4a91/datas
   :alt: OCA Contributor
   :target: https://odoo-community.org

To contribute to this module, please visit the `GitHub page <https://github.com/fenix-es/odoo-addons>`_
and file an issue or pull request.
