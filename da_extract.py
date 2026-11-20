"""Extract read-only DA decks and formula book, preserving slide/page numbers."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
FILES = ['Module 1- Introduction to Data Analytics.pptx', 'DA-Mod-2.pptx',
         'Module 3 - part_A.pptx', 'Module 3 Hypothesis testing.pptx',
         'Module 4 (1).pptx', 'Module 5 updated new.pptx', 'DA Formula Book_ Endterm.pdf']

def extract(source, output):
    output.mkdir(parents=True, exist_ok=True)
    documents = []
    for name in FILES:
        path = source / name
        if path.suffix == '.pptx':
            with ZipFile(path) as deck:
                presentation = ET.fromstring(deck.read('ppt/presentation.xml'))
                rels = ET.fromstring(deck.read('ppt/_rels/presentation.xml.rels'))
                targets = {r.attrib['Id']: r.attrib['Target'] for r in rels}
                pages = []
                for slide in presentation.findall('.//{http://schemas.openxmlformats.org/presentationml/2006/main}sldId'):
                    target = targets[slide.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
                    member = target.lstrip('/') if target.startswith('/') else 'ppt/' + target
                    tree = ET.fromstring(deck.read(member))
                    pages.append('\n'.join(''.join(p.itertext()) for p in tree.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}p')))
        else:
            pages = [p.extract_text() or '' for p in PdfReader(path).pages]
            if not any(text.strip() for text in pages):
                import pymupdf
                with pymupdf.open(path) as document:
                    for i, page in enumerate(document, 1):
                        page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(str(output / f'formula-{i:02}.png'))
        record = {'file': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                  'image_only': not any(text.strip() for text in pages),
                  'pages': [{'number': i, 'text': text} for i, text in enumerate(pages, 1)]}
        documents.append(record)
        (output / (path.stem + '.txt')).write_text('\n\n'.join(f'--- {name} {"slide" if path.suffix == ".pptx" else "page"} {i} ---\n{text}' for i, text in enumerate(pages, 1)), encoding='utf-8')
    (output / 'sources.json').write_text(json.dumps(documents, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({d['file']: len(d['pages']) for d in documents}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=Path.home() / 'Downloads')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/da/extracted')
    args = parser.parse_args()
    extract(args.source_dir, args.output_dir)
