# -*- coding: utf-8 -*-
# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Pagare Payment and Printing',
    'version': "11.0.1.3.10",
    'category': 'Accounting',
    'sequence': 10,
    'summary': 'Pagare payment methods and pagare printing',
    'description': """
This module adds outbound and inbound pagare payment methods. You can also print your emitted pagares.
The pagare settings are located in the accounting journals configuration page.
    """,
    'license': 'AGPL-3',
    'author': "Fenix Engineering Solutions",
    'website': "http://www.fenix-es.com",
    'images': [
        'static/description/cover.png'
    ],
    'depends': ['account', ],
    'data': [
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'data/account_pagare_printing_data.xml',
        'views/account_payment_pagare_report_view.xml',
        'views/report_pagare_base.xml',
        'views/account_journal_views.xml',
        'views/account_payment_views.xml',
        'report/account_pagare_printing_report.xml',
        'wizard/print_prenumbered_pagares_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
