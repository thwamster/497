import os

import requests

base_dir = r"./data"
os.makedirs(base_dir, exist_ok=True)

endpoints = {
    "OMT-MDCR-GEO.2013-2023.csv": "https://data.cms.gov/data-api/v1/dataset/94d00f36-73ce-4520-9b3f-83cd3cded25c/data.csv"
}

print("Started.")

for filename, url in endpoints.items():
    output_path = os.path.join(base_dir, filename)

    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()

            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

print("Ended.")
