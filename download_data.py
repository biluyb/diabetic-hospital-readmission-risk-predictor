import os
import requests
import zipfile
import io

data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)

csv_path = os.path.join(data_dir, 'diabetic_data.csv')

if not os.path.exists(csv_path):
    print("Downloading dataset from UCI repository...")
    url = "https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip"
    resp = requests.get(url, timeout=60)
    print(f"Status code: {resp.status_code}, content length: {len(resp.content)}")
    if resp.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        z.extractall(data_dir)
        print("Extracted archive successfully!")
        print("Extracted files:", os.listdir(data_dir))
    else:
        print("Failed to download zip directly. Trying ucimlrepo fallback...")
        from ucimlrepo import fetch_ucirepo
        diabetes_130_us_hospitals_for_years_1999_2008 = fetch_ucirepo(id=296)
        X = diabetes_130_us_hospitals_for_years_1999_2008.data.features
        y = diabetes_130_us_hospitals_for_years_1999_2008.data.targets
        import pandas as pd
        df = pd.concat([X, y], axis=1)
        df.to_csv(csv_path, index=False)
        print("Saved via ucimlrepo!")
else:
    print(f"Dataset already exists at {csv_path}")
