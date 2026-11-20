"""Run the existing extractor, reconcile page-break duplicates and DA overrides."""
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader
import extract

ROOT = Path(__file__).resolve().parent
EXPECTED = [f'{n}{part}' for n in range(1, 6) for part in 'ABC']

def main():
    folder = ROOT / 'data/da'
    manifest = folder / 'papers-manifest.json'
    raw_path = folder / 'papers-extracted-raw.json'
    extract.main(['--papers', str(manifest), '--output', str(raw_path)])
    raw = json.loads(raw_path.read_text(encoding='utf-8'))
    overrides = json.loads((ROOT / 'data/overrides.json').read_text(encoding='utf-8'))
    output, records = [], []
    for paper in json.loads(manifest.read_text(encoding='utf-8')):
        grouped = {}
        for q in raw:
            if q['paper_id'] == paper['id']:
                grouped.setdefault(q['qno'], []).append(q)
        if list(grouped) != EXPECTED:
            raise ValueError(f'{paper["id"]}: unexpected question sequence {list(grouped)}')
        selected = []
        for number, copies in grouped.items():
            # The PDF repeats headings at page breaks; prefer the complete copy.
            q = max(copies, key=lambda item: (item['marks'] is not None, item['co'] is not None, len(item['text']))).copy()
            if q['id'] in overrides:
                q.update(text=overrides[q['id']], from_image=True)
            if q['marks'] is None or not q['text'].strip():
                raise ValueError(f'{q["id"]}: missing marks or transcription')
            selected.append(q)
        if sum(q['marks'] for q in selected) != 50:
            raise ValueError(f'{paper["id"]}: marks do not sum to 50')
        output.extend(selected)
        path = ROOT / paper['file']
        records.append({'id': paper['id'], 'file': paper['file'], 'url': paper['url'],
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'pages': len(PdfReader(path).pages), 'questions': len(selected),
                        'raw_records': sum(len(v) for v in grouped.values()), 'marks': 50})
    (folder / 'papers-extracted.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    evidence = ROOT / '.artifacts/da-module-tests'
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / 'paper-sources.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(records, indent=2))

if __name__ == '__main__':
    main()
