# Copyright 2020 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _create_product_feature_values(self):
        """
        Crear los valores de características en el producto en función
        de las que están definidas en la plantilla.
        Al quitar características de la plantilla se borran los valores
        en el producto automáticamente (cascade).

        Se filtran las que son de lote, esas no se añaden al producto
        """
        for template in self:
            for variant in template.product_variant_ids:
                values_to_add = \
                    template.product_feature_line_ids.filtered(
                        lambda x: not x.is_lot_feature).mapped(
                        'feature_id') - variant.product_feature_value_ids.mapped(
                        'feature_id')
                for value in values_to_add:
                    line = template.product_feature_line_ids.filtered(
                        lambda x: x.feature_id == value)
                    vals = {
                        'product_id': variant.id,
                        'feature_line_id': line.id,
                        'feature_id': line.feature_id.id,
                    }
                    if line.feature_value_type == 'table' and line.default_table_value_id:
                        vals['table_value_id'] = line.default_table_value_id.id
                    elif line.feature_value_type == 'text' and line.default_text_value:
                        vals['text_value'] = line.default_text_value
                    elif line.feature_value_type == 'number' and line.default_number_value:
                        vals['number_value'] = line.default_number_value
                    self.env['product_feature.value'].create(vals)
