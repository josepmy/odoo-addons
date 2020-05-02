# Copyright 2020 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare

import logging

_logger = logging.getLogger(__name__)


class ProductFeature(models.Model):
    _inherit = 'product_feature.feature'

    is_lot_feature = fields.Boolean(
        string='Lot/serial Feature',
    )

    @api.multi
    def write(self, values):
        """
        Al actualizar, si se ha modificado is_lot_feature,
        verificar que no afecte a valores ya introducidos
        """
        if 'is_lot_feature' in values:
            if any(self.env['product_feature.value'].search(
                    [('feature_id', '=', self.id)])):
                raise ValidationError(
                    'This feature has been already used in products, cannot be switched to lot.')
            if any(self.env['product_feature.lot.value'].search(
                    [('feature_id', '=', self.id)])):
                raise ValidationError(
                    'This feature has been already used in lots, cannot be switched to product.')

        return super(ProductFeature, self).write(values)


class ProductFeatureLine(models.Model):
    _inherit = 'product_feature.feature_line'

    is_lot_feature = fields.Boolean(
        related='feature_id.is_lot_feature',
        readonly=True,
    )


class ProductFeatureValue(models.Model):
    _inherit = 'product_feature.value'

    is_lot_feature = fields.Boolean(
        related='feature_id.is_lot_feature',
        readonly=True,
    )


