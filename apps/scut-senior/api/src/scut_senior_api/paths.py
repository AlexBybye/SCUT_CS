import os
from pathlib import Path


APP_ROOT = Path(
    os.getenv("SCUT_SENIOR_APP_ROOT", str(Path(__file__).resolve().parents[3]))
).resolve()
CONTRACT_ROOT = APP_ROOT / "packages" / "contracts" / "v1"
FIXTURE_ROOT = APP_ROOT / "tests" / "fixtures"
MIGRATION_ROOT = APP_ROOT / "api" / "migrations"
