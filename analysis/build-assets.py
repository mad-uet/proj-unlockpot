"""PROTOTYPE. Build an offline HTML demo and XLSX with Python's standard library."""
import csv
import html
import json
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

base = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()

def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

meta = read_csv(base / "indicators.csv")
data = read_csv(out / "synthetic-829.csv")
summary = read_csv(out / "group-summary.csv")
cases = read_csv(out / "scoring-scenarios.csv")
groups = list(dict.fromkeys(m["group"] for m in meta))
first = [int(data[0][m["indicator"]]) for m in meta]

# Formula caches are computed from the same explicit rule, then compared to R.
def score(values):
    valid = [type(v) in (int, float) and math.isfinite(v) and v == int(v) and 1 <= v <= 5 for v in values]
    return sum(values) / len(values) if all(valid) else None

def col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def formula(text, cached):
    return {"f": text, "v": cached}

def cell(row, column, value):
    address = f"{col(column)}{row}"
    style = ' s="1"' if row == 1 else ""
    if value is None:
        return f'<c r="{address}"{style}/>'
    if isinstance(value, dict):
        v = value["v"]
        kind = ' t="str"' if isinstance(v, str) else ""
        return f'<c r="{address}"{kind}{style}><f>{escape(value["f"])}</f><v>{escape(str(v))}</v></c>'
    if isinstance(value, (int, float)):
        return f'<c r="{address}"{style}><v>{value}</v></c>'
    return f'<c r="{address}" t="inlineStr"{style}><is><t xml:space="preserve">{escape(str(value))}</t></is></c>'

def sheet(rows, widths=None, validate=None):
    columns = "".join(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths or [], 1))
    body = "".join(f'<row r="{r}">' + "".join(cell(r, c, v) for c, v in enumerate(values, 1)) + '</row>' for r, values in enumerate(rows, 1))
    dv = ""
    if validate:
        dv = f'<dataValidations count="1"><dataValidation type="whole" operator="between" allowBlank="1" showErrorMessage="1" errorTitle="Giá trị không hợp lệ" error="Chỉ nhập số nguyên từ 1 đến 5." sqref="{validate}"><formula1>1</formula1><formula2>5</formula2></dataValidation></dataValidations>'
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>' + columns + '</cols><sheetData>' + body + '</sheetData>' + dv + '</worksheet>'

def valid_formula(ref):
    return f'IFERROR(IF(AND(ISNUMBER({ref}),{ref}=INT({ref}),{ref}>=1,{ref}<=5),1,0),0)'

instructions = [
    ["BẢN THỬ THEO PHẠM VI ĐÃ CHỌN", "Nội dung"],
    ["Thiết kế", "Trung bình đủ câu trong từng nhóm, kèm quy trình R mở rộng đã được người học đồng ý."],
    ["Nguồn", "49 chỉ báo theo Phụ lục F, Bảng A4 trang 23. Bản dịch nhãn rút gọn phục vụ demo, xem nội dung gốc khi trích dẫn."],
    ["Sai lệch trong bài", "Tóm tắt ghi 47, A4 có 49, A2 có 52 mã. Không tự sửa danh mục để khớp số 47."],
    ["Cách dùng", "Sửa cột D của Bang diem. Mặc định là phiếu đầu tiên trong dữ liệu tổng hợp. Xem điểm ở cột I."],
    ["Câu hỏi", "Bạn đánh giá mức độ quan trọng của từng chỉ báo đối với năng lực quản trị như thế nào?"],
    ["Mức 1", "Cực kỳ không quan trọng"], ["Mức 2", "Không quan trọng"],
    ["Mức 3", "Trung lập theo trang 8. Phụ lục dùng general, cần ghi chú khác biệt cách diễn đạt."],
    ["Mức 4", "Quan trọng"], ["Mức 5", "Cực kỳ quan trọng"],
    ["Quy tắc thử", "Trung bình không trọng số trong nhóm khi đủ toàn bộ số nguyên 1-5. Thiếu hoặc sai một ô thì không có điểm nhóm. Không điền bù, không đảo điểm."],
    ["Diễn giải", "Điểm mức độ quan trọng theo nhóm năng lực. Không xếp loại yếu hoặc tốt, không có điểm tổng toàn thang."],
    ["Quyền tác giả", "Quy tắc tính điểm và xử lý thiếu do demo đề xuất. Bài báo không công bố các quy tắc này."],
    ["Dữ liệu", "829 dòng được tạo bởi R với seed 20261104. Không phải dữ liệu khảo sát gốc hoặc dữ liệu tổ chức thật."],
    ["Vai trò", "Sáu loại danh nghĩa. PLS dùng năm biến giả một chỉ báo, chủ đầu tư là nhóm tham chiếu. Các hệ số PLS được chuẩn hóa, không phải chênh lệch trung bình thô."],
    ["Đã chạy", "Sàng lọc trên 438 phiếu tổng hợp riêng, PCA với oblimin, CFA WLSMV, CR, AVE, HTMT Pearson và PLS-PM với 1000 mẫu bootstrap."],
    ["Giới hạn", "Chưa chạy EFA khám phá theo mô hình nhân tố chung hoặc tái lập dữ liệu gốc. PLS minh họa chỉ xét vai trò, không xét loại dự án và số năm hoạt động."],
    ["Tính lại công thức", "Tệp có công thức và giá trị lưu sẵn đã đối chiếu với R. Chưa kiểm tra việc tính lại bằng Excel hoặc LibreOffice trong môi trường này."],
    ["Kiểm tra tương tác", "Mở Tinh huong để xem đủ câu, ô trống, giá trị 0, 6, 4.5 và chữ. Thử sửa trực tiếp một ô để xem điểm biến mất."],
]
rows = [["Nhóm năng lực", "Mã chỉ báo", "Nội dung chỉ báo rút gọn", "Mức độ quan trọng", "Hợp lệ", None, "Nhóm năng lực", "Số câu hợp lệ", "Điểm mức độ quan trọng", "Trạng thái"]]
for i, m in enumerate(meta, 2):
    rows.append([m["group_vi"], m["indicator"], m["label_vi"], first[i - 2], formula(valid_formula(f"D{i}"), 1)])
