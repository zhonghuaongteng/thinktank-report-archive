"""Check the user's separate weekly minimums against selected items and decisions."""
from pathlib import Path
from collections import Counter
import argparse, csv, json

def validate(items, rows):
    errors = []
    urls = [x.get('url', '').strip().rstrip('/') for x in items]
    if not all(urls) or len(set(urls)) != len(urls):
        errors.append('入选材料存在空URL或重复URL')
    decisions = {r['URL'].strip().rstrip('/'): r['最终处置'] for r in rows}
    counts = Counter()
    for item, url in zip(items, urls):
        kind = '重点' if item.get('priority') in ('P0', 'P1') else '简讯'
        counts[kind] += 1
        body = item.get('highlights_markdown') if kind == '重点' else item.get('chinese_summary')
        if not (body or '').strip(): errors.append(f'{url}: 缺少正文')
        if decisions.get(url) != kind: errors.append(f'{url}: 与复核表处置不一致')
    if set(urls) != {u for u, d in decisions.items() if d in ('重点', '简讯')}:
        errors.append('入选文件与复核表的收录集合不一致')
    for kind, minimum in [('重点', 6), ('简讯', 10)]:
        if counts[kind] < minimum: errors.append(f'{kind}只有{counts[kind]}篇，低于{minimum}篇')
    return {'passed': not errors, 'minimum_features': 6, 'minimum_briefs': 10,
            'features': counts['重点'], 'briefs': counts['简讯'], 'errors': errors}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ('items', 'review', 'output'): p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    data = json.loads(a.items.read_text(encoding='utf-8'))
    with a.review.open(encoding='utf-8-sig', newline='') as f: rows = list(csv.DictReader(f))
    result = validate(data['items'] if isinstance(data, dict) else data, rows)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=True))
    raise SystemExit(0 if result['passed'] else 1)
