"""Finish the validated prototype workbook, preserving all R data and analysis sheets."""
import argparse
import csv
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
ET.register_namespace("", MAIN)
ET.register_namespace("r", REL)


def tag(name):
    return f"{{{MAIN}}}{name}"


def element(parent, name, text=None, **attrs):
    node = ET.SubElement(parent, tag(name), {key: str(value) for key, value in attrs.items()})
    node.text = text
    return node


def xml(node):
    return ET.tostring(node, encoding="utf-8", xml_declaration=True)


def rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def cell(row, address, value, formula=None, style=0):
    node = element(row, "c", r=address, s=style)
    if formula is not None:
        if isinstance(value, str):
            node.set("t", "str")
        element(node, "f", formula)
        element(node, "v", str(value))
    elif isinstance(value, str):
        node.set("t", "inlineStr")
        element(element(node, "is"), "t", value)
    elif value is not None:
        element(node, "v", str(value))
    return node


def layout(sheet, widths, height=34):
    view = sheet.find(tag("sheetViews"))
    if view is None:
        view = ET.Element(tag("sheetViews"))
        sheet.insert(0, view)
        element(element(view, "sheetView", workbookViewId=0), "pane", ySplit=1, topLeftCell="A2", activePane="bottomLeft", state="frozen")
    cols = sheet.find(tag("cols"))
    if cols is None:
        cols = ET.Element(tag("cols"))
        sheet.insert(1, cols)
    cols.clear()
    for index, width in enumerate(widths, 1):
        element(cols, "col", min=index, max=index, width=width, customWidth=1)
    for row in sheet.find(tag("sheetData")):
        row.set("ht", str(40 if row.get("r") == "1" else height))
        row.set("customHeight", "1")
    element(sheet, "printOptions", horizontalCentered=1)
    element(sheet, "pageMargins", left=0.3, right=0.3, top=0.4, bottom=0.4, header=0.2, footer=0.2)
    element(sheet, "pageSetup", paperSize=9, orientation="landscape", fitToWidth=1, fitToHeight=0)