for i, g in enumerate(groups, 2):
    indices = [j for j, m in enumerate(meta) if m["group"] == g]
    start, end = indices[0] + 2, indices[-1] + 2
    k = len(indices)
    value = score([first[j] for j in indices])
    expected = float(summary[i - 2]["mean_first_person"])
    if not math.isclose(value, expected, abs_tol=1e-12):
        raise ValueError(f"Cached score differs from R: {g}")
    rows[i - 1].extend([None] * (6 - len(rows[i - 1])))
    rows[i - 1].extend([meta[indices[0]]["group_vi"], formula(f"SUM(E{start}:E{end})", k),
                       formula(f'IF(H{i}={k},AVERAGE(D{start}:D{end}),"")', value),
                       formula(f'IF(COUNTA(D{start}:D{end})=0,"Chưa nhập",IF(H{i}={k},"Đủ dữ liệu","Thiếu hoặc không hợp lệ"))', "Đủ dữ liệu")])

scenario_rows = [["Tình huống"] + [f"Câu {i}" for i in range(1, 9)] + ["Điểm mức độ quan trọng"] + [f"Hợp lệ {i}" for i in range(1, 9)] + ["Trạng thái"]]
scenario_values = [[4] * 8, [None] + [4] * 7, [None] * 8, [0] + [4] * 7, [6] + [4] * 7, [4.5] + [4] * 7, ["abc"] + [4] * 7]
scenario_labels = ["Đủ 8 câu", "Thiếu một câu", "Trống cả nhóm", "Nhập 0", "Nhập 6", "Nhập 4.5", "Nhập chữ"]
for r, (values, case, label) in enumerate(zip(scenario_values, cases, scenario_labels), 2):
    result = score(values)
    expected = float(case["score"]) if case["score"] else None
    if result != expected:
        raise ValueError(f"Scenario differs from R: {label}")
    helpers = [formula(valid_formula(f"{col(j + 2)}{r}"), int(type(v) in (int, float) and v == int(v) and 1 <= v <= 5)) for j, v in enumerate(values)]
    scenario_rows.append([label] + values + [formula(f'IF(SUM(K{r}:R{r})=8,AVERAGE(B{r}:I{r}),"")', result if result is not None else "")] + helpers + [formula(f'IF(COUNTA(B{r}:I{r})=0,"Chưa nhập",IF(SUM(K{r}:R{r})=8,"Đủ dữ liệu","Thiếu hoặc không hợp lệ"))', "Chưa nhập" if all(v is None for v in values) else "Đủ dữ liệu" if result is not None else "Thiếu hoặc không hợp lệ")])

results = [["Nhóm năng lực", "Số chỉ báo", "Số phiếu", "Trung bình nhóm trên 829 phiếu", "Độ lệch chuẩn", "Alpha thô"]]
for s in summary:
    results.append([s["group_vi"], int(s["k"]), int(s["n"]), float(s["mean"]), float(s["sd"]), float(s["alpha_raw"])])
