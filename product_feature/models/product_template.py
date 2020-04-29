# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_feature_line_ids = fields.One2many(
        comodel_name='product_feature.feature_line',
        inverse_name='template_id', string='Features')

    @api.model
    def create(self, vals):
        """
        Al crear, si se ha creado variante, creamos sus product feature values
        """
        _logger.debug('---> Product Template create()')
        template = super(ProductTemplate, self).create(vals)
        if len(template.product_feature_line_ids) > 0 \
                and len(template.product_variant_ids) > 0:
            template.create_product_feature_value_ids()

    @api.multi
    def write(self, values):
        """
        Al actualizar, si se ha modificado product_feature_line_ids,
        actualizamos product feature values de las variantes
        """
        _logger.debug('---> Product Template write()')
        res = super(ProductTemplate, self).write(values)
        if 'product_feature_line_ids' in values:
            self.create_product_feature_value_ids()
        return res

    @api.multi
    def create_product_feature_value_ids(self):
        _logger.debug('---> create_product_feature_value_ids()')
        for template in self:
            for variant in template.product_variant_ids:
                _logger.warning('variant: [%s] %s', variant.code, variant.name)
                for feature_line in template.product_feature_line_ids:
                    _logger.warning('feature_line: %s', feature_line.feature_id.name)

