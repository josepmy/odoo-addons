# Copyright 2020 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    product_feature_lot_value_ids = fields.One2many(
        comodel_name='product_feature.lot.value',
        inverse_name='lot_id',
        string='Feature values',
        help='You can manage the features in the product template, then you can input here values for each one.',
    )

    @api.model
    def create(self, vals):
        """
        Al crear, si se ha indicado product, creamos sus product feature lot values
        """
        lot = super(StockProductionLot, self).create(vals)
        if lot.product_id:
            lot._create_product_feature_lot_values()
        return lot

    @api.multi
    def write(self, vals):
        """
        Al actualizar, si se ha modificado product,
        actualizamos product feature lot values
        """
        res = super(StockProductionLot, self).write(vals)
        if 'product_id' in vals:
            self.product_feature_lot_value_ids.unlink()
            self._create_product_feature_lot_values()
        return res

    @api.multi
    def _create_product_feature_lot_values(self):
        """
        Crear los valores de características en el lote en función
        de las que están definidas en la plantilla del producto y
        corresponden a lote.
        Si se modifican las características en la plantilla no se
        actualizan en el lote (a diferencia de lo que ocurre con los
        productos).
        """
        for lot in self:
            template = lot.product_id and lot.product_id.product_tmpl_id
            if template:
                for line in template.product_feature_line_ids.filtered(
                        lambda x: x.is_lot_feature):
                    vals = {
                        'lot_id': lot.id,
                        'feature_line_id': line.id,
                        'feature_id': line.feature_id.id,
                    }
                    if line.feature_value_type == 'table' and line.default_table_value_id:
                        vals['table_value_id'] = line.default_table_value_id.id
                    elif line.feature_value_type == 'text' and line.default_text_value:
                        vals['text_value'] = line.default_text_value
                    elif line.feature_value_type == 'number' and line.default_number_value:
                        vals['number_value'] = line.default_number_value
                    self.env['product_feature.lot.value'].create(vals)

