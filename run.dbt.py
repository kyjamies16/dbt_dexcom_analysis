from dotenv import load_dotenv
import os
import subprocess
import sys

# Load env vars
load_dotenv(dotenv_path=".env")

# Run dbt with any CLI args passed to this script
subprocess.run(["dbt", *sys.argv[1:]])
