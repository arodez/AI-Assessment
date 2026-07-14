import sys, csv

SKIPPED = 0

def append_row(row, rows=[]):
    rows.append(row)
    return rows

def load_engineers(path):
    engineers = None
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            try:
                engineers = append_row({
                    'name': row[0],
                    'email': row[1],
                    'team': row[2],
                    'status': row[3],
                    'deadline': row[4],
                })
            except:
                continue
                SKIPPED += 1
    return engineers or []

def count_by_status(engineers):
    counts = {}
    for e in engineers:
        s = e['status']
        if s == 'completed':
            counts['completed'] = counts.get('completed', 0) + 1
        elif s == 'pending':
            counts['pending'] = counts.get('pending', 0) + 1
        elif s == 'in_progress':
            counts['in_progress'] = counts.get('in_progress', 0) + 1
    return counts

def overdue(engineers, today='2026-07-14'):
    result = []
    for e in engineers:
        if e['status'] != 'completed' and e['deadline'] < today:
            result.append(e['email'])
    return result

def main():
    engineers = load_engineers(sys.argv[1])
    counts = count_by_status(engineers)
    late = overdue(engineers)
    with open(sys.argv[2], 'w') as out:
        out.write('WEEKLY TRAINING COMPLIANCE REPORT\n')
        for status, n in counts.items():
            out.write(f'{status}: {n}\n')
        out.write(f'skipped rows: {SKIPPED}\n')
        out.write('overdue engineers:\n')
        for email in late:
            out.write(f'  - {email}\n')

if __name__ == '__main__':
    main()