def main(source):
    prototype = source / "bang-diem-prototype.xlsx"
    with ZipFile(prototype) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    metadata = rows(ROOT / "analysis/indicators.csv")
    summary = rows(source / "group-summary.csv")
    first = rows(source / "group-scores.csv")[0]
    instructions = [
        ("BẢNG TÍNH ĐIỂM MỨC ĐỘ QUAN TRỌNG", "Hướng dẫn sử dụng"),
        ("1. Lưu bản làm việc", "Lưu một bản sao XLSX trước khi sửa. Chọn Bang diem, nhập ở các ô màu vàng D2:D50. Các giá trị ban đầu là phiếu số 1 của dữ liệu tổng hợp do R tạo."),
        ("2. Câu hỏi", "Bạn đánh giá mức độ quan trọng của từng chỉ báo đối với năng lực quản trị như thế nào? Đây là nhận định về tầm quan trọng, không phải mức năng lực hiện có của tổ chức."),
        ("3. Nhập câu trả lời", "Chỉ nhập số nguyên 1 đến 5. Mức 1: Cực kỳ không quan trọng. Mức 2: Không quan trọng. Mức 3: Trung lập. Mức 4: Quan trọng. Mức 5: Cực kỳ quan trọng."),
        ("Nhãn mức 3", "Thân bài trang 8 dùng neutral, trung lập; phụ lục dùng general. Demo chọn nhãn trung lập và giữ ghi chú khác biệt. Bản dịch phục vụ học tập, chưa kiểm định tại Việt Nam."),
        ("4. Xem kết quả", "Mở Diem nhom, đọc số câu hợp lệ ở C và điểm ở D. Cột F là mốc R của phiếu số 1, cố định để đối chiếu trước khi sửa, không phải điểm của phiếu bạn vừa nhập."),
        ("5. Khi thiếu hoặc sai", "Một ô trống, chữ, số lưu dạng chữ, 0, 6 hoặc 4,5 làm nhóm không có điểm. E ở Bang diem bằng 0 chỉ ô cần sửa. Cả nhóm trống ghi Chưa nhập. Sửa lại ô đó thành số nguyên 1 đến 5, điểm nhóm sẽ xuất hiện."),
        ("6. Tính lại", "Excel: Formulas > Calculation Options > Automatic; F9 để tính lại. LibreOffice Calc: Data > Calculate > AutoCalculate; Ctrl+Shift+F9 để tính lại toàn bộ. Lưu và mở lại XLSX sau khi thử."),
        ("7. Thử tình huống", "Tinh huong có bảy ví dụ, cột J là điểm, cột S là trạng thái; các cột kiểm tra K:R được ẩn. Thử nhập tám số 4 ở Bang diem D2:D9, xem Diem nhom D2 bằng 4; xóa D2, điểm phải trống; sửa D2 về 4, điểm phải trở lại 4."),
        ("Cảnh báo nhập liệu", "Nhập trực tiếp giá trị sai có thể bị ứng dụng chặn. Dán dữ liệu có thể vượt cảnh báo, công thức vẫn phải từ chối. Dùng bản sao khi thử. Không sửa các ô công thức hoặc cột mã, không chèn/xóa hàng."),
        ("Quy tắc demo", "Lấy trung bình không trọng số chỉ khi toàn bộ câu trong nhóm là số nguyên 1 đến 5. Không điền bù, không đảo điểm, không tính tổng toàn thang, không xếp loại năng lực. Đây là lựa chọn của demo, không gán cho tác giả."),
        ("Danh mục và nguồn", "49 mã thuộc tám nhóm theo Appendix F, Table A4 trang 23, Zheng, Su và Liu, 2024, Systems 12, 497, DOI 10.3390/systems12110497. Số mã Bus/Fin/HR/LI/Mkg/OM/PM/Proc là 8/7/7/4/3/9/6/5."),
        ("Sai lệch nguồn", "Abstract ghi 47, Bảng 1 có 52 mã ban đầu, A2 có tập 52 mã khác. Demo giữ 49 mã có nội dung ở A4; không bịa Bus_9 đến Bus_11 hoặc bỏ mã để ép về 47."),
        ("Dữ liệu và mốc R", "Du lieu 829 giữ 829 phiếu tổng hợp, seed 20261104; Ket qua R là thống kê cố định trên mẫu này. Sửa Bang diem không chạy lại R, CFA hoặc PLS. Dữ liệu không phải khảo sát gốc hay tổ chức thật."),
        ("Các trang phân tích", "CFA WLSMV, CR AVE, HTMT, PLS bootstrap, PLS R2 và Trang thai bootstrap giữ kết quả mẫu chính. Sang loc 438 và Doi chieu 3 ma dùng mẫu sơ bộ tổng hợp 438 phiếu riêng, seed 20261105."),
        ("Giới hạn phân tích", "Tám nhân tố là giả định sinh dữ liệu. HTMT dùng Pearson tuyệt đối, chỉ ước lượng điểm. PLS-PM dùng năm biến giả vai trò với chủ đầu tư tham chiếu, hệ số chuẩn hóa; 1000 bootstrap, không suy ra nhân quả hoặc chênh lệch Likert thô."),
        ("Bằng chứng kiểm tra", "Kiểm tra cached values chỉ đối chiếu giá trị lưu sẵn; kiểm tra ứng dụng phải mở, sửa ô, tính lại, lưu và mở lại bằng LibreOffice hoặc Excel."),
    ]
    guide = ET.Element(tag("worksheet"))
    body = element(guide, "sheetData")
    for index, values in enumerate(instructions, 1):
        row = element(body, "row", r=index)
        for column, value in zip("AB", values):
            cell(row, f"{column}{index}", value, style=1 if index == 1 else 0)
    layout(guide, [29, 112], 58)
    parts["xl/worksheets/sheet1.xml"] = xml(guide)
    inputs = ET.fromstring(parts["xl/worksheets/sheet2.xml"])
    for row in inputs.find(tag("sheetData")):
        for node in list(row):
            address = node.get("r")
            if address[0] not in "ABCDE":
                row.remove(node)
            elif address.startswith("D") and row.get("r") != "1":
                node.set("s", "2")
    inputs.find(f"{tag('sheetData')}/{tag('row')}/{tag('c')}[@r='E1']/{tag('is')}/{tag('t')}").text = "Hợp lệ 1/0"
    layout(inputs, [24, 19, 68, 20, 14], 38)
    parts["xl/worksheets/sheet2.xml"] = xml(inputs)
    scores = ET.Element(tag("worksheet"))
    body = element(scores, "sheetData")
    header = element(body, "row", r=1)
    for column, value in zip("ABCDEF", ["Nhóm năng lực", "Số câu cần", "Số câu hợp lệ", "Điểm mức độ quan trọng", "Trạng thái", "Mốc R phiếu số 1"]):
        cell(header, f"{column}1", value, style=1)
    for index, group in enumerate(summary, 2):
        positions = [i for i, m in enumerate(metadata, 2) if m["group"] == group["group"]]
        start, end, count = positions[0], positions[-1], len(positions)
        row = element(body, "row", r=index)
        cell(row, f"A{index}", group["group_vi"])
        cell(row, f"B{index}", count)
        cell(row, f"C{index}", count, f"SUM('Bang diem'!E{start}:E{end})")
        cell(row, f"D{index}", float(first[group["group"]]), f'IF(C{index}=B{index},AVERAGE(\'Bang diem\'!D{start}:D{end}),"")', 3)
        cell(row, f"E{index}", "Đủ dữ liệu", f'IF(COUNTA(\'Bang diem\'!D{start}:D{end})=0,"Chưa nhập",IF(C{index}=B{index},"Đủ dữ liệu","Thiếu hoặc không hợp lệ"))')
        cell(row, f"F{index}", float(first[group["group"]]), style=3)
    for index, text in [(11, "Điểm là mức độ quan trọng, không phải năng lực hiện có."), (12, "Cột F cố định theo R; sau khi sửa, chỉ đọc điểm mới ở D."), (13, "Ô D trống nghĩa là chưa có điểm. Xem trạng thái ở E và sửa ô có kiểm tra bằng 0 ở Bang diem.")]:
        row = element(body, "row", r=index)
        cell(row, f"A{index}", text)
    merges = element(scores, "mergeCells", count=3)
    for index in (11, 12, 13):
        element(merges, "mergeCell", ref=f"A{index}:F{index}")
    layout(scores, [25, 13, 15, 24, 30, 22], 38)
    parts["xl/worksheets/sheet14.xml"] = xml(scores)
    scenarios = ET.fromstring(parts["xl/worksheets/sheet3.xml"])
    layout(scenarios, [24] + [8] * 8 + [22] + [10] * 8 + [29], 38)
    for col in scenarios.find(tag("cols")):
        if 11 <= int(col.get("min")) <= 18:
            col.set("hidden", "1")
    parts["xl/worksheets/sheet3.xml"] = xml(scenarios)
    workbook = ET.fromstring(parts["xl/workbook.xml"])
    sheets = workbook.find(tag("sheets"))
    sheets.insert(2, ET.Element(tag("sheet"), {"name": "Diem nhom", "sheetId": "14", f"{{{REL}}}id": "rId15"}))
    calc = workbook.find(tag("calcPr"))
    calc.set("calcMode", "auto")
    calc.set("forceFullCalc", "1")
    parts["xl/workbook.xml"] = xml(workbook)
    relations = ET.fromstring(parts["xl/_rels/workbook.xml.rels"])
    ET.SubElement(relations, f"{{{PKG}}}Relationship", {"Id": "rId15", "Type": REL + "/worksheet", "Target": "worksheets/sheet14.xml"})
    parts["xl/_rels/workbook.xml.rels"] = xml(relations)
    content = ET.fromstring(parts["[Content_Types].xml"])
    ET.SubElement(content, f"{{{CT}}}Override", {"PartName": "/xl/worksheets/sheet14.xml", "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"})
    parts["[Content_Types].xml"] = xml(content)
    parts["xl/styles.xml"] = f'''<?xml version="1.0" encoding="utf-8"?>
<styleSheet xmlns="{MAIN}"><fonts count="2"><font><sz val="12"/><name val="Times New Roman"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="12"/><name val="Times New Roman"/></font></fonts><fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF244C61"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="4"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="0" fillId="3" borderId="0" xfId="0" applyFill="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'''.encode()
    target = BASE / "bang-diem-muc-do-quan-trong.xlsx"
    with tempfile.TemporaryDirectory(prefix="q5s4-") as temporary:
        candidate = Path(temporary) / target.name
        with ZipFile(candidate, "w", ZIP_DEFLATED) as archive:
            for name, payload in parts.items():
                archive.writestr(name, payload)
        subprocess.run([sys.executable, "-I", str(BASE / "check-workbook.py"), str(candidate), "--source", str(source)], check=True)
        target.write_bytes(candidate.read_bytes())
    source_label = source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else str(source)
    used = [prototype, ROOT / "analysis/indicators.csv"] + sorted(source.glob("*.csv"))
    with (BASE / "source-sha256.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "sha256"])
        for path in used:
            writer.writerow([str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), hashlib.sha256(path.read_bytes()).hexdigest()])
    (BASE / "source-path.txt").write_text(source_label + "\n", encoding="utf-8")
    cases = rows(source / "scoring-scenarios.csv")
    if [case["score"] for case in cases] != ["4", "", "", "", "", "", ""]:
        raise ValueError("R scenario results differ from the recorded expectations")
    data_rows = [
        ["Đủ dữ liệu", "4; 4; 4; 4; 4; 4; 4; 4", "8/8", "32 / 8 = 4", "Đủ dữ liệu", "du_8_cau"],
        ["Thiếu một ô", "trống; 4; 4; 4; 4; 4; 4; 4", "7/8", "Không có điểm", "Thiếu hoặc không hợp lệ", "thieu_1_cau"],
        ["Nhập giá trị 6", "6; 4; 4; 4; 4; 4; 4; 4", "7/8", "Không có điểm", "Thiếu hoặc không hợp lệ", "nhap_6"],
    ]
    with (BASE / "tinh-huong-nhap-lieu.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Tình huống", "Tám câu trả lời nhóm kinh doanh", "Hợp lệ", "Điểm mức độ quan trọng", "Trạng thái", "Mã tình huống R"])
        writer.writerows(data_rows)
    print(f"Wrote {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, nargs="?", default=None, help="Thư mục đầu ra R (mặc định: output-standard)")
    parser.add_argument("--source", dest="source_opt", type=Path, default=None, help="Alias tùy chọn cho positional source")
    arguments = parser.parse_args()
    main((arguments.source_opt or arguments.source or ROOT / "output-standard").resolve())
