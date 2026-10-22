"""One-command pipeline: train models, save predictions, run fairness audit."""

import subprocess
import sys
from pathlib import Path

from train import train_and_save


if __name__ == "__main__":
    output_dir = Path.home() / "clinical-readmission-risk" / "data" / "processed"

    print("=" * 60)
    print("STEP 1: Training models")
    print("=" * 60)
    train_and_save(output_dir)

    print()
    print("=" * 60)
    print("STEP 2: Fairness audit")
    print("=" * 60)
    fairness_script = Path(__file__).parent / "fairness_audit.py"
    subprocess.run([sys.executable, str(fairness_script)], check=True)

    print()
    print("Pipeline complete.")