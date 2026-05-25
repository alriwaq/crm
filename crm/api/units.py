# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def after_insert(doc, method=None):
	_sync_to_project(doc, None, doc.get("project"))


def on_update(doc, method=None):
	old_project = (
		doc._doc_before_save.get("project")
		if getattr(doc, "_doc_before_save", None)
		else None
	)
	new_project = doc.get("project")
	_sync_to_project(doc, old_project, new_project)


def on_submit(doc, method=None):
	project = doc.get("project")
	if project:
		_add_unit_to_project(doc.name, project)


def on_trash(doc, method=None):
	project = doc.get("project")
	if project:
		_remove_unit_from_project(doc.name, project)


def _sync_to_project(doc, old_project, new_project):
	if old_project and old_project != new_project:
		_remove_unit_from_project(doc.name, old_project)
	if new_project:
		_add_unit_to_project(doc.name, new_project)


def _add_unit_to_project(unit_name, project_name):
	"""Add a Unit to a CRM Project's child table if not already present."""
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
	"""Remove a Unit from a CRM Project's child table."""
	if not frappe.db.exists("CRM Project", project_name):
		return

	rows = frappe.get_all(
		"CRM Project Units",
		filters={"parent": project_name, "unit": unit_name, "parenttype": "CRM Project"},
		fields=["name"],
	)
	for row in rows:
		frappe.delete_doc("CRM Project Units", row.name, ignore_permissions=True, force=True)
