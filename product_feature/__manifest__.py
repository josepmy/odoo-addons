# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': "Product Feature",
    'version': "11.0.1.0.7",
    'category': "Product",
    'sequence': 10,
    'summary': "Add product features",
    'license': 'AGPL-3',
    'author': "Fenix Engineering Solutions",
    'website': "http://www.fenix-es.com",
    'images': [
        'static/description/cover.png'
    ],
    'depends': ['product', 'stock', 'sale', ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/product_feature.xml',
        'views/product_inherit.xml',
    ],
    'demo': [
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
