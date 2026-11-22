"""Archive public transit evidence; preserve acquisition times and source bytes.

Existing successful archives are verified, not silently refreshed. A cached HTML
page may be only a dynamic shell; successful HTTP acquisition is not fact admission.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'evidence/tech_support_v0.1'


def acquire(extract_text=False):
    E.mkdir(parents=True, exist_ok=True)
    requests = json.loads((ROOT / 'evidence/tech_source_requests_v0.1.json').read_text())
    previous = {}
    for manifest in E.glob('*acquisition_manifest.json'):
        for row in json.loads(manifest.read_text()):
            if row.get('status') == 'acquired':
                previous[row['source_id']] = row

    def fetch(item):
        sid, name, url = item['source_id'], item['file'], item['url']
        path = E / name
        row = dict(source_id=sid, file=str(path.relative_to(ROOT)), url=url,
                   retrieved_utc=datetime.now(timezone.utc).isoformat())
        try:
            cached = path.exists()
            if not cached:
                with urllib.request.urlopen(url, timeout=45) as response:
                    data = response.read()
                if name.endswith('.pdf') and not data.startswith(b'%PDF'):
                    raise ValueError('Response is not a PDF')
                path.write_bytes(data)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if cached and sid in previous:
                old = previous[sid]
                if digest != old['sha256']:
                    raise ValueError('Cached source changed; preserve the archive and investigate')
                row['retrieved_utc'] = old['retrieved_utc']
            row.update(status='acquired', bytes=path.stat().st_size, sha256=digest)
        except Exception as error:
            row.update(status='failed', error=str(error))
        print(sid, row['status'], flush=True)
        return row

    with ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(fetch, requests))
    (E / 'acquisition_manifest.json').write_text(json.dumps(rows, indent=2) + '\n')
    if extract_text:
        from pypdf import PdfReader
        for row in rows:
            path = ROOT / row['file']
            if row['status'] == 'acquired' and path.suffix == '.pdf':
                text = '\n'.join(f'\n--- PHYSICAL PAGE {i} ---\n' + page.extract_text()
                                 for i, page in enumerate(PdfReader(path).pages, 1))
                path.with_suffix('.txt').write_text('\n'.join(line.rstrip() for line in text.splitlines()).strip() + '\n')
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract-text', action='store_true', help='Extract PDF text using pypdf')
    acquire(parser.parse_args().extract_text)
