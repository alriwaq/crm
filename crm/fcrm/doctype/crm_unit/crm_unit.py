# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMUnit(Document):
	def after_insert(self):
		self._sync_to_product(None, self.get("product"))

	def on_update(self):
		old_product = (
			self._doc_before_save.get("product")
			if getattr(self, "_doc_before_save", None)
			else None
		)
		new_product = self.get("product")
		self._sync_to_product(old_product, new_product)

	def on_trash(self):
		product = self.get("product")
		if product:
			_remove_unit_from_product(self.name, product)

	def _sync_to_product(self, old_product, new_product):
		if old_product and old_product != new_product:
			_remove_unit_from_product(self.name, old_product)
		if new_product:
			_add_unit_to_product(self.name, new_product)

	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Title",
				"type": "Data",
				"key": "title",
				"width": "16rem",
			},
			{
				"label": "Last Modified",
				"type": "Datetime",
				"key": "modified",
				"width": "8rem",
			},
		]
		rows = ["name", "title", "modified"]
		return {"columns": columns, "rows": rows}


def _add_unit_to_product(unit_name, product_name):
	"""Add a CRM Unit to a CRM Product's child table if not already present."""
	if not frappe.db.exists("CRM Product", product_name):
		return

	already_linked = frappe.db.exists(
		"CRM Product Units",
		{"parent": product_name, "unit": unit_name, "parenttype": "CRM Product"},
	)
	if already_linked:
		return

	row = frappe.new_doc("CRM Product Units")
	row.unit = unit_name
	row.parent = product_name
	row.parenttype = "CRM Product"
	row.parentfield = "units"
	row.insert(ignore_permissions=True)


def _remove_unit_from_product(unit_name, product_name):
	"""Remove a CRM Unit from a CRM Product's child table."""
	if not frappe.db.exists("CRM Product", product_name):
		return

	rows = frappe.get_all(
		"CRM Product Units",
		filters={"parent": product_name, "unit": unit_name, "parenttype": "CRM Product"},
		fields=["name"],
	)
	for row in rows:
		frappe.delete_doc("CRM Product Units", row.name, ignore_permissions=True, force=True)
