import pandas as pd
from pathlib import Path

INPUT_PATH = Path("./input_data")

VALIDATION_RULES = {
                    "parametres": {
                        "names": ["Debiteurnaam", "Factuurnummer", "Datum", "Bedrag_EUR"],
                        "pandas_formatting": ["SAP"],
                        "formatting-SAP": "Cust. Name",
                        "to_discard": [
                            "Belegart",
                            "Sonderhauptb.Kennz.",
                            "Symbol Nettofälligkeit",
                            "Text",
                            "Hauswährung",
                            "Ausgleichsbeleg",
                            "Zuordnung"
                            ],
                    }
                }

def file_ingestion(path_dir: Path) -> pd.DataFrame:
    assert INPUT_PATH.exists()
    df = pd.read_excel(path_dir)
    return df



