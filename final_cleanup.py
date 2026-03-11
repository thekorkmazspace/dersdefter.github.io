import os
import json

JSON_DIR = 'json_planlar'
INDEX_FILE = os.path.join(JSON_DIR, 'index.json')

if not os.path.exists(INDEX_FILE):
    print("index.json not found.")
    exit(1)

with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    index_data = json.load(f)

indexed_files = {entry['dosya'] for entry in index_data['dosyalar']}
indexed_files.add('index.json')

actual_files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json')]

removed_count = 0
for file in actual_files:
    if file not in indexed_files:
        os.remove(os.path.join(JSON_DIR, file))
        removed_count += 1

print(f'Removed {removed_count} orphaned files.')