raw = [["Mã phiếu", "Vai trò tổ chức"] + [m["indicator"] for m in meta]]
role_vi = dict(zip(["Chu dau tu", "Giam sat", "Tong thau", "Thau phu", "Vat lieu", "Thiet bi"], ["Chủ đầu tư hoặc đơn vị phát triển dự án", "Đơn vị giám sát", "Tổng thầu", "Nhà thầu phụ", "Nhà cung cấp vật liệu", "Nhà cung cấp thiết bị"]))
raw.extend([[int(d["id"]), role_vi[d["role"]]] + [int(d[m["indicator"]]) for m in meta] for d in data])
sheets = [("Huong dan", sheet(instructions, [28, 130])), ("Bang diem", sheet(rows, [24, 18, 82, 24, 12, 3, 26, 20, 28, 30], "D2:D50")), ("Tinh huong", sheet(scenario_rows, [25] + [12] * 8 + [26] + [12] * 8 + [32])), ("Ket qua R", sheet(results, [28, 16, 16, 36, 22, 22])), ("Du lieu 829", sheet(raw, [16, 42] + [18] * 49))]
# Present actual extended results with Vietnamese labels, rather than copied article values.
measure_values = {r["metric"]: float(r["value"]) if r["value"] else None for r in read_csv(out / "cfa-fit-measures.csv")}
measure_labels = {"chisq.scaled": "Chi bình phương hiệu chỉnh", "df.scaled": "Bậc tự do", "pvalue.scaled": "Giá trị p hiệu chỉnh", "cfi.scaled": "CFI hiệu chỉnh", "tli.scaled": "TLI hiệu chỉnh", "rmsea.scaled": "RMSEA hiệu chỉnh", "srmr": "SRMR"}
cfa_rows = [["Chỉ số CFA WLSMV", "Giá trị"]] + [[label, measure_values.get(key)] for key, label in measure_labels.items()]
reliability_rows = [["Nhóm năng lực", "Tải nhỏ nhất", "Tải lớn nhất", "Độ tin cậy tổng hợp CR", "Phương sai trích AVE"]]
name_vi = {m["group"]: m["group_vi"] for m in meta}
for r in read_csv(out / "cfa-cr-ave.csv"):
    reliability_rows.append([name_vi[r["group"]]] + [float(r[k]) for k in ["min_loading", "max_loading", "CR", "AVE"]])
htmt_rows = [["Nhóm thứ nhất", "Nhóm thứ hai", "HTMT Pearson", "Dưới 0,85"]]
for r in read_csv(out / "htmt-pairs.csv"):
    htmt_rows.append([name_vi[r["group_a"]], name_vi[r["group_b"]], float(r["HTMT"]), "Có" if r["below_085"] == "TRUE" else "Không"])
role_construct_vi = dict(zip([f"Role{i}" for i in range(2, 7)], ["Giám sát", "Tổng thầu", "Nhà thầu phụ", "Vật liệu", "Thiết bị"]))
path_rows = [["Vai trò so với nhóm chủ đầu tư", "Nhóm năng lực", "Hệ số chuẩn hóa", "Sai số chuẩn bootstrap", "Cận 2,5%", "Cận 97,5%"]]
for r in read_csv(out / "pls-bootstrap-paths.csv"):
    start, end = [s.strip() for s in r["path"].split("->")]
    path_rows.append([role_construct_vi[start], name_vi[end]] + [float(r[k]) for k in ["Original", "Std.Error", "perc.025", "perc.975"]])
bootstrap_counts = read_csv(out / "pls-bootstrap-counts.csv")[0]
bootstrap_rows = [["Số mẫu đã thử", "Số mẫu hội tụ", "Số mẫu thất bại", "Seed"], [int(bootstrap_counts[k]) for k in ["attempted", "successful", "failed", "seed"]]]
r2_rows = [["Nhóm năng lực", "R bình phương của PLS"]]
for r in read_csv(out / "pls-inner-summary.csv"):
    if r["construct"] in name_vi:
        r2_rows.append([name_vi[r["construct"]], float(r["R2"])])
sheets.extend([("CFA WLSMV", sheet(cfa_rows, [36, 24])), ("CR AVE", sheet(reliability_rows, [28, 22, 22, 30, 26])), ("HTMT", sheet(htmt_rows, [28, 28, 22, 18])), ("PLS bootstrap", sheet(path_rows, [36, 28, 24, 28, 24, 24])), ("PLS R2", sheet(r2_rows, [28, 32])), ("Trang thai bootstrap", sheet(bootstrap_rows, [24, 24, 24, 24]))])

