"""Exercise the delivered workbook in real LibreOffice Calc through UNO, without a GUI."""
import argparse
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

# Flatpak ships UNO beside soffice rather than in Python's site-packages.
if Path("/app/libreoffice/program/pyuno.so").is_file():
    sys.path.insert(0, "/app/libreoffice/program")
    os.environ.setdefault("URE_BOOTSTRAP", "vnd.sun.star.pathname:/app/libreoffice/program/fundamentalrc")
    os.environ.setdefault("UNO_PATH", "/app/libreoffice/program")
import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.document.MacroExecMode import NEVER_EXECUTE
from com.sun.star.document.UpdateDocMode import NO_UPDATE

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(__file__).resolve().parent
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def prop(name, value):
    item = PropertyValue()
    item.Name, item.Value = name, value
    return item


def require(condition, message):
    if not condition:
        raise ValueError(message)


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def equal(actual, expected):
    if expected is None:
        return actual == ""
    return isinstance(actual, (int, float)) and math.isclose(actual, expected, abs_tol=1e-10)


def value(cell):
    require(cell.getError() == 0, f"Formula error {cell.getError()}: {cell.getFormula()}")
    return cell.getValue() if cell.getString() != "" else ""


def run(args):
    workbook = args.workbook.resolve()
    source = args.source.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    results = []
    cases = [
        ("du_8_cau", 4, 4.0, "Đủ dữ liệu"),
        ("thieu_1_cau", None, None, "Thiếu hoặc không hợp lệ"),
        ("trong_ca_nhom", None, None, "Chưa nhập"),
        ("nhap_0", 0, None, "Thiếu hoặc không hợp lệ"),
        ("nhap_6", 6, None, "Thiếu hoặc không hợp lệ"),
        ("nhap_4_5", 4.5, None, "Thiếu hoặc không hợp lệ"),
        ("nhap_chu", "abc", None, "Thiếu hoặc không hợp lệ"),
    ]
    r_cases = csv_rows(source / "scoring-scenarios.csv")
    require([r["scenario"] for r in r_cases] == [r[0] for r in cases], "R scenario labels differ")
    require([r["score"] for r in r_cases] == ["4", "", "", "", "", "", ""], "R scenario results differ")
    metadata = csv_rows(ROOT / "analysis/indicators.csv")
    summary = csv_rows(source / "group-summary.csv")
    r_scores = csv_rows(source / "group-scores.csv")[0]
    raw = csv_rows(source / "synthetic-829.csv")[0]
    subprocess.run([sys.executable, "-I", str(BASE / "check-workbook.py"), str(workbook), "--source", str(source)], check=True)
    version = subprocess.run([args.soffice, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="q5s4-calc-") as temp:
        temporary = Path(temp)
        poisoned = temporary / "stale-cache.xlsx"
        poisoned_count = 0
        with ZipFile(workbook) as original, ZipFile(poisoned, "w", ZIP_DEFLATED) as archive:
            for name in original.namelist():
                payload = original.read(name)
                if name.startswith("xl/worksheets/") and name.endswith(".xml"):
                    sheet = ET.fromstring(payload)
                    for node in sheet.iter(f"{{{NS}}}c"):
                        if node.find(f"{{{NS}}}f") is not None:
                            node.find(f"{{{NS}}}v").text = "999"
                            poisoned_count += 1
                    payload = ET.tostring(sheet, encoding="utf-8", xml_declaration=True)
                archive.writestr(name, payload)
        pipe = "q5s4_" + uuid.uuid4().hex
        command = [args.soffice, "-env:UserInstallation=" + (temporary / "profile").as_uri(), "--headless", "--nologo", "--nodefault", "--nofirststartwizard", "--accept=pipe,name=" + pipe + ";urp;StarOffice.ComponentContext"]
        with (evidence / "libreoffice-console.log").open("w") as console:
            process = subprocess.Popen(command, stdout=console, stderr=subprocess.STDOUT, env={key: value for key, value in os.environ.items() if key != "SAL_USE_VCLPLUGIN"})
            desktop = None
            document = None
            try:
                local = uno.getComponentContext()
                resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
                deadline = time.monotonic() + 25
                while True:
                    try:
                        context = resolver.resolve("uno:pipe,name=" + pipe + ";urp;StarOffice.ComponentContext")
                        desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
                        break
                    except Exception:
                        if time.monotonic() > deadline or process.poll() is not None:
                            raise
                        time.sleep(0.2)

                def load(path):
                    doc = desktop.loadComponentFromURL(path.as_uri(), "_blank", 0, (prop("Hidden", True), prop("ReadOnly", False), prop("MacroExecutionMode", NEVER_EXECUTE), prop("UpdateDocMode", NO_UPDATE)))
                    require(doc is not None, f"Cannot open {path}")
                    doc.enableAutomaticCalculation(True)
                    doc.calculateAll()
                    return doc

                def save_reopen(path):
                    nonlocal document
                    document.calculateAll()
                    document.storeAsURL(path.as_uri(), (prop("FilterName", "Calc MS Excel 2007 XML"), prop("Overwrite", True)))
                    document.close(True)
                    document = load(path)

                document = load(poisoned)
                for index, group in enumerate(summary, 2):
                    actual = value(document.Sheets["Diem nhom"].getCellRangeByName(f"D{index}"))
                    expected = float(r_scores[group["group"]])
                    require(equal(actual, expected), f"Stale cache not recalculated {group['group']}: {actual}")
                    results.append({"phase": "stale-cache-recalculated", "group": group["group"], "expected": expected, "actual": actual, "pass": True})
                for index, case in enumerate(cases, 2):
                    actual = value(document.Sheets["Tinh huong"].getCellRangeByName(f"J{index}"))
                    state = document.Sheets["Tinh huong"].getCellRangeByName(f"S{index}").getString()
                    require(equal(actual, case[2]) and state == case[3], f"Scenario sheet differs: {case[0]} {actual!r} {state}")
                    results.append({"phase": "scenario-sheet-recalculated", "case": case[0], "expected": case[2], "actual": actual, "status": state, "pass": True})
                save_reopen(evidence / "recalculated.xlsx")
                subprocess.run([sys.executable, "-I", str(BASE / "check-workbook.py"), str(evidence / "recalculated.xlsx"), "--source", str(source)], check=True)
                for index, group in enumerate(summary, 2):
                    positions = [i for i, row in enumerate(metadata, 2) if row["group"] == group["group"]]
                    for label, entry, expected, state in cases:
                        inputs = document.Sheets["Bang diem"]
                        for pos in positions:
                            inputs.getCellRangeByName(f"D{pos}").setValue(4)
                        targets = positions if label == "trong_ca_nhom" else [positions[0]]
                        for pos in targets:
                            target = inputs.getCellRangeByName(f"D{pos}")
                            if entry is None:
                                # VALUE | DATETIME | STRING | FORMULA; preserve validation and formatting.
                                target.clearContents(1 | 2 | 4 | 16)
                            elif isinstance(entry, str):
                                target.setString(entry)
                            else:
                                target.setValue(entry)
                        document.calculateAll()
                        if group["group"] == "Bus":
                            save_reopen(evidence / (label + ".xlsx"))
                        score = document.Sheets["Diem nhom"].getCellRangeByName(f"D{index}")
                        actual = value(score)
                        actual_state = document.Sheets["Diem nhom"].getCellRangeByName(f"E{index}").getString()
                        require(score.getFormula().startswith("="), f"Formula lost: {group['group']}")
                        require(equal(actual, expected) and actual_state == state, f"Edit/recalc failed {group['group']}/{label}: {actual!r}, {actual_state}")
                        for other_index, other in enumerate(summary, 2):
                            if other_index != index:
                                other_value = value(document.Sheets["Diem nhom"].getCellRangeByName(f"D{other_index}"))
                                require(equal(other_value, float(r_scores[other["group"]])), f"Unrelated group changed: {other['group']}")
                        results.append({"phase": "edit-recalculate", "group": group["group"], "case": label, "input": entry, "expected": expected, "actual": actual, "status": actual_state, "saved_reopened": group["group"] == "Bus", "pass": True})
                    for pos in positions:
                        document.Sheets["Bang diem"].getCellRangeByName(f"D{pos}").setValue(float(raw[metadata[pos - 2]["indicator"]]))
                    document.calculateAll()
                    require(equal(value(document.Sheets["Diem nhom"].getCellRangeByName(f"D{index}")), float(r_scores[group["group"]])), f"Restore failed {group['group']}")
                save_reopen(evidence / "restored.xlsx")
                for sheet in document.Sheets:
                    sheet.IsVisible = True
                    sheet.setPrintAreas(())
                scores = document.Sheets["Diem nhom"]
                document.getCurrentController().setActiveSheet(scores)
                for sheet in document.Sheets:
                    if sheet.Name != "Diem nhom":
                        sheet.IsVisible = False
                scores.setPrintAreas((scores.getCellRangeByName("A1:F13").getRangeAddress(),))
                style = document.StyleFamilies.getByName("PageStyles").getByName(scores.PageStyle)
                style.IsLandscape = True
                style.Width, style.Height = 29700, 21000
                style.ScaleToPagesX, style.ScaleToPagesY = 1, 1
                document.calculateAll()
                document.storeToURL((evidence / "calc-scores.pdf").as_uri(), (prop("FilterName", "calc_pdf_Export"),))
                document.close(True)
                document = None
            finally:
                if document is not None:
                    document.close(True)
                if desktop is not None:
                    desktop.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    process.wait(timeout=5)
    result = {"application": version, "mode": "headless Calc via UNO, real document load/edit/calculateAll/store/reopen", "workbook": str(workbook), "workbook_sha256": hashlib.sha256(workbook.read_bytes()).hexdigest(), "poisoned_formula_caches": poisoned_count, "checks": results}
    (evidence / "libreoffice-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(BASE / "check-workbook.py"), str(evidence / "restored.xlsx"), "--source", str(source)], check=True)
    print(f"PASS {version}: {len(results)} checks; {poisoned_count} stale caches poisoned; edited all eight groups; seven Bus cases saved/reopened; results {evidence}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--soffice", default="libreoffice")
    parser.add_argument("--source", type=Path, default=ROOT / "output-standard")
    parser.add_argument("--evidence", type=Path, default=ROOT / "spreadsheet/verification")
    run(parser.parse_args())
