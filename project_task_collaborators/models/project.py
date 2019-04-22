# -*- coding: utf-8 -*-
# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    collaborator_ids = fields.Many2many(
        string='Collaborators',
        comodel_name='hr.employee',
        relation='project_task_collaborator_hr_employee_rel',
        column1='task_id', column2='collaborator_hr_employee_id',
        track_visibility='onchange')
