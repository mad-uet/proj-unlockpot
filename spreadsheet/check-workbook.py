"""Verify the delivered XLSX against the independent R outputs. No formula evaluator."""
import argparse
import csv
import math
import posixpath
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
ROOT = Path(__file__).resolve().parents[1]


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected, label):
    require(isinstance(actual, (int, float)) and math.isclose(actual, float(expected), rel_tol=1e-10, abs_tol=1e-12),
            f"{label}: {actual!r} != {expected!r}")


def read_book(path):
    with ZipFile(path) as archive:
        require(archive.testzip() is None, "ZIP CRC failed")
        names = set(archive.namelist())
        require(not any("externalLink" in n or "vbaProject" in n for n in names), "External links/macros")
        for name in names:
            if name.endswith((".xml", ".rels")):
                root = ET.fromstring(archive.read(name))
                if name.endswith(".rels"):
                    folder = posixpath.dirname(posixpath.dirname(name))
                    for link in root:
                        require(link.get("TargetMode") != "External", f"External relationship: {name}")
                        target = link.get("Target", "")
                        resolved = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(folder, target))
                        require(resolved in names, f"Missing relationship: {resolved}")
        strings = []
        if "xl/sharedStrings.xml" in names:
            strings = ["".join(node.itertext()) for node in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relations = {r.get("Id"): r.get("Target") for r in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        styles = ET.fromstring(archive.read("xl/styles.xml"))
        style_count = len(styles.find("s:cellXfs", NS))
        result = {}
        for sheet in workbook.find("s:sheets", NS):
            target = relations[sheet.get(f"{{{OFFICE_REL}}}id")]
            name = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            root = ET.fromstring(archive.read(name))
            cells = {}
            for cell in root.findall("s:sheetData/s:row/s:c", NS):
                require(int(cell.get("s", "0")) < style_count, f"Bad style in {name}")
                kind = cell.get("t")
                text = cell.findtext("s:v", default="", namespaces=NS)
                if kind == "inlineStr":
                    value = "".join(cell.find("s:is", NS).itertext())
                elif kind == "s":
                    value = strings[int(text)]
                elif kind in ("str", "e"):
                    value = text
                elif kind == "b":
                    value = bool(int(text))
                else:
                    value = float(text) if text else ""
                require(kind != "e", f"Excel error {sheet.get('name')}!{cell.get('r')}: {text}")
                cells[cell.get("r")] = (value, cell.findtext("s:f", namespaces=NS))
            result[sheet.get("name")] = (cells, root)
        return result


def check(path, source):
    book = read_book(path)
    metadata = csv_rows(ROOT / "analysis/indicators.csv")
    summary = csv_rows(source / "group-summary.csv")
    first = csv_rows(source / "group-scores.csv")[0]
    data = csv_rows(source / "synthetic-829.csv")
    cells, sheet = book["Bang diem"]
    require(len(metadata) == 49, "Expected 49 indicators")
    for index, row in enumerate(metadata, 2):
        for column, field in [("A", "group_vi"), ("B", "indicator"), ("C", "label_vi")]:
            require(cells[f"{column}{index}"][0] == row[field], f"Indicator mismatch at {column}{index}")
        close(cells[f"D{index}"][0], data[0][row["indicator"]], f"Initial answer {index}")
        close(cells[f"E{index}"][0], 1, f"Validity {index}")
        require(bool(cells[f"E{index}"][1]), f"Missing validity formula {index}")
    require(sum(address.startswith("B") for address in cells) == 50, "Wrong indicator row count")
    validations = sheet.findall("s:dataValidations/s:dataValidation", NS)
    require(any(v.get("sqref") == "D2:D50" and v.get("type") == "whole" and
                v.findtext("s:formula1", namespaces=NS) == "1" and v.findtext("s:formula2", namespaces=NS) == "5"
                for v in validations), "Missing integer 1..5 input validation")
    scores = book["Diem nhom"][0]
    require([int(r["k"]) for r in summary] == [8, 7, 7, 4, 3, 9, 6, 5], "Wrong group sizes")
    for index, row in enumerate(summary, 2):
        require(scores[f"A{index}"][0] == row["group_vi"], f"Wrong group {index}")
        for column in ("B", "C"):
            close(scores[f"{column}{index}"][0], row["k"], f"Group count {index}")
        close(scores[f"D{index}"][0], first[row["group"]], f"Group score {row['group']}")
        close(scores[f"F{index}"][0], first[row["group"]], f"R reference {row['group']}")
        require(bool(scores[f"D{index}"][1]), f"Missing group formula {index}")
    scenarios = book["Tinh huong"][0]
    cases = csv_rows(source / "scoring-scenarios.csv")
    require([r["scenario"] for r in cases] == ["du_8_cau", "thieu_1_cau", "trong_ca_nhom", "nhap_0", "nhap_6", "nhap_4_5", "nhap_chu"], "Wrong R scenarios")
    for index, case in enumerate(cases, 2):
        value, formula = scenarios[f"J{index}"]
        require(bool(formula), f"Missing scenario formula {index}")
        if case["score"]:
            close(value, case["score"], f"Scenario {index}")
        else:
            require(value == "", f"Invalid scenario scored: {case['scenario']}")
    raw = book["Du lieu 829"][0]
    require(sum(a.startswith("A") and a[1:].isdigit() for a in raw) == 830, "Wrong raw data row count")
    def column(number):
        label = ""
        while number:
            number, rest = divmod(number - 1, 26)
            label = chr(65 + rest) + label
        return label
    for index, row in enumerate(data, 2):
        close(raw[f"A{index}"][0], row["id"], f"Raw id {index}")
        for offset, indicator in enumerate(metadata, 3):
            close(raw[f"{column(offset)}{index}"][0], row[indicator["indicator"]], f"Raw data {index}/{offset}")
    for name, csv_name, fields, start in [
        ("Ket qua R", "group-summary.csv", ["k", "n", "mean", "sd", "alpha_raw"], 2),
        ("CR AVE", "cfa-cr-ave.csv", ["min_loading", "max_loading", "CR", "AVE"], 2),
        ("HTMT", "htmt-pairs.csv", ["HTMT"], 3),
        ("PLS bootstrap", "pls-bootstrap-paths.csv", ["Original", "Std.Error", "perc.025", "perc.975"], 3),
        ("Trang thai bootstrap", "pls-bootstrap-counts.csv", ["attempted", "successful", "failed", "seed"], 1),
        ("Sang loc 438", "preliminary-screening.csv", ["citc", "alpha_before", "alpha_if_deleted"], 3),
        ("Doi chieu 3 ma", "preliminary-authored-removals.csv", ["simulated_citc", "alpha_before", "alpha_after_authored_list"], 3),
    ]:
        for index, row in enumerate(csv_rows(source / csv_name), 2):
            for offset, field in enumerate(fields, start):
                close(book[name][0][f"{column(offset)}{index}"][0], row[field], f"{name}/{index}/{field}")
    cfa = {r["metric"]: r["value"] for r in csv_rows(source / "cfa-fit-measures.csv")}
    for index, metric in enumerate(["chisq.scaled", "df.scaled", "pvalue.scaled", "cfi.scaled", "tli.scaled", "rmsea.scaled", "srmr"], 2):
        close(book["CFA WLSMV"][0][f"B{index}"][0], cfa[metric], metric)
    r2 = [r for r in csv_rows(source / "pls-inner-summary.csv") if r["construct"] in first]
    for index, row in enumerate(r2, 2):
        close(book["PLS R2"][0][f"B{index}"][0], row["R2"], f"R2 {index}")
    print(f"PASS {path}: ZIP/XML/relationships/styles; 49 codes; 829 x 49 values; 8 scores and 7 scenarios versus R; CFA/CR/AVE/28 HTMT/40 PLS/bootstrap/screening. Formula execution requires LibreOffice check.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--source", type=Path, default=ROOT / "output-standard")
    args = parser.parse_args()
    check(args.workbook, args.source)
