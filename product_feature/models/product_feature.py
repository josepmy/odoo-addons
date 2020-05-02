# Copyright 2019 Fenix Engineering Solutions
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
    _name = 'product_feature.feature'
    _description = 'Product Feature'
    _order = 'code, name'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    code = fields.Char(
        string='Feature Code',
        index=True,
    )
    name = fields.Char(
        string='Feature name',
        required=True,
        translate=True,
    )
    value_type = fields.Selection([
        ('table', "Values table"),
        ('text', "Text value"),
        ('number', "Number value"),
    ],
        string='Type of value',
        required=True,
        default='table',
        help="This selection defines the type of value used for the feature.",
    )
    num_decimals = fields.Integer(
        string='# of decimals',
        default=lambda self: self.env['decimal.precision'].precision_get('Number Feature'),
    )

    table_value_ids = fields.One2many(
        comodel_name='product_feature.table_value',
        inverse_name='feature_id', string='Feature table values')

    _sql_constraints = [
        ('product_feature_uniq_key', 'UNIQUE (company_id, code, name)',
         'You can not have two features with the same code and name!')
    ]


class TableValue(models.Model):
    _name = 'product_feature.table_value'
    _description = 'Product Feature Table Value'
    _order = 'feature_id, id'

    feature_id = fields.Many2one(
        comodel_name='product_feature.feature',
        string='Feature',
        required=True,
    )
    company_id = fields.Many2one(
        related='feature_id.company_id',
        string='Company',
        store=True,
        readonly=True,
    )
    code = fields.Char(
        string='Value Code',
        index=True,
    )
    name = fields.Char(
        string='Value name',
        required=True,
        translate=True,
    )

    _sql_constraints = [
        ('product_feature_table_value_uniq_key', 'UNIQUE (company_id, feature_id, code, name)',
         'You can not have two values with the same code and name in the feature!')
    ]


class ProductFeatureLine(models.Model):
    _name = 'product_feature.feature_line'
    _description = 'Product Feature Line'
    _order = 'template_id, sequence, id'

    template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True,
        ondelete='cascade',
    )
    feature_id = fields.Many2one(
        comodel_name='product_feature.feature',
        string='Feature',
        required=True,
    )
    company_id = fields.Many2one(
        related='feature_id.company_id',
        string='Company',
        store=True,
        readonly=True,
    )
    sequence = fields.Integer(
        'Sequence',
        help="Determine the display order",
    )
    default_text_value = fields.Char(
        'Default Text Value',
        translate=True,
    )
    default_number_value = fields.Float(
        'Default Number Value',
        digits=dp.get_precision('Number Feature'),
    )
    min_number_value = fields.Float(
        'Min. Number Value',
        digits=dp.get_precision('Number Feature'),
    )
    max_number_value = fields.Float(
        'Max. Number Value',
        digits=dp.get_precision('Number Feature'),
    )
    feature_num_decimals = fields.Integer(
        related='feature_id.num_decimals',
        readonly=True,
    )
    feature_value_type = fields.Selection(
        related='feature_id.value_type',
        readonly=True,
    )
    default_table_value_id = fields.Many2one(
        comodel_name='product_feature.table_value',
        string='Default Table Value',
    )
    filtered_table_value_ids = fields.Many2many(
        comodel_name='product_feature.table_value',
        string='Table Values',
        help='If you enter some values here, feature values of this template '
             'variant will be only allowed from this list. Leave empty to '
             'allow any value from feature to be choosen.',
    )

    _sql_constraints = [
        ('product_feature_line_uniq_key', 'UNIQUE (company_id, template_id, feature_id)',
         'You can not have the same feature two times on the template!')
    ]

    @api.multi
    @api.constrains('default_number_value', 'min_number_value', 'max_number_value')
    def _check_default_number_limits(self):
        for line in self:
            if line.min_number_value and line.max_number_value:
                if line.min_number_value > line.max_number_value:
                    raise ValidationError(_('Minimum value can not be lower than maximum value.'))
            if line.default_number_value:
                if line.min_number_value:
                    if line.min_number_value > line.default_number_value:
                        raise ValidationError(_('Default value must not be lower than minimum value.'))
                if line.max_number_value:
                    if line.default_number_value > line.max_number_value:
                        raise ValidationError(_('Default value must not be greater than maximum value.'))
        return True

    @api.onchange('default_number_value', 'min_number_value', 'max_number_value')
    def _onchange_default_number_limits(self):
        self.ensure_one()
        if self.feature_value_type == 'number':
            if self.min_number_value and self.max_number_value:
                if self.min_number_value > self.max_number_value:
                    return {'warning': {
                        'title': _('Value out of limits!'),
                        'message': _('Minimum value can not be lower than maximum value.')
                    }}
            if self.default_number_value:
                if self.min_number_value:
                    if self.min_number_value > self.default_number_value:
                        return {'warning': {
                            'title': _('Value out of limits!'),
                            'message': _('Default value must not be lower than minimum value.')
                        }}
                if self.max_number_value:
                    if self.default_number_value > self.max_number_value:
                        return {'warning': {
                            'title': _('Value out of limits!'),
                            'message': _('Default value must not be greater than maximum value.')
                        }}


class ProductFeatureValue(models.Model):
    _name = 'product_feature.value'
    _description = 'Product Feature Value'
    _order = 'product_id, sequence, id'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        related='product_id.company_id',
        string='Company',
        store=True,
        readonly=True,
    )
    feature_line_id = fields.Many2one(
        comodel_name='product_feature.feature_line',
        string='Feature Line',
        ondelete='cascade',
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
         'UNIQUE (company_id, product_id, feature_id)',
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
