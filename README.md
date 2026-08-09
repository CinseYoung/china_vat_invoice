# China VAT Invoice — ERPNext 增值税发票出票

给 ERPNext Sales Invoice 增加「打印发票」按钮，直接输出符合中国增值税专用发票尺寸 (241×140mm) 的 PDF。

## 功能

### 增值税专用发票一键出票（241×140mm）

在**已提交**的销售发票表单上，「打印」菜单里会出现 **「打印发票」** 按钮，点击直接下载符合增值税发票专用纸尺寸的 PDF。

- 后端: `china_vat_invoice/cn_print.py` → `download_fapiao(name)`
- 前端: `china_vat_invoice/public/js/sales_invoice_fapiao.js`
- API: `/api/method/china_vat_invoice.cn_print.download_fapiao?name=SI-xxxxx`

**不影响其它单据** — 全局 `Print Settings.pdf_page_size` 保持 A4，只有发票走 241×140mm（通过 per-request 参数）。

## 依赖

- frappe / erpnext `>=15,<17`
- **`erpnext_china`** — 提供中文金额大写函数 `cncurrency()`（模板里用到）
- 打印格式 **`增值税专用发票-中文`** — 需先导入（见部署目录的 `cn_print_formats.json`）

## 安装

通过 bench get-app 从 Git 仓库安装：

```bash
bench get-app china_vat_invoice https://github.com/CinseYoung/china_vat_invoice.git
bench --site <站点> install-app china_vat_invoice
bench build --app china_vat_invoice
bench --site <站点> clear-cache
```

`bootstrap-aliyun.sh` 已自动完成以上步骤。

## 实现说明（踩过的坑）

1. **不能用 Server Script** — 沙箱禁止写 `frappe.response`，报 `SyntaxError: Not allowed to write to object ... NamespaceDict`。必须放在真实 app 里。
2. **必须传 per-request 纸张参数** — `Print Format` 没有 per-format 的尺寸字段，只有全局 `Print Settings`。改全局会让所有单据变成发票纸。
3. **打印模板里必须覆盖 Frappe 包裹层的 `min-height`** — Frappe 的 `.print-format` 带 `min-height:11.69in`(A4 297mm)，不覆盖会让 140mm 纸张必然分成 2 页，且与字号/行高无关。
4. **中文金额大写依赖 `frappe.local.lang == "zh"`** — 代码里显式设置，不依赖全局配置。
