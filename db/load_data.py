import boto3
import json
from decimal import Decimal

def load_data(json_file_path, table_name, region='us-east-1'):
    """
    Loads data from a JSON file into a DynamoDB table.
    """
    
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f, parse_float=Decimal) # Parse floats as Decimal for DynamoDB
            
        print(f"Loading {len(data)} items into '{table_name}'...")
        
        # Use batch_writer for efficient bulk uploads
        with table.batch_writer() as batch:
            for item in data:
                batch.put_item(Item=item)
                
        print(f"Successfully loaded {len(data)} items.")
        
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    # Configuration
    JSON_FILE = 'seed_data.json'
    TABLE_NAME = 'ElectronicsInventory'
    REGION = 'us-east-2'  # Change if your table is in a different region
    
    load_data(JSON_FILE, TABLE_NAME, REGION)