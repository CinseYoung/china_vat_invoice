// Sales Invoice 表单:增加「打印发票」按钮,输出 241×140mm 增值税专用发票
frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		// 仅已提交的发票可出票(草稿不该出票)
		if (frm.doc.docstatus !== 1) return;

		frm.add_custom_button(
			__("打印发票"),
			() => {
				// open_url_post 会自动带上 CSRF token 和会话 cookie
				open_url_post(
					"/api/method/china_vat_invoice.cn_print.download_fapiao",
					{ name: frm.doc.name },
					true // 新窗口打开
				);
			},
			__("打印")
		);
	},
});
