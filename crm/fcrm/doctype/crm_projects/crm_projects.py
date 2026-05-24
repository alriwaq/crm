# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMProjects(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		autocomplete: DF.Autocomplete | None
		discount_amount: DF.Currency
		discount_percentage: DF.Percent
		net_amount: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project_code: DF.Link | None
		project_name: DF.Data
		qty: DF.Float
		rate: DF.Currency
	# end: auto-generated types

	pass


def create_project_details_script(doctype):
	if not frappe.db.exists("CRM Form Script", "Project Details Script for " + doctype):
		script = get_project_details_script(doctype)
		frappe.get_doc(
			{
				"doctype": "CRM Form Script",
				"name": "Project Details Script for " + doctype,
				"dt": doctype,
				"view": "Form",
				"script": script,
				"enabled": 1,
				"is_standard": 1,
			}
		).insert()


def get_project_details_script(doctype):
	doctype_class = "class " + doctype.replace(" ", "")

	return (
		doctype_class
		+ " {"
		+ """
  update_total() {
    let total = 0
    let total_qty = 0
    let net_total = 0
    let discount_applied = false

    this.doc.projects.forEach((d) => {
      total += d.amount
      net_total += d.net_amount
      if (d.discount_percentage > 0) {
        discount_applied = true
      }
    })

    this.doc.total = total
    this.doc.net_total = net_total || total

    if (!net_total && discount_applied) {
      this.doc.net_total = net_total
    }
  }
}

class CRMProjects {
  projects_add() {
    let row = this.doc.getRow('projects')
    row.trigger('qty')
    this.doc.trigger('update_total')
  }

  projects_remove() {
    this.doc.trigger('update_total')
  }

  async project_code(idx) {
    let row = this.doc.getRow('projects', idx)

    let a = await call("frappe.client.get_value", {
        doctype: "CRM Project",
        filters: { name: row.project_code },
        fieldname: ["project_name", "standard_rate"],
    })

    row.project_name = a.project_name
    if (a.standard_rate && !row.rate) {
        row.rate = a.standard_rate
        row.trigger("rate")
    }
  }

  qty(idx) {
    let row = this.doc.getRow('projects', idx)
    row.amount = row.qty * row.rate
    row.trigger('discount_percentage', idx)
  }

  rate() {
    let row = this.doc.getRow('projects')
    row.amount = row.qty * row.rate
    row.trigger('discount_percentage')
  }

  discount_percentage(idx) {
    let row = this.doc.getRow('projects', idx)
    if (!row.discount_percentage) {
      row.net_amount = row.amount
      row.discount_amount = 0
    }
    if (row.discount_percentage && row.amount) {
      row.discount_amount = (row.discount_percentage / 100) * row.amount
      row.net_amount = row.amount - row.discount_amount
    }
    this.doc.trigger('update_total')
  }
}"""
	)
