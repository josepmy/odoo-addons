# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_feature_value_ids = fields.One2many(
        comodel_name='product_feature.value',
        inverse_name='product_id', string='Feature values')

