# -*- coding: utf-8 -*-
# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    pagare_due_date = fields.Date(string='Pagare Due Date')
    pagare_amount_in_words = fields.Char(string="Amount in Words")
    pagare_manual_sequencing = fields.Boolean(related='journal_id.pagare_manual_sequencing', readonly=1)
    # Note: a pagare_number == 0 means that it will be attributed when the check is printed
    pagare_number = fields.Integer(string="Pagare Number", readonly=True, copy=False, default=0,
                                   help="Number of the pagare corresponding to this payment. "
                                        "If your pre-printed pagares are not already numbered, "
                                        "you can manage the numbering in the journal configuration page.")

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if hasattr(super(AccountRegisterPayments, self), '_onchange_journal_id'):
            super(AccountRegisterPayments, self)._onchange_journal_id()
        if self.payment_method_id == self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare') \
                and self.journal_id.pagare_manual_sequencing:
            self.pagare_number = self.journal_id.pagare_sequence_id.number_next_actual

    @api.onchange('amount')
    def _onchange_amount(self):
        if hasattr(super(AccountRegisterPayments, self), '_onchange_amount'):
            super(AccountRegisterPayments, self)._onchange_amount()
        if self.payment_method_id == self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare'):
            self.pagare_amount_in_words = self.currency_id.amount_to_text(self.amount)

    def _compute_pagare_due_date(self, invoices):
        date_due = False
        for invoice in invoices:
            if not date_due:
                date_due = invoice.date_due
            elif invoice.date_due < date_due:
                date_due = invoice.date_due
        return date_due

    @api.onchange('payment_method_id')
    def _onchange_payment_method_id(self):
        if self.payment_method_id.code == 'pagare_printing' and not self.multi:
            active_ids = self._context.get('active_ids')
            invoices = self.env['account.invoice'].browse(active_ids)
            self.pagare_due_date = self._compute_pagare_due_date(invoices)
            if self.payment_method_id == self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare'):
                self.pagare_amount_in_words = self.currency_id.amount_to_text(self.amount)

    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPayments, self)._prepare_payment_vals(invoices)
        res.update({
            'pagare_due_date': self.pagare_due_date or self._compute_pagare_due_date(invoices),
        })
        if self.payment_method_id == self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare'):
            res.update({
                'pagare_amount_in_words': self.currency_id.amount_to_text(res['amount']) if self.multi else self.pagare_amount_in_words,
            })
        return res


