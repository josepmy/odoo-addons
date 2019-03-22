# -*- coding: utf-8 -*-
# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentPagareReport(models.Model):
    _name = "account.payment.pagare.report"

    name = fields.Char(string='Name', required=True)
    report = fields.Char(string='Report name', required=True)
