app_name = "china_vat_invoice"
app_title = "China VAT Invoice"
app_publisher = "CinseYoung"
app_description = "ERPNext 中国本地化: 增值税发票出票 (241×140mm)"
app_email = "dev@example.com"
app_license = "mit"

# Sales Invoice 表单增加「打印发票」按钮(241×140mm 增值税专用发票)
# 用 doctype_js 而非 app_include_js:只在该 doctype 加载,不污染全局
doctype_js = {
	"Sales Invoice": "public/js/sales_invoice_fapiao.js",
}
