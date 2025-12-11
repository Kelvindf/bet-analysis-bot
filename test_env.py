from dotenv import load_dotenv
import os

load_dotenv()
print(f"ANALYSIS_INTERVAL_MINUTES = {os.getenv('ANALYSIS_INTERVAL_MINUTES')}")
print(f"SCHEDULE_INTERVAL_MINUTES = {os.getenv('SCHEDULE_INTERVAL_MINUTES')}")
