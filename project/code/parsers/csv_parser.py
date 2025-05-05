import pandas as pd

def parse_csv(file_path):
    df = pd.read_csv(file_path)
    text = df.to_string(index=False)
    metadata = {
        "source_filename": file_path.name,
        "columns": list(df.columns),
        "rows": len(df)
    }
    return text.strip(), metadata
