# -*- coding: utf-8 -*-
# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Project Task Collaborators",
    'version': "11.0.1.2.8",
    'category': "Project",
    'sequence': 10,
    'summary': "Add collaborators to project task",
    'license': 'AGPL-3',
    'author': "Fenix Engineering Solutions",
    'website': "http://www.fenix-es.com",
    'images': [
        'static/description/cover.png'
    ],
    'depends': ['project', 'hr', ],
    'data': [
        'views/project_inherit.xml',
    ],
    'demo': [
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
