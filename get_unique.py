import json
import re

DATA_PATH = "/home/fatih/Masaüstü/Yıllık Planlar/data/index.json"

def get_unique_names():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return sorted(list(set(item["ders"] for item in data["dosyalar"])))

if __name__ == "__main__":
    names = get_unique_names()
    with open("unique_names.txt", "w", encoding="utf-8") as f:
        for n in names:
            f.write(n + "\n")
