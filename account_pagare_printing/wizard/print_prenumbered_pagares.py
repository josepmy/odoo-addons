# -*- coding: utf-8 -*-
# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PrintPreNumberedPagares(models.TransientModel):
    _name = 'print.prenumbered.pagares'
    _description = 'Print Pre-numbered Pagares'

    next_pagare_number = fields.Integer('Next Pagare Number', required=True)

    @api.multi
    def print_pagares(self):
        pagare_number = self.next_pagare_number
        payments = self.env['account.payment'].browse(self.env.context['payment_ids'])
        payments.filtered(lambda r: r.state == 'draft').post()
        payments.filtered(lambda r: r.state not in ('sent', 'cancelled')).write({'state': 'sent'})
        for payment in payments:
            payment.set_pagare_number_from_printing(pagare_number)
            pagare_number += 1
        return payments.do_print_pagares()
