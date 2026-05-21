# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMProduct(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from crm.fcrm.doctype.crm_product_units.crm_product_units import CRMProductUnits

		description: DF.TextEditor | None
		disabled: DF.Check
		image: DF.AttachImage | None
		naming_series: DF.Literal["CRM-PROD-.YYYY.-"]
		product_code: DF.Data
		product_name: DF.Data | None
		standard_rate: DF.Currency
		units: DF.Table[CRMProductUnits]
	# end: auto-generated types

	def onload(self):
		self.sync_units()

	def before_save(self):
		self.sync_units()

	def sync_units(self):
		"""Keep the Units child table in sync with CRM Units linked to this product."""
		linked_units = frappe.get_all(
			"CRM Unit",
			filters={"product": self.name},
			fields=["name"],
			order_by="name asc",
		)
		linked_unit_names = {u.name for u in linked_units}

		# Remove rows whose unit is no longer linked to this product
		self.units = [row for row in (self.get("units") or []) if row.unit in linked_unit_names]

		# Append rows for any newly linked unit not yet in the child table
		existing = {row.unit for row in (self.get("units") or [])}
		for unit in linked_units:
			if unit.name not in existing:
				self.append("units", {"unit": unit.name})

	def validate(self):
		self.set_product_name()

	def set_product_name(self):
		if not self.product_name:
			self.product_name = self.product_code
		else:
			self.product_name = self.product_name.strip()

	@staticmethod
	def default_list_data():
		columns = [
			{"label": "Product Code", "type": "Data", "key": "product_code", "width": "14rem"},
			{"label": "Product Name", "type": "Data", "key": "product_name", "width": "14rem"},
			{"label": "Standard Rate", "type": "Currency", "key": "standard_rate", "width": "10rem"},
			{"label": "Disabled", "type": "Check", "key": "disabled", "width": "8rem"},
			{"label": "Modified", "type": "Datetime", "key": "modified", "width": "10rem"},
		]
		rows = ["name", "product_code", "product_name", "standard_rate", "disabled", "modified"]
		return {"columns": columns, "rows": rows}
