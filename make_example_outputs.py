import os
import subprocess
import sys

def main():
    cmd = [sys.executable, os.path.join("src", "digital_twin_pipeline_ekf.py"),
           "--save-plots", "--no-show", "--outdir", "outputs", "--seed", "2"]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    main()