def rendered_table(rows):
    def display(value):
        if value is None:
            return "Chưa có"
        if isinstance(value, float):
            if value != 0 and abs(value) < 0.0001:
                return format(value, ".3g")
            return format(value, ".4f").replace(".", ",")
        return str(value)
    return '<table><thead><tr>' + ''.join('<th>' + html.escape(str(v)) + '</th>' for v in rows[0]) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + html.escape(display(v)) + '</td>' for v in row) + '</tr>' for row in rows[1:]) + '</tbody></table>'

report = '<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kết quả demo R mở rộng</title><style>body{font:17px/1.5 system-ui;max-width:1100px;margin:32px auto;padding:0 20px;color:#23313c}table{border-collapse:collapse;width:100%;margin:20px 0}td,th{text-align:left;border-bottom:1px solid #ddd;padding:8px}a{color:#126577}section{margin:36px 0}</style><h1>Kết quả demo R mở rộng</h1><p>Toàn bộ số dưới đây được đọc từ kết quả R trên dữ liệu tổng hợp. Chúng không phải kết quả khảo sát gốc. Tám nhân tố và tương quan được giả định khi tạo dữ liệu; mức phù hợp CFA cao không kiểm định lại thang đo ngoài thực tế.</p><p><a href="demo-prototype.html">Mở phiếu tương tác</a> · <a href="bang-diem-prototype.xlsx">Mở bảng tính và kết quả</a></p>'
report += '<section><h2>Sàng lọc sơ bộ và xoay oblimin</h2><p>Dùng một tập riêng 438 phiếu với 52 mã từ Bảng 1, seed 20261105. Quy tắc sàng lọc chỉ tạo cờ xem xét, không ép loại ba mã của tác giả và không thay danh mục cuối đã chọn. PCA Pearson với direct oblimin chạy riêng trên tập sơ bộ và tập cuối. Bảng pattern là tải trong phương trình tái tạo biến, bảng structure là tương quan với thành phần; hai bảng khác nhau khi các thành phần tương quan.</p><p><a href="preliminary-screening.csv">Kết quả sàng lọc</a> · <a href="pca-oblimin-pattern.csv">Tải pattern trên 829 phiếu</a> · <a href="pca-oblimin-structure.csv">Tải structure</a> · <a href="pca-oblimin-phi.csv">Tương quan các thành phần</a></p></section>'
report += '<section><h2>CFA cho tám nhân tố tương quan</h2><p>49 chỉ báo thứ bậc, WLSMV, phương sai nhân tố bằng 1, không thêm tải chéo hoặc tương quan phần dư sau khi xem kết quả. Các chỉ số có chữ hiệu chỉnh dùng thống kê scaled trong lavaan.</p>' + rendered_table(cfa_rows) + '<p>CR và AVE dưới đây dùng tải và phần dư chuẩn hóa của biến đáp ứng tiềm ẩn trong CFA thứ bậc. Không đồng nhất chúng với độ tin cậy của điểm trung bình Likert quan sát.</p>' + rendered_table(reliability_rows) + '</section>'
report += '<section><h2>HTMT</h2><p>Tỷ số HTMT dùng trung bình các tương quan Pearson tuyệt đối giữa chỉ báo. Đây là phép xấp xỉ riêng trên điểm Likert, không dùng ma trận nhân tố từ CFA WLSMV. Chỉ có ước lượng điểm, chưa bootstrap HTMT. Mốc 0,85 được dùng để minh họa tiêu chí trong bài.</p>' + rendered_table(htmt_rows) + '</section>'
report += '<section><h2>PLS-PM và bootstrap</h2><p>PLS truyền thống, Mode A, năm biến giả vai trò liên hệ với tám nhóm. Nhóm chủ đầu tư làm tham chiếu. Hệ số được chuẩn hóa, không phải chênh lệch trung bình thô. Không có biến loại dự án hoặc số năm hoạt động trong mô hình minh họa này.</p><p>1000 mẫu bootstrap theo phiếu được tạo trước bằng seed 20261106. Mỗi mẫu được phân tích một lần, không thay mẫu khi không hội tụ. Bảng dưới công khai số mẫu thành công và thất bại; các khoảng dùng mẫu thành công. Hai cận là phân vị thực nghiệm 2,5% và 97,5%. Khoảng chứa 0 chưa cho thấy hệ số khác 0 theo cách đọc khoảng này. Không diễn giải nhân quả hoặc suy rộng từ mẫu tổng hợp. Các vai trò được gán độc lập với câu trả lời, vì thế không kỳ vọng tái hiện R bình phương và đường dẫn của tác giả.</p>' + rendered_table(bootstrap_rows) + rendered_table(r2_rows) + rendered_table(path_rows) + '</section><p>EFA khám phá theo mô hình nhân tố chung chưa chạy. CFA đã chạy là phân tích khẳng định theo mô hình được định trước. Bản demo không tái lập toàn bộ cấu hình nghiên cứu gốc.</p></html>'
screening = read_csv(out / "preliminary-screening.csv")
screening_rows = [["Nhóm năng lực", "Mã chỉ báo", "CITC", "Alpha trước", "Alpha khi bỏ chỉ báo", "Cờ xem xét"]]
for r in screening:
    screening_rows.append([name_vi[r["group"]], r["indicator"], float(r["citc"]), float(r["alpha_before"]), float(r["alpha_if_deleted"]), "Có" if r["review_flag"] == "TRUE" else "Không"])
