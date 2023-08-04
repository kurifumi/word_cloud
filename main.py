import csv

def read_csv(file_name: str, target_column: str = 'name'):
    base_path = 'data/'
    with open(f'{base_path}{file_name}', 'r') as f: #comma-separated
        reader = csv.DictReader(f)
        data = []
        for row in reader: data.append(row[target_column])
    return data

