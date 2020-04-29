# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
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
        help="This selection defines the type of value used for the "
             "feature.",
    )
    num_decimals = fields.Integer(
        string='# of decimals',
        default=0,
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
    sequence = fields.Integer('Sequence', help="Determine the display order")
    default_text_value = fields.Char('Default Text Value', translate=True)
    default_number_value = fields.Float('Default Number Value')
    min_number_value = fields.Float('Min. Number Value')
    max_number_value = fields.Float('Max. Number Value')
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
    text_number_code = fields.Char('Value Code', index=True)
    text_value = fields.Char('Text Value', translate=True)
    number_value = fields.Float('Number Value')
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
        store=True,
    )
    value = fields.Char(
        'Value',
        compute='_compute_value',
        inverse='_set_value',
        store=True,
    )

    _sql_constraints = [
        ('product_feature_value_uniq_key',
         'UNIQUE (company_id, product_id, feature_id)',
         'You can not have more than one value for a feature!')
    ]

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
                value.code = value.table_value_id and value.table_value_id.code
            else:
                value.code = value.text_number_code

    def _set_code(self):
        for value in self:
            if value.feature_value_type == 'table':
                domain = [
                    ('feature_id', '=', value.feature_id),
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
                value.value = value.table_value_id and value.table_value_id.name
            elif value.feature_value_type == 'text':
                value.value = value.text_value
            elif value.feature_value_type == 'number':
                value.value = value.number_value

    def _set_value(self):
        for value in self:
            if value.feature_value_type == 'table':
                domain = [
                    ('feature_id', '=', value.feature_id),
                    ('name', '=', value.value)
                ]
                table_value = self.env['product_feature.table_value'].search(domain, limit=1)
                if table_value:
                    value.table_value_id = table_value
            elif value.feature_value_type == 'text':
                value.text_value = value.value
            elif value.feature_value_type == 'number':
                value.number_value = value.value
