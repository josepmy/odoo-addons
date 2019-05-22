# -*- coding: utf-8 -*-
# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from odoo import api, models
from odoo.tools import float_is_zero
import logging

_logger = logging.getLogger(__name__)


class ReportPagarePrinting(models.AbstractModel):
    _name = 'report.account_pagare_printing.report_pagare_base'

    def fill_stars(self, amount_in_word):
        if amount_in_word and len(amount_in_word) < 170:
            stars = (170 - len(amount_in_word)) // 2
            return ' '.join([amount_in_word, '* ' * stars])
        else:
            return amount_in_word

    @api.multi
    def get_paid_lines(self, payments):
        lines = {}
        for payment in payments:
            lines[payment.id] = []
            for invoice in payment.invoice_ids:
                amount_currency = 0.0
                amount = 0.0
                line = {
                    'date': invoice.date,
                    'date_due': invoice.date_due,
                    'reference': invoice.reference,
                    'number': invoice.number,
                    'amount_total': invoice.amount_total,
                    'paid_amount': 0.0
                }
                if invoice.type == 'out_refund':
                    line['amount_total'] *= -1
                total_amount_to_show = 0.0
                for pay in invoice.payment_move_line_ids:
                    if pay.payment_id == payment:
                        if invoice.type in ('out_invoice', 'in_refund'):
                            for p in pay.matched_debit_ids:
                                if p.credit_move_id == pay:
                                    if p.debit_move_id.invoice_id == invoice:
                                        amount = p.amount
                                        amount_currency = p.amount_currency
                                        payment_currency_id = p.currency_id
                        elif invoice.type in ('in_invoice', 'out_refund'):
                            for p in pay.matched_credit_ids:
                                if p.debit_move_id == pay:
                                    if p.credit_move_id.invoice_id == invoice:
                                        amount = p.amount
                                        amount_currency = p.amount_currency
                                        payment_currency_id = p.currency_id

                        if payment_currency_id and payment_currency_id == \
                                invoice.currency_id:
                            amount_to_show = amount_currency
                        else:
                            amount_to_show = \
                                pay.company_id.currency_id.with_context(
                                    date=pay.date).compute(
                                    amount, invoice.currency_id)
                        if not float_is_zero(
                                amount_to_show,
                                precision_rounding=invoice.currency_id.rounding):
                            total_amount_to_show += amount_to_show
                if invoice.type in ['in_refund', 'out_refund']:
                    total_amount_to_show *= -1
                line['paid_amount'] = total_amount_to_show
                lines[payment.id].append(line)
        return lines

    @api.multi
    def get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model', 'account.payment')
        objects = self.env[model].browse(docids)
        paid_lines = self.get_paid_lines(objects)
        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'docs': objects,
            'time': time,
            'fill_stars': self.fill_stars,
            'paid_lines': paid_lines
        }
        return docargs
