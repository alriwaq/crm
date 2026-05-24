// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("CRM Project", {
  project_code: function (frm) {
    if (!frm.doc.project_name)
      frm.set_value("project_name", frm.doc.project_code);
  },
});
