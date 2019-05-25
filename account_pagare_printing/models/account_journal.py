# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.one
    @api.depends('type', 'outbound_payment_method_ids')
    def _compute_pagare_printing_outbound_payment_method_selected(self):
        self.pagare_printing_outbound_payment_method_selected = self.type in ('bank', 'cash') and \
                                                                any(pm.code == 'pagare_printing' for pm in
                                                                    self.outbound_payment_method_ids)

    @api.one
    @api.depends('type', 'inbound_payment_method_ids')
    def _compute_pagare_printing_inbound_payment_method_selected(self):
        self.pagare_printing_inbound_payment_method_selected = self.type in ('bank', 'cash') and \
                                                               any(pm.code == 'pagare_printing' for pm in
                                                                   self.inbound_payment_method_ids)

    @api.one
    @api.depends('pagare_manual_sequencing')
    def _get_pagare_next_number(self):
        if self.pagare_sequence_id:
            self.pagare_next_number = self.pagare_sequence_id.number_next_actual
        else:
            self.pagare_next_number = 1

    @api.one
    def _set_pagare_next_number(self):
        if self.pagare_next_number < self.pagare_sequence_id.number_next_actual:
            raise ValidationError(_("The last pagare number was %s. In order to avoid a pagare being rejected "
                                    "by the bank, you can only use a greater number.") %
                                  self.pagare_sequence_id.number_next_actual)
        if self.pagare_sequence_id:
            self.pagare_sequence_id.sudo().number_next_actual = self.pagare_next_number

    pagare_manual_sequencing = fields.Boolean('Manual Numbering', default=False,
                                              help="Check this option if your pre-printed pagares are not numbered.")
    pagare_sequence_id = fields.Many2one('ir.sequence', 'Pagare Sequence', readonly=True, copy=False,
                                         help="Pagares numbering sequence.")
    pagare_next_number = fields.Integer('Next Pagare Number', compute='_get_pagare_next_number',
                                        inverse='_set_pagare_next_number',
                                        help="Sequence number of the next printed pagare.")
    pagare_printing_outbound_payment_method_selected = fields.Boolean(
        compute='_compute_pagare_printing_outbound_payment_method_selected',
        help="Technical feature used to know whether pagare printing was enabled as outbound payment method.")
    pagare_printing_inbound_payment_method_selected = fields.Boolean(
        compute='_compute_pagare_printing_inbound_payment_method_selected',
        help="Technical feature used to know whether pagare printing was enabled as inbound payment method.")
    pagare_outbound_bridge_account_id = fields.Many2one(comodel_name='account.account',
                                                        string='Outbound Pagare Bridge Account',
                                                        domain=[('deprecated', '=', False)],
                                                        help="Account to move the ammount when the pagare is emitted.",
                                                        oldname="pagare_bridge_account_id")
    pagare_inbound_bridge_account_id = fields.Many2one(comodel_name='account.account',
                                                       string='Inbound Pagare Bridge Account',
                                                       domain=[('deprecated', '=', False)],
                                                       help="Account to move the ammount when the pagare is received.")
    pagare_layout_id = fields.Many2one(comodel_name='account.payment.pagare.report', string="Pagare printing format")

    @api.model
    def create(self, vals):
        rec = super(AccountJournal, self).create(vals)
        if not rec.pagare_sequence_id:
            rec._create_pagare_sequence()
        return rec

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        rec = super(AccountJournal, self).copy(default)
        rec._create_pagare_sequence()
        return rec

    @api.one
    def _create_pagare_sequence(self):
        """ Create a pagare sequence for the journal """
        self.pagare_sequence_id = self.env['ir.sequence'].sudo().create({
            'name': self.name + _(": Pagare Number Sequence"),
            'implementation': 'no_gap',
            'padding': 5,
            'number_increment': 1,
            'company_id': self.company_id.id,
        })

    def _default_outbound_payment_methods(self):
        methods = super(AccountJournal, self)._default_outbound_payment_methods()
        return methods + self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare')

    def _default_inbound_payment_methods(self):
        methods = super(AccountJournal, self)._default_inbound_payment_methods()
        return methods + self.env.ref('account_pagare_printing.account_payment_method_inbound_pagare')

    @api.model
    def _enable_pagare_printing_on_bank_journals(self):
        """ Enables pagare printing payment method and add a pagare sequence on bank journals.
            Called upon module installation via data file.
        """
        pagare_outbound_printing = self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare')
        pagare_inbound_printing = self.env.ref('account_pagare_printing.account_payment_method_inbound_pagare')
        bank_journals = self.search([('type', '=', 'bank')])
        for bank_journal in bank_journals:
            bank_journal._create_pagare_sequence()
            bank_journal.write({
                'outbound_payment_method_ids': [(4, pagare_outbound_printing.id, None)],
                'inbound_payment_method_ids': [(4, pagare_inbound_printing.id, None)],
            })

    @api.multi
    def get_journal_dashboard_datas(self):
        domain_pagares_to_print = [
            ('journal_id', '=', self.id),
            ('payment_type', '=', 'outbound'),
            ('payment_method_id.code', '=', 'pagare_printing'),
            ('state', '=', 'posted')
        ]
        return dict(
            super(AccountJournal, self).get_journal_dashboard_datas(),
            num_pagares_to_print=len(self.env['account.payment'].search(domain_pagares_to_print))
        )

    @api.multi
    def action_pagares_to_print(self):
        return {
            'name': _('Pagares to Print'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form,graph',
            'res_model': 'account.payment',
            'context': dict(
                self.env.context,
                search_default_pagares_to_send=1,
                journal_id=self.id,
                default_journal_id=self.id,
                default_payment_type='outbound',
                default_payment_method_id=self.env.ref('account_pagare_printing.account_payment_method_outbound_pagare').id,
            ),
        }