class ProductFeatureValue(models.Model):
    _name = 'product_feature.lot.value'
    _description = 'Product Feature Lot/Serial Value'
    _order = 'lot_id, sequence, id'

    company_id = fields.Many2one(
        related='feature_id.company_id',
        string='Company',
        store=True,
        readonly=True,
    )
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot/Serial',
        required=True,
        ondelete='cascade',
    )
    feature_line_id = fields.Many2one(
        comodel_name='product_feature.feature_line',
        string='Feature Line',
        ondelete='set null',
    )
    sequence = fields.Integer(
        related='feature_line_id.sequence',
        string='Sequence',
        store=True,
        readonly=True,
        help="Determine the display order",
    )
    feature_id = fields.Many2one(
        comodel_name='product_feature.feature',
        string='Feature',
        required=True,
        ondelete='restrict',
    )
    feature_value_type = fields.Selection(
        related='feature_id.value_type',
        readonly=True,
    )
    text_number_code = fields.Char(
        'Value Code',
        index=True,
    )
    text_value = fields.Char(
        'Text Value',
        translate=True,
    )
    number_value = fields.Float(
        'Number Value',
        digits=dp.get_precision('Number Feature'),
    )
    table_value_id = fields.Many2one(
        comodel_name='product_feature.table_value',
        string='Table Value',
        ondelete='restrict',
    )
    possible_value_ids = fields.Many2many(
        comodel_name='product_feature.table_value',
        compute='_compute_possible_value_ids',
        readonly=True,
    )
    code = fields.Char(
        'Code',
        compute='_compute_code',
        inverse='_set_code',
    )
    value = fields.Char(
        'Value',
        compute='_compute_value',
        inverse='_set_value',
    )

    _sql_constraints = [
        ('product_feature_value_uniq_key',
         'UNIQUE (company_id, lot_id, feature_id)',
         'You can not have more than one value for a feature!')
    ]

    @api.multi
    @api.constrains('number_value')
    def _check_number_limits(self):
        for record in self:
            if record.feature_value_type == 'number':
                if record.feature_line_id and record.feature_line_id.min_number_value:
                    if float_compare(record.feature_line_id.min_number_value,
                                     record.number_value,
                                     precision_digits=record.feature_id.num_decimals) == 1:
                        raise ValidationError(_('Value must not be lower than minimum value.'))
                if record.feature_line_id and record.feature_line_id.max_number_value:
                    if float_compare(record.number_value,
                                     record.feature_line_id.max_number_value,
                                     precision_digits=record.feature_id.num_decimals) == 1:
                        raise ValidationError(_('Value must not be greater than maximum value.'))
        return True

    @api.depends('feature_line_id')
    def _compute_possible_value_ids(self):
        for record in self:
            if record.feature_line_id:
                if record.feature_line_id.filtered_table_value_ids:
                    record.possible_value_ids = record.feature_line_id.filtered_table_value_ids
                else:
                    record.possible_value_ids = record.feature_line_id.feature_id.table_value_ids
            else:
                record.possible_value_ids = False

    @api.depends('feature_id.value_type', 'table_value_id.code', 'text_number_code')
    def _compute_code(self):
        for value in self:
            if value.feature_value_type == 'table':
                value.code = value.table_value_id and value.table_value_id.code or ''
            else:
                value.code = value.text_number_code

    def _set_code(self):
        for value in self:
            if value.feature_value_type == 'table':
                domain = [
                    ('feature_id', '=', value.feature_id.id),
                    ('code', '=', value.code)
                ]
                table_value = self.env['product_feature.table_value'].search(domain, limit=1)
                if table_value:
                    value.table_value_id = table_value
            else:
                value.text_number_code = value.code

    @api.depends('feature_id.value_type', 'table_value_id.name', 'text_value', 'number_value')
    def _compute_value(self):
        for value in self:
            if value.feature_value_type == 'table':
                value.value = value.table_value_id and value.table_value_id.name or ''
            elif value.feature_value_type == 'text':
                value.value = value.text_value
            elif value.feature_value_type == 'number':
                value.value = formatLang(self.env, value.number_value, digits=value.feature_id.num_decimals)

    def _set_value(self):
        def _to_float(val):
            locale = self.env.context.get('lang') or self.env.user.lang or 'en_US'
            lang_obj = self.env['res.lang']._lang_get(locale)
            try:
                return float(str(val).replace(lang_obj.thousands_sep, '').replace(lang_obj.decimal_point, '.'))
            except:
                raise ValidationError(_('Not a valid float: %s' % val))

        for value in self:
            if value.feature_value_type == 'table':
                domain = [
                    ('feature_id', '=', value.feature_id.id),
                    ('name', '=', value.value)
                ]
                table_value = self.env['product_feature.table_value'].search(domain, limit=1)
                if table_value:
                    value.table_value_id = table_value
            elif value.feature_value_type == 'text':
                value.text_value = value.value
            elif value.feature_value_type == 'number':
                float_value = _to_float(value.value)
                if value.feature_line_id and value.feature_line_id.min_number_value:
                    if float_compare(value.feature_line_id.min_number_value,
                                     float_value,
                                     precision_digits=value.feature_id.num_decimals) == 1:
                        raise ValidationError(_(
                            'Value must not be lower than minimum value (%s).' % formatLang(
                                self.env,
                                value.feature_line_id.min_number_value,
                                digits=value.feature_id.num_decimals)))
                if value.feature_line_id and value.feature_line_id.max_number_value:
                    if float_compare(float_value,
                                     value.feature_line_id.max_number_value,
                                     precision_digits=value.feature_id.num_decimals) == 1:
                        raise ValidationError(_(
                            'Value must not be larger than maximum value (%s).' % formatLang(
                                self.env,
                                value.feature_line_id.max_number_value,
                                digits=value.feature_id.num_decimals)))
                value.number_value = float_value

    @api.multi
    @api.depends('feature_id', 'feature_id.name', 'code', 'value')
    def name_get(self):
        return [(rec.id,
                 '%s: %s%s' % (rec.feature_id.name, rec.code and ('[%s] - ' % rec.code) or '', rec.value)
                 ) for rec in self]

    @api.onchange('number_value')
    def _onchange_number_value(self):
        self.ensure_one()
        if self.feature_line_id:
            if self.feature_line_id.min_number_value:
                if float_compare(self.feature_line_id.min_number_value,
                                 self.number_value,
                                 precision_digits=self.feature_id.num_decimals) == 1:
                    return {'warning': {
                        'title': _('Out of limits!'),
                        'message': _(
                            'Value must not be lower than minimum value (%s).' % formatLang(
                                self.env,
                                self.feature_line_id.min_number_value,
                                digits=self.feature_id.num_decimals))
                    }}
            if self.feature_line_id.max_number_value:
                if float_compare(self.number_value,
                                 self.feature_line_id.max_number_value,
                                 precision_digits=self.feature_id.num_decimals) == 1:
                    return {'warning': {
                        'title': _('Out of limits!'),
                        'message': _(
                            'Value must not be larger than maximum value (%s).' % formatLang(
                                self.env,
                                self.feature_line_id.max_number_value,
                                digits=self.feature_id.num_decimals))
                    }}
