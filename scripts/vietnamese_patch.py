"""Starter Vietnamese translation patch for DouDuo SwiftUI labels.

Only replaces exact Chinese literals in UI contexts. Does not attempt to
translate network payloads, API field names or all dynamically generated text.
Edit vietnamese_translations.json to expand coverage, then run GitHub Actions.
"""
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[1]
translations = json.loads((root / 'scripts/vietnamese_translations.json').read_text(encoding='utf-8'))
# SwiftUI UI entry points (deliberately scoped to avoid changing API keys).
ui = r'(?:Text|Label|Button|Toggle|Section|TextField|SecureField|Picker|Menu|NavigationLink|ContentUnavailableView|ProgressView|LabeledContent|GroupBox|ShareLink|Link|navigationTitle|accessibilityLabel|accessibilityHint|alert|confirmationDialog)'
pattern = re.compile(r'(?P<head>\b' + ui + r'\s*\(\s*)"(?P<value>(?:\\.|[^"\\])*)"')
chinese = re.compile(r'[\u3400-\u9fff]')
changed = 0
remaining = set()
scanned = 0
for file in (root / 'DouDuo').rglob('*.swift'):
    source = file.read_text(encoding='utf-8')
    scanned += 1
    def patch(m):
        global changed
        s = m.group('value')
        if chinese.search(s):
            if s in translations:
                changed += 1
                replacement = translations[s].replace('\\', r'\\').replace('"', r'\"')
                return m.group('head') + '"' + replacement + '"'
            remaining.add(s)
        return m.group(0)
    output = pattern.sub(patch, source)
    if source != output:
        file.write_text(output, encoding='utf-8')
report = [f'Swift files scanned: {scanned}', f'UI labels replaced: {changed}',
          f'Untranslated UI labels found: {len(remaining)}', '',
          'Add exact Chinese text below to scripts/vietnamese_translations.json:', '']
report.extend(sorted(remaining))
(root / 'vietnamese-report.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
print('\n'.join(report[:4]))
