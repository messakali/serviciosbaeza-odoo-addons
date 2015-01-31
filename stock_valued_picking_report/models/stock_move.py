# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#    Copyright (c) 2015 Antiun Ingenieria (http://www.antiun.com)
#                       Antonio Espinosa <antonioea@antiun.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import fields, models, api

# Uncomment for debug proposes
# from pprint import pformat
# import logging
# _logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    sale_price_unit = fields.Float(
        string="Sale price unit",
        related='procurement_id.sale_line_id.price_unit',
        readonly=True)
    sale_discount = fields.Float(
        string="Sale discount (%)",
        related='procurement_id.sale_line_id.discount',
        readonly=True)
    sale_price_subtotal = fields.Float(
        string="Price subtotal",
        compute='_get_sale_price_subtotal',
        readonly=True)

    @api.one
    @api.depends(
        'sale_price_unit',
        'sale_discount',
        'product_qty',
        'product_id',
        'procurement_id.sale_line_id.order_id.currency_id',
    )
    def _get_sale_price_subtotal(self):
        st = 0.0
        price = self.sale_price_unit
        qty = self.product_qty
        discount = self.sale_discount
        subtotal = price * qty * (1 - (discount or 0.0) / 100.0)
        # Only get subtotal if this stock.move belongs to a
        # stock.picking created from a sale.order
        if self.procurement_id and self.procurement_id.sale_line_id:
            # Round by currency precision
            order = self.procurement_id.sale_line_id.order_id
            currency = order.currency_id
            if currency:
                st = currency.round(subtotal)
        # Write subtotal into record (cache because this field is store=False)
        self.sale_price_subtotal = st