removal_labels = {r["indicator"]: r["label_vi"] for r in read_csv(out / "preliminary-authored-removal-labels.csv")}
removal_rows = [["Mã chỉ báo tác giả loại", "Nội dung", "CITC mô phỏng", "Alpha trước", "Alpha sau bỏ theo danh sách công bố"]]
for r in read_csv(out / "preliminary-authored-removals.csv"):
    removal_rows.append([r["indicator"], removal_labels[r["indicator"]], float(r["simulated_citc"]), float(r["alpha_before"]), float(r["alpha_after_authored_list"])])
sheets.extend([("Sang loc 438", sheet(screening_rows, [28, 22, 22, 22, 26, 22])), ("Doi chieu 3 ma", sheet(removal_rows, [30, 54, 24, 24, 46]))])
flag_count = sum(r["review_flag"] == "TRUE" for r in screening)
preliminary_detail = '<section><h2>Kết quả sàng lọc 438 phiếu</h2><p>Quy tắc thử cần đồng thời CITC nhỏ hơn 0,50 và alpha khi bỏ tăng hơn 0,000001. Có ' + str(flag_count) + ' chỉ báo được gắn cờ xem xét. Không tự loại chỉ báo khỏi bộ cuối.</p><p>Ba chỉ báo trong bảng dưới do tác giả công bố đã loại. CITC và alpha ở đây được tính trên dữ liệu tổng hợp. Với nhóm học hỏi và đổi mới, alpha sau bỏ tính khi bỏ cả LI_1 và LI_4. Kết quả không được ép khớp ba quyết định loại của tác giả.</p>' + rendered_table(removal_rows) + '<details><summary>Xem toàn bộ 52 chỉ báo và cờ sàng lọc</summary>' + rendered_table(screening_rows) + '</details></section>'
report = report.replace('<section><h2>CFA cho tám nhân tố tương quan</h2>', preliminary_detail + '<section><h2>CFA cho tám nhân tố tương quan</h2>', 1)
(out / "ket-qua-mo-rong.html").write_text(report, encoding="utf-8")