class AccountPayment(models.Model):
    _inherit = "account.payment"

    state = fields.Selection(selection_add=[('received', 'Received')])
    pagare_due_date = fields.Date(string='Pagare Due Date')
    pagare_amount_in_words = fields.Char(string="Amount in Words")
    pagare_manual_sequencing = fields.Boolean(related='journal_id.pagare_manual_sequencing', readonly=1)
    pagare_number = fields.Integer(string="Pagare Number", readonly=True, copy=False,
                                   help="The selected journal is configured to print pagare numbers. "
                                        "If your pre-printed pagare paper already has numbers "
                                        "or if the current numbering is wrong, you can change it in "
                                        "the journal configuration page.")

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if hasattr(super(AccountPayment, self), '_onchange_journal_id'):
            super(AccountPayment, self)._onchange_journal_id()
        if self.payment_method_id == self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare') \
                and self.journal_id.pagare_manual_sequencing:
            self.pagare_number = self.journal_id.pagare_sequence_id.number_next_actual

    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        res = super(AccountPayment, self)._onchange_amount()
        if self.payment_method_id == self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare'):
            self.pagare_amount_in_words = self.currency_id.amount_to_text(self.amount) if self.currency_id else ''
        return res

    @api.onchange('payment_method_id')
    def _onchange_payment_method_id(self):
        if self.payment_method_id.code == 'pagare_printing':
            date_due = False
            for invoice in self.invoice_ids:
                if not date_due:
                    date_due = invoice.date_due
                elif invoice.date_due < date_due:
                    date_due = invoice.date_due
            self.pagare_due_date = date_due
            if self.payment_method_id == self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare'):
                self.pagare_amount_in_words = self.currency_id.amount_to_text(self.amount)

    @api.model
    def create(self, vals):
        if vals['payment_method_id'] == self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare').id:
            journal = self.env['account.journal'].browse(vals['journal_id'])
            if journal.pagare_manual_sequencing:
                vals.update({'pagare_number': journal.pagare_sequence_id.next_by_id()})
        return super(AccountPayment, self).create(vals)

    @api.multi
    def print_pagares(self):
        """ Check that the recordset is valid, set the payments state to sent and call print_pagares() """
        # Since this method can be called via a client_action_multi, we need to make sure the received records are what we expect
        self = self.filtered(lambda r: r.payment_method_id.code == 'pagare_printing' and
                                       r.payment_type == 'outbound' and
                                       r.state != 'reconciled')

        if len(self) == 0:
            raise UserError(_("Payments to print as a pagare must have 'Emitted Pagare' selected as payment method and "
                              "not have already been reconciled"))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple pagares at once, they must belong to the same bank journal."))

        if not self[0].journal_id.pagare_manual_sequencing:
            # The wizard asks for the number printed on the first pre-printed pagare
            # so payments are attributed the number of the pagare the'll be printed on.
            last_printed_pagare = self.search([
                ('journal_id', '=', self[0].journal_id.id),
                ('pagare_number', '!=', 0)], order="pagare_number desc", limit=1)
            next_pagare_number = last_printed_pagare and last_printed_pagare.pagare_number + 1 or 1
            return {
                'name': _('Print Pre-numbered Pagares'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.pagares',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_pagare_number': next_pagare_number,
                }
            }
        else:
            self.filtered(lambda r: r.state == 'draft').post()
            return self.do_print_pagares()

    def set_pagare_number_from_printing(self, pagare_number):
        self.pagare_number = pagare_number
        account = self.payment_type in (
            'outbound', 'transfer'
        ) and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id
        if self.payment_type == 'outbound':
            self.name = _('Emitted pagare: %d') % pagare_number
            account = self.journal_id.pagare_outbound_bridge_account_id or self.journal_id.account_id
            self.move_line_ids.filtered(lambda m: m.account_id == account).name = self.name
        elif self.payment_type == 'inbound':
            self.name = _('Received pagare: %d') % pagare_number
            account = self.journal_id.pagare_inbound_bridge_account_id or self.journal_id.account_id
            self.move_line_ids.filtered(lambda m: m.account_id == account).name = self.name

    @api.multi
    def unmark_sent(self):
        self.write({'state': 'posted'})

    @api.multi
    def do_print_pagares(self):
        for rec in self:
            if rec.journal_id.pagare_layout_id:
                return self.env['ir.actions.report']._get_report_from_name(
                    rec.journal_id.pagare_layout_id.report
                ).report_action(self)
        raise UserError(_("There is no pagare layout configured.\nMake sure the proper pagare printing module is "
                          "installed and its configuration in the bank journal is correct."))

    def _get_counterpart_move_line_vals(self, invoice=None):
        vals = super(AccountPayment, self)._get_counterpart_move_line_vals(invoice)
        if self.payment_method_id.code == 'pagare_printing':
            vals['date_maturity'] = self.pagare_due_date
        return vals

    def _get_liquidity_move_line_vals(self, amount):
        vals = super(AccountPayment, self)._get_liquidity_move_line_vals(amount)
        if self.payment_method_id.code == 'pagare_printing':
            vals['date_maturity'] = self.pagare_due_date
            if self.payment_type == 'outbound':
                vals['name'] = _('Emitted pagare: %d') % self.pagare_number
                if self.journal_id.pagare_outbound_bridge_account_id:
                    vals['account_id'] = self.journal_id.pagare_outbound_bridge_account_id.id
            elif self.payment_type == 'inbound':
                vals['name'] = _('Received pagare: %d') % self.pagare_number
                if self.journal_id.pagare_inbound_bridge_account_id:
                    vals['account_id'] = self.journal_id.pagare_inbound_bridge_account_id.id
        return vals

    @api.multi
    def post(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))
            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
            # keep the name in case of a payment reset to draft
            if not rec.name:
                if rec.payment_method_id.code == 'pagare_printing':
                    if rec.payment_type == 'outbound':
                        rec.name = _('Emitted pagare: %d') % rec.pagare_number
                    elif rec.payment_type == 'inbound':
                        rec.name = _('Received pagare: %d') % rec.pagare_number

        return super(AccountPayment, self).post()
