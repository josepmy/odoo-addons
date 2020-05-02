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
        inverse_name='template_id',
        string='Features',
    )

    @api.model
    def create(self, vals):
        """
        Al crear, si se ha creado variante, creamos sus product feature values
        """
        template = super(ProductTemplate, self).create(vals)
        if len(template.product_feature_line_ids) > 0 \
                and len(template.product_variant_ids) > 0:
            template._create_product_feature_values()
        return template

    @api.multi
    def write(self, vals):
        """
        Al actualizar, si se ha modificado product_feature_line_ids,
        actualizamos product feature values de las variantes
        """
        res = super(ProductTemplate, self).write(vals)
        if 'product_feature_line_ids' in vals:
            self._create_product_feature_values()
        return res

    @api.multi
    def _create_product_feature_values(self):
        """
        Crear los valores de características en el producto en función
        de las que están definidas en la plantilla.
        Al quitar características de la plantilla se borran los valores
        en el producto automáticamente (cascade).
        """
        for template in self:
            for variant in template.product_variant_ids:
                values_to_add = \
                    template.product_feature_line_ids.mapped(
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
