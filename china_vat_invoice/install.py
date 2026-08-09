# app 安装/升级时自动创建依赖的 Custom Field 和打印格式
#
# 为什么需要这个文件:
#   Custom Field 是「数据库记录 + 物理列」,用 frappe.new_doc() 手动创建的话
#   module 为 None —— 不属于任何 app,换个环境（新部署/新站点）就没有,
#   而发票模板引用了 cn_bank_info,字段缺失会导致发票打不出来。
#   写在 after_install/after_migrate 里,才能随 app 分发。
#
# 参照:ERPNext 官方 apps/erpnext/erpnext/setup/install.py 同样用 create_custom_fields()

import json
import os

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

# 增值税发票必需但 ERPNext 原生没有的字段:开户行及账号
CUSTOM_FIELDS = {
    "Company": [
        {
            "fieldname": "cn_bank_info",
            "label": "开户行及账号",
            "fieldtype": "Data",
            "insert_after": "tax_id",
            "description": "增值税发票「开户行及账号」栏,例:中国工商银行上海张江支行 1001 2345 6789 0123",
        }
    ],
    "Customer": [
        {
            "fieldname": "cn_bank_info",
            "label": "开户行及账号",
            "fieldtype": "Data",
            "insert_after": "tax_id",
            "description": "增值税发票购买方「开户行及账号」栏",
        }
    ],
}


def after_install():
    """首次安装 app 时执行。"""
    setup_custom_fields()
    import_print_formats()
    frappe.db.commit()


def after_migrate():
    """每次 bench migrate 时执行,保证字段不会因升级丢失(幂等)。"""
    setup_custom_fields()


def setup_custom_fields():
    """创建 Custom Field。create_custom_fields 本身幂等,已存在则跳过。"""
    create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
    frappe.clear_cache()


def import_print_formats():
    """导入随 app 分发的打印格式（含 241×140mm 增值税专用发票）。

    打印格式是数据库记录,不随代码走,所以导出成 JSON 放在 app 里。
    """
    path = os.path.join(
        frappe.get_app_path("china_vat_invoice"), "data", "print_formats.json"
    )
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as f:
        specs = json.load(f)

    for spec in specs:
        name = spec.get("name")
        if not name:
            continue
        doc = (
            frappe.get_doc("Print Format", name)
            if frappe.db.exists("Print Format", name)
            else frappe.new_doc("Print Format")
        )
        if not doc.get("name"):
            doc.name = name
        for key, value in spec.items():
            if key not in ("doctype", "name"):
                setattr(doc, key, value)
        doc.save(ignore_permissions=True)

        # A4 常规单据设为默认;增值税发票是特殊纸张,走「打印发票」按钮,不设默认
        if name != "增值税专用发票-中文" and spec.get("doc_type"):
            frappe.make_property_setter(
                {
                    "doctype": spec["doc_type"],
                    "doctype_or_field": "DocType",
                    "property": "default_print_format",
                    "value": name,
                    "property_type": "Data",
                },
                is_system_generated=False,
            )
