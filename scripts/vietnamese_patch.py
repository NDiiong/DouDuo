import json
import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "scripts/vietnamese_translations.json").read_text(encoding="utf-8"))
report_path = root / "vietnamese-report.txt"
han = re.compile(r"[\u3400-\u9fff]")
translated_sources = {}

for name, edits in manifest.items():
    path = root / name
    if name != "project.yml" and not path.is_relative_to(root / "DouDuo"):
        raise SystemExit(f"Không hỗ trợ tệp dịch: {name}")
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for number, original, replacement in edits:
        if not 1 <= number <= len(lines) or lines[number - 1].rstrip("\n") != original:
            error = f"{name}:{number} không khớp mã nguồn đã rà soát."
            report_path.write_text(error + "\n", encoding="utf-8")
            raise SystemExit(error)
        ending = "\n" if lines[number - 1].endswith("\n") else ""
        lines[number - 1] = replacement + ending
    translated_sources[path] = "".join(lines)

for path, translated in translated_sources.items():
    path.write_text(translated, encoding="utf-8")

report = [
    f"Dòng mã đã cập nhật: {sum(len(edits) for edits in manifest.values())}",
    f"Tệp đã cập nhật: {len(manifest)}",
    "",
    "Các dòng có chữ Hán trong Swift và cấu hình quyền sau khi áp dụng patch.",
    "Danh sách gồm cả chuỗi giao diện, mã tích hợp, giá trị lưu trữ và dữ liệu mẫu.",
    "",
]
for path in sorted((root / "DouDuo").rglob("*.swift")) + [root / "project.yml"]:
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        value = line.strip()
        if value.startswith(("//", "/*", "*", "#")):
            continue
        if han.search(value):
            report.append(f"{path.relative_to(root)}:{number} | {value}")

report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report[:2]))
