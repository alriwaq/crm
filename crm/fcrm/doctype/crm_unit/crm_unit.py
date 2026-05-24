# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMUnit(Document):
	def after_insert(self):
		self._sync_to_project(None, self.get("project"))

	def on_update(self):
		old_project = (
			self._doc_before_save.get("project")
			if getattr(self, "_doc_before_save", None)
			else None
		)
		new_project = self.get("project")
		self._sync_to_project(old_project, new_project)

	def on_trash(self):
		project = self.get("project")
		if project:
			_remove_unit_from_project(self.name, project)

	def _sync_to_project(self, old_project, new_project):
		if old_project and old_project != new_project:
			_remove_unit_from_project(self.name, old_project)
		if new_project:
			_add_unit_to_project(self.name, new_project)

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


def _add_unit_to_project(unit_name, project_name):
	"""Add a CRM Unit to a CRM Project's child table if not already present."""
	if not frappe.db.exists("CRM Project", project_name):
		return

	already_linked = frappe.db.exists(
		"CRM Project Units",
		{"parent": project_name, "unit": unit_name, "parenttype": "CRM Project"},
	)
	if already_linked:
		return

	row = frappe.new_doc("CRM Project Units")
	row.unit = unit_name
	row.parent = project_name
	row.parenttype = "CRM Project"
	row.parentfield = "units"
	row.insert(ignore_permissions=True)


def _remove_unit_from_project(unit_name, project_name):
	"""Remove a CRM Unit from a CRM Project's child table."""
	if not frappe.db.exists("CRM Project", project_name):
		return

	rows = frappe.get_all(
		"CRM Project Units",
		filters={"parent": project_name, "unit": unit_name, "parenttype": "CRM Project"},
		fields=["name"],
	)
	for row in rows:
		frappe.delete_doc("CRM Project Units", row.name, ignore_permissions=True, force=True)
