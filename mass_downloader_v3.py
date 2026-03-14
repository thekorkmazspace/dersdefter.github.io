import requests
import os
import json
import concurrent.futures
import time

def download_id(plan_id):
    url = f"https://defterdoldur.com/planword/{plan_id}"
    filename = f"word_planlar/downloaded_{plan_id}.docx"
    
    if os.path.exists(filename):
        return plan_id, "exists"
        
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            with open(filename, "wb") as f:
                f.write(r.content)
            return plan_id, "saved"
        else:
            return plan_id, f"error_{r.status_code}"
    except Exception as e:
        return plan_id, f"exception_{str(e)}"

def start_mass_download():
    with open("all_possible_ids.json", "r") as f:
        all_ids = json.load(f)
    
    os.makedirs("word_planlar", exist_ok=True)
    
    print(f"Starting mass download of {len(all_ids)} plans using 10 threads...")
    
    results = {"saved": 0, "exists": 0, "error": 0}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_id = {executor.submit(download_id, pid): pid for pid in all_ids}
        
        count = 0
        for future in concurrent.futures.as_completed(future_to_id):
            pid, status = future.result()
            count += 1
            
            if status == "saved":
                results["saved"] += 1
            elif status == "exists":
                results["exists"] += 1
            else:
                results["error"] += 1
                print(f"[{pid}] Failed: {status}")
            
            if count % 50 == 0:
                print(f"Progress: {count}/{len(all_ids)} (New: {results['saved']}, Skipped: {results['exists']}, Errors: {results['error']})")

    print(f"\nFinal Results:")
    print(f"Total processed: {count}")
    print(f"Successfully downloaded: {results['saved']}")
    print(f"Already existed: {results['exists']}")
    print(f"Errors: {results['error']}")

if __name__ == "__main__":
    start_mass_download()
