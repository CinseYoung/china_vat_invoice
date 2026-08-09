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

# 安装/升级时自动创建依赖项(Custom Field + 打印格式)
# 不这样做的话,换环境部署后 cn_bank_info 字段缺失 -> 发票打不出来
after_install = "china_vat_invoice.install.after_install"
after_migrate = "china_vat_invoice.install.after_migrate"
