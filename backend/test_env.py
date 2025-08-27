import os
from dotenv import load_dotenv

# Load .env file from parent directory
load_dotenv('../.env')

print("Environment Variables Loaded:")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"API_PORT: {os.getenv('API_PORT')}")

