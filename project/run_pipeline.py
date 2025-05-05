import argparse
import logging
import json
from pathlib import Path
from code.main import process_file
import warnings

warnings.filterwarnings("ignore", message=".*cropbox missing from /Page.*")

# Setup Logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(logs_dir / "pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline(input_file_path):
    input_path = Path(input_file_path)

    if not input_path.exists() or not input_path.is_file():
        logger.error(f"File not found: {input_file_path}")
        raise FileNotFoundError(f"File not found: {input_file_path}")

    logger.info(f"Starting semantic chunking pipeline for: {input_path.name}")
    
    try:
        result = process_file(input_path)
    except Exception as e:
        logger.exception(f"Failed during processing: {e}")
        raise

    output_folder = Path("output")
    output_folder.mkdir(exist_ok=True)
    out_path = output_folder / f"{input_path.stem}_chunks.json"

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"Output saved at: {out_path}")
    except Exception as e:
        logger.exception(f"Error saving output: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Run the semantic chunking pipeline on a file.")
    parser.add_argument("filepath", type=str, help="Path to the input file (PDF, DOCX, TXT, etc.)")
    args = parser.parse_args()

    try:
        run_pipeline(args.filepath)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")

if __name__ == "__main__":
    main()
