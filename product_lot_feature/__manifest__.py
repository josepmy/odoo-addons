# Copyright 2020 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product Lot/Serial Feature',
    'version': '11.0.1.0.12',
    'category': 'Product',
    'sequence': 10,
    'license': 'AGPL-3',
    'author': 'Fenix Engineering Solutions',
    'website': 'http://www.fenix-es.com',
    'depends': [
        'product_feature',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/product_lot_feature.xml',
        'views/product_inherit.xml',
        'views/stock_production_lot_inherit.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'summary': 'Feature values that go associated with the product lot/serial',
    'description': """
Product Lot/Serial Feature
==========================
Ciertos productos tienen características que no afectan a la definición del 
producto pero que varían por lote/serie.

En este módulo extiende la funcionalidad del módulo product_feature
permitiendo indicar que una característica es de lote y de ese modo
solamente se podrá emplear en productos que tengan control por lote/serie
y su valor en vez de asociarse a product.product, se vincula con 
stock.production.lot
    
""",
}
