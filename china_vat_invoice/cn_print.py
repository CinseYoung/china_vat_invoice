# 中国本地化打印:增值税专用发票 241×140mm 出票
#
# 为什么这段必须放在真实 app 里(不能用 Server Script):
#   Frappe 的 Server Script 沙箱禁止写 frappe.response,
#   会报 SyntaxError: Not allowed to write to object ... NamespaceDict
#
# 为什么必须传 per-request 纸张参数(不能只改全局 Print Settings):
#   Print Format 没有 per-format 的纸张尺寸字段,只有全局
#   Print Settings.pdf_page_size。改全局会让所有单据都变成 241×140mm。
#
# 相关坑(已在 Print Format 的 <style> 里处理):
#   Frappe 包裹层有 min-height:11.69in(A4 297mm) + padding:0.75in,
#   不覆盖会导致 140mm 纸张必然分成 2 页,且与字号/行高无关。

import frappe
from frappe import _
from frappe.utils.pdf import get_pdf

# 增值税发票专用纸尺寸
FAPIAO_PAPER = {
    "page-width": "241mm",
    "page-height": "140mm",
    "margin-top": "2mm",
    "margin-bottom": "2mm",
    "margin-left": "4mm",
    "margin-right": "4mm",
}

FAPIAO_FORMAT = "增值税专用发票-中文"


@frappe.whitelist()
def download_fapiao(name: str, print_format: str | None = None):
    """输出 241×140mm 增值税专用发票 PDF。

    挂在 Sales Invoice 表单的「打印发票」按钮上。
    调用: /api/method/china_vat_invoice.cn_print.download_fapiao?name=SI-26-00001
    """
    if not name:
        frappe.throw(_("缺少参数 name"))

    # 权限:必须对该发票有读权限(未登录/无权限 -> 403)
    if not frappe.has_permission("Sales Invoice", "read", doc=name):
        raise frappe.PermissionError

    fmt = print_format or FAPIAO_FORMAT
    if not frappe.db.exists("Print Format", fmt):
        frappe.throw(_("打印格式 {0} 不存在,请先导入中文打印模板").format(fmt))

    # 中文金额大写依赖 lang=zh
    # (erpnext_china.print_utils 按 frappe.local.lang 判断是否输出汉字大写)
    frappe.local.lang = "zh"

    html = frappe.get_print("Sales Invoice", name, print_format=fmt, no_letterhead=1)
    pdf = get_pdf(html, options=dict(FAPIAO_PAPER))

    frappe.local.response.filename = f"增值税专用发票-{name}.pdf"
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"