main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
with ZipFile(out / "bang-diem-prototype.xlsx", "w", ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' + ''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1, len(sheets) + 1)) + '</Types>')
    z.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="' + rel_ns + '/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    z.writestr("xl/workbook.xml", f'<?xml version="1.0"?><workbook xmlns="{main_ns}" xmlns:r="{rel_ns}"><sheets>' + ''.join(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>' for i, (name, _) in enumerate(sheets, 1)) + '</sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
    z.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(f'<Relationship Id="rId{i}" Type="{rel_ns}/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(sheets) + 1)) + f'<Relationship Id="rId{len(sheets) + 1}" Type="{rel_ns}/styles" Target="styles.xml"/></Relationships>')
    z.writestr("xl/styles.xml", f'<?xml version="1.0"?><styleSheet xmlns="{main_ns}"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="2"><xf fontId="0"/><xf fontId="1" applyFont="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')
    for i, (_, xml) in enumerate(sheets, 1):
        z.writestr(f"xl/worksheets/sheet{i}.xml", xml)

payload = json.dumps({"meta": meta, "first": first, "summary": summary}, ensure_ascii=False).replace("<", "\\u003c")
page = '''<!doctype html>
<html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bản thử điểm mức độ quan trọng</title>
<style>body{font:17px/1.55 system-ui,sans-serif;max-width:1060px;margin:32px auto;padding:0 20px;color:#23313c;background:#fafbfc}h1{line-height:1.2}button,select,input{font:inherit;padding:8px;margin:4px;border:1px solid #adb9c3;border-radius:5px}button{cursor:pointer;background:white}button[aria-selected=true]{background:#e2f1f4;border-color:#126577}section{margin:24px 0;padding:20px;background:white;border:1px solid #dce2e8;border-radius:8px}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:8px;border-bottom:1px solid #e5e9ed}input{width:85px}.state{font-size:20px;color:#126577}small{display:block}a{color:#126577}#notice{min-height:1.5em}button:focus,input:focus,select:focus{outline:2px solid #126577}</style>
<h1>Bản thử điểm mức độ quan trọng</h1>
<p>Bản thử này kiểm tra quy tắc lấy trung bình trong từng nhóm khi đủ câu trả lời nguyên từ 1 đến 5. Một ô trống hoặc sai sẽ làm nhóm chưa có điểm. Người học đã chọn phạm vi mở rộng. Quy tắc tính điểm do demo đề xuất, không gán cho tác giả.</p>
<p>49 chỉ báo theo Phụ lục F. Tóm tắt bài báo ghi 47 và Bảng A2 có 52 mã. Điểm thể hiện mức độ quan trọng theo nhận định của người trả lời. Không dùng để xếp loại năng lực hiện có của tổ chức.</p>
<section><h2>Trạng thái hiện tại</h2><label>Nhóm năng lực <select id="group"></select></label>
<p class="state" id="state" aria-live="polite"></p><p id="notice" aria-live="polite"></p>
<small>Câu hỏi: Bạn đánh giá mức độ quan trọng của chỉ báo đối với năng lực quản trị như thế nào?</small>
<small>1: Cực kỳ không quan trọng. 2: Không quan trọng. 3: Trung lập. 4: Quan trọng. 5: Cực kỳ quan trọng. Trang 8 dùng trung lập, phụ lục dùng general cho mức 3.</small>
<table><thead><tr><th>Mã và nội dung chỉ báo rút gọn</th><th>Câu trả lời</th><th>Kiểm tra</th></tr></thead><tbody id="inputs"></tbody></table>
<h3>Điểm của tám nhóm trong phiếu đang thử</h3><div id="all"></div></section>
<section><h2>Thử tự do</h2><button data-action="fill">Điền 4 cho cả nhóm</button><button data-action="missing">Xóa câu đầu</button><button data-action="empty">Xóa cả nhóm</button><button data-action="six">Nhập 6 ở câu đầu</button><button data-action="decimal">Nhập 4,5 ở câu đầu</button><button data-action="text">Nhập chữ ở câu đầu</button><button data-action="first">Nạp phiếu tổng hợp đầu tiên</button></section>
<section><h2>Tình huống có hướng dẫn</h2><div role="tablist" aria-label="Tình huống"><button role="tab" data-scenario="complete">Đủ câu</button><button role="tab" data-scenario="missing">Thiếu câu</button><button role="tab" data-scenario="invalid">Sai giá trị</button></div><p id="guide"></p><div id="steps"></div></section>
<section><h2>Kết quả đã chạy bằng R trên dữ liệu tổng hợp</h2><p>829 phiếu, seed 20261104. Bảng dưới là kết quả cố định từ lần chạy R, không đổi khi sửa phiếu tương tác ở trên. Tám nhóm và tương quan được giả định khi tạo dữ liệu. Kết quả không xác nhận mô hình của tác giả.</p><div id="rsummary"></div><p><a href="bang-diem-prototype.xlsx">Mở bảng tính thử</a> · <a href="pca-scree.svg">Xem biểu đồ PCA</a> · <a href="synthetic-829.csv">Dữ liệu tổng hợp</a></p><p>Đã chạy thêm sàng lọc trên một tập 438 phiếu tổng hợp riêng, PCA với direct oblimin, CFA WLSMV, CR, AVE, HTMT Pearson và PLS-PM với 1000 mẫu bootstrap. EFA khám phá theo mô hình nhân tố chung chưa chạy. Các mô hình và kết quả tổng hợp không tái lập dữ liệu hoặc cấu hình đầy đủ của tác giả. <a href="ket-qua-mo-rong.html">Xem kết quả mở rộng và giới hạn diễn giải</a>.</p></section>
<script>
const data = __PAYLOAD__;
// Pure scoring module. No DOM access and no persistence.
const Scoring = {
 valid: v => typeof v === 'number' && Number.isInteger(v) && v >= 1 && v <= 5,
 summarize: values => {const n = values.filter(Scoring.valid).length; return {n, k: values.length, mean: n === values.length ? values.reduce((a,b)=>a+b,0)/values.length : null};},
 change: (state, index, value) => state.map((v,i)=>i===index?value:v)
};
const groupNames = [...new Set(data.meta.map(m=>m.group))];
let state = data.meta.map(()=>4), active = groupNames[0];
const byId = id=>document.getElementById(id);
const indices = ()=>data.meta.flatMap((m,i)=>m.group===active?[i]:[]);
const escapeText = s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const format = n=>n===null?'Chưa có điểm':n.toLocaleString('vi-VN',{maximumFractionDigits:3});
function render(message='') {
 const ids=indices(), result=Scoring.summarize(ids.map(i=>state[i]));
 byId('group').value=active;
 byId('state').textContent=`${result.n}/${result.k} câu hợp lệ. Điểm mức độ quan trọng: ${format(result.mean)}.`;
 byId('notice').textContent=message;
 byId('inputs').innerHTML=ids.map(i=>`<tr><td>${escapeText(data.meta[i].indicator)}<br>${escapeText(data.meta[i].label_vi)}</td><td><input aria-label="${escapeText(data.meta[i].indicator)}" data-index="${i}" inputmode="decimal" value="${state[i]===null?'':escapeText(state[i])}"></td><td>${Scoring.valid(state[i])?'Hợp lệ':state[i]===null?'Thiếu câu trả lời':'Không hợp lệ'}</td></tr>`).join('');
 byId('all').innerHTML='<table><tr><th>Nhóm</th><th>Câu hợp lệ</th><th>Điểm mức độ quan trọng</th></tr>'+groupNames.map(g=>{const ids=data.meta.flatMap((m,i)=>m.group===g?[i]:[]), r=Scoring.summarize(ids.map(i=>state[i]));return `<tr><td>${escapeText(data.meta[ids[0]].group_vi)}</td><td>${r.n}/${r.k}</td><td>${format(r.mean)}</td></tr>`;}).join('')+'</table>';
}
function act(action) {
 const ids=indices();
 if(action==='first') state=[...data.first];
 else if(action==='fill'||action==='empty') state=state.map((v,i)=>ids.includes(i)?action==='fill'?4:null:v);
 else state=Scoring.change(state,ids[0],{missing:null,six:6,decimal:4.5,text:'abc'}[action]);
 render({fill:'Đã điền mức 4 cho cả nhóm.',empty:'Đã xóa cả nhóm.',missing:'Một câu bị bỏ trống. Không điền bù và không lấy trung bình các câu còn lại.',six:'6 nằm ngoài thang 1 đến 5.',decimal:'4,5 không phải lựa chọn nguyên của thang Likert.',text:'Chữ không phải câu trả lời hợp lệ.',first:'Đã nạp phiếu đầu tiên do R tạo.'}[action]);
}
byId('group').innerHTML=groupNames.map(g=>`<option value="${g}">${escapeText(data.meta.find(m=>m.group===g).group_vi)}</option>`).join('');
byId('group').addEventListener('change',e=>{active=e.target.value;render();});
byId('inputs').addEventListener('change',e=>{if(!e.target.matches('input'))return;const raw=e.target.value.trim().replace(',','.');const value=raw===''?null:Number.isFinite(Number(raw))?Number(raw):raw;state=Scoring.change(state,Number(e.target.dataset.index),value);render('Đã cập nhật câu trả lời.');});
document.querySelectorAll('[data-action]').forEach(b=>b.addEventListener('click',()=>act(b.dataset.action)));
const scenarios={complete:{text:'Điền đủ tám câu kinh doanh ở mức 4, sau đó xóa một câu để xem điều kiện tính điểm.',steps:[['Điền đủ câu','fill'],['Bỏ trống một câu','missing'],['Khôi phục đủ câu','fill']]},missing:{text:'Một câu trống khiến nhóm chưa có điểm. Xóa cả nhóm để phân biệt chưa nhập với thiếu một câu.',steps:[['Xóa câu đầu','missing'],['Xóa cả nhóm','empty'],['Nhập đủ câu','fill']]},invalid:{text:'Giá trị ngoài thang, số lẻ và chữ đều không được dùng tính điểm. Sau mỗi lần nhập sai, thử khôi phục.',steps:[['Nhập giá trị 6','six'],['Nhập số 4,5','decimal'],['Nhập chữ','text'],['Khôi phục mức 4','fill']]}};
function scenario(name){active='Bus';state=data.meta.map(()=>4);document.querySelectorAll('[data-scenario]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.scenario===name)));byId('guide').textContent=scenarios[name].text;byId('steps').innerHTML='';scenarios[name].steps.forEach(([label,action],i)=>{const b=document.createElement('button');b.textContent=`Bước ${i+1}. ${label}`;b.disabled=i!==0;b.addEventListener('click',()=>{act(action);b.disabled=true;const next=b.nextElementSibling;if(next)next.disabled=false;});byId('steps').append(b);});render('Đã bắt đầu tình huống với tám câu kinh doanh ở mức 4.');}
document.querySelectorAll('[data-scenario]').forEach(b=>b.addEventListener('click',()=>scenario(b.dataset.scenario)));
byId('rsummary').innerHTML='<table><tr><th>Nhóm</th><th>Trung bình nhóm</th><th>Alpha thô</th></tr>'+data.summary.map(s=>`<tr><td>${escapeText(s.group_vi)}</td><td>${format(Number(s.mean))}</td><td>${format(Number(s.alpha_raw))}</td></tr>`).join('')+'</table>';
scenario('complete');
</script></html>'''
(out / "demo-prototype.html").write_text(page.replace("__PAYLOAD__", payload), encoding="utf-8")
# Parse the generated package and check all ZIP members before handing it over.
import xml.etree.ElementTree as ET
with ZipFile(out / "bang-diem-prototype.xlsx") as z:
    if z.testzip() is not None:
        raise ValueError("XLSX checksum failed")
    for name in z.namelist():
        ET.fromstring(z.read(name))
# Verify the delivered data and recompute bootstrap intervals independently.
import statistics
from html.parser import HTMLParser

assert len(data) == 829 and len(meta) == 49
assert len(read_csv(out / "preliminary-438.csv")) == 438 and len(screening) == 52
assert len({r["indicator"] for r in screening}) == 52
assert len(htmt_rows) == 29 and len(path_rows) == 41
cfa_status = read_csv(out / "cfa-status.csv")[0]
assert cfa_status["converged"] == "TRUE" and cfa_status["admissible"] == "TRUE"
draws = read_csv(out / "pls-bootstrap-draws.csv")
statuses = read_csv(out / "pls-bootstrap-status.csv")
assert len(draws) == len(statuses) == int(bootstrap_counts["attempted"]) == 1000
successful = [r for r, status in zip(draws, statuses) if status["converged"] == "TRUE"]
assert len(successful) == int(bootstrap_counts["successful"])
assert 1000 - len(successful) == int(bootstrap_counts["failed"])

def quantile(values, probability):
    ordered = sorted(values)
    at = (len(ordered) - 1) * probability
    lo = math.floor(at)
    hi = math.ceil(at)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (at - lo)

for r in read_csv(out / "pls-bootstrap-paths.csv"):
    values = [float(draw[r["path"]]) for draw in successful]
    calculated = [statistics.mean(values), statistics.stdev(values), quantile(values, .025), quantile(values, .975)]
    for key, value in zip(["Mean.Boot", "Std.Error", "perc.025", "perc.975"], calculated):
        assert math.isclose(value, float(r[key]), rel_tol=1e-11, abs_tol=1e-12), (r["path"], key)

class LinkCheck(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "href" and value and not value.startswith(("https:", "http:", "#")):
                assert (out / value).is_file(), value

for name in ["demo-prototype.html", "ket-qua-mo-rong.html"]:
    LinkCheck().feed((out / name).read_text(encoding="utf-8"))
verification = "\n".join([
    "Input checks: final 829 x 49; preliminary 438 x 52, all unique indicator codes.",
    "Cached spreadsheet group scores: 8/8 agree with R; scoring scenarios: 7/7 agree with R.",
    "CFA: converged and admissible; HTMT pairs: 28; PLS structural paths: 40.",
    f"Bootstrap: 1000 attempts; {len(successful)} successful; {1000-len(successful)} failed, no redraws.",
    "Bootstrap means, sample standard errors and type-7 percentile limits independently recomputed in Python for all 40 paths.",
    "XLSX ZIP checksums and every XML member parse successfully.",
    "All local links in both HTML files exist.",
    "Excel/LibreOffice formula recalculation has NOT been verified.",
])
(out / "verification.txt").write_text(verification + "\n", encoding="utf-8")
(out / "pipeline-complete.txt").write_text("Full R pipeline and asset validation completed successfully.\n", encoding="utf-8")
print("Created HTML and XLSX. " + verification.replace("\n", " "))
