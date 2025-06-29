import boto3
import json
from datetime import datetime
from typing import List, Dict, Optional
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

class DynamoDBService:
    """Service layer for DynamoDB operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'events')
        self.table = self.dynamodb.Table(self.table_name)
        
    def create_table_if_not_exists(self):
        """Create the events table if it doesn't exist"""
        try:
            # Check if table exists
            self.dynamodb.meta.client.describe_table(TableName=self.table_name)
            print(f"✅ Table {self.table_name} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create table
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'id',
                            'KeyType': 'HASH'  # Partition key
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                
                # Wait for table to be created
                table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
                print(f"✅ Created table {self.table_name}")
            else:
                raise e
    
    def get_all_events(self) -> List[Dict]:
        """Get all events from DynamoDB"""
        try:
            response = self.table.scan()
            events = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                events.extend(response.get('Items', []))
            
            # Sort by start_time
            events.sort(key=lambda x: x.get('start_time', ''))
            return events
            
        except ClientError as e:
            print(f"❌ Error getting events: {e}")
            return []
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
        """Get a specific event by ID"""
        try:
            response = self.table.get_item(Key={'id': event_id})
            return response.get('Item')
        except ClientError as e:
            print(f"❌ Error getting event {event_id}: {e}")
            return None
    
    def create_event(self, event_data: Dict) -> Dict:
        """Create a new event"""
        try:
            # Add timestamps
            now = datetime.now().isoformat()
            event_data['created_at'] = now
            event_data['updated_at'] = now
            
            # Insert into DynamoDB
            self.table.put_item(Item=event_data)
            print(f"✅ Created event: {event_data['title']}")
            return event_data
            
        except ClientError as e:
            print(f"❌ Error creating event: {e}")
            raise Exception(f"Failed to create event: {str(e)}")
    
    def update_event(self, event_id: str, event_data: Dict) -> Dict:
        """Update an existing event"""
        try:
            # Get existing event
            existing_event = self.get_event_by_id(event_id)
            if not existing_event:
                raise ValueError("Event not found")
            
            # Update fields
            existing_event.update(event_data)
            existing_event['updated_at'] = datetime.now().isoformat()
            
            # Save to DynamoDB
            self.table.put_item(Item=existing_event)
            print(f"✅ Updated event: {existing_event['title']}")
            return existing_event
            
        except ClientError as e:
            print(f"❌ Error updating event: {e}")
            raise Exception(f"Failed to update event: {str(e)}")
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            # Check if event exists
            existing_event = self.get_event_by_id(event_id)
            if not existing_event:
                raise ValueError("Event not found")
            
            # Delete from DynamoDB
            self.table.delete_item(Key={'id': event_id})
            print(f"✅ Deleted event: {existing_event['title']}")
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting event: {e}")
            raise Exception(f"Failed to delete event: {str(e)}")
    
    def search_events(self, query: str) -> List[Dict]:
        """Search events by title or description"""
        try:
            # Get all events and filter locally
            # For production, consider using DynamoDB Global Secondary Index
            all_events = self.get_all_events()
            query_lower = query.lower()
            
            matching_events = []
            for event in all_events:
                title = event.get('title', '').lower()
                description = event.get('description', '').lower()
                
                if query_lower in title or query_lower in description:
                    matching_events.append(event)
            
            return matching_events
            
        except Exception as e:
            print(f"❌ Error searching events: {e}")
            return []
    
    def get_events_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get events within a date range"""
        try:
            all_events = self.get_all_events()
            matching_events = []
            
            for event in all_events:
                event_start = event.get('start_time', '')
                if start_date <= event_start <= end_date:
                    matching_events.append(event)
            
            return matching_events
            
        except Exception as e:
            print(f"❌ Error getting events by date range: {e}")
            return []
    
    def get_events_with_email(self) -> List[Dict]:
        """Get all events that have email reminders"""
        try:
            all_events = self.get_all_events()
            return [event for event in all_events if event.get('email')]
            
        except Exception as e:
            print(f"❌ Error getting events with email: {e}")
            return []
    
    def migrate_from_json(self, json_file_path: str):
        """Migrate events from JSON file to DynamoDB"""
        try:
            if not os.path.exists(json_file_path):
                print(f"❌ JSON file not found: {json_file_path}")
                return
            
            with open(json_file_path, 'r') as f:
                events = json.load(f)
            
            print(f"🔄 Migrating {len(events)} events to DynamoDB...")
            
            for event in events:
                try:
                    self.create_event(event)
                except Exception as e:
                    print(f"❌ Failed to migrate event {event.get('title', 'Unknown')}: {e}")
            
            print(f"✅ Migration completed! {len(events)} events migrated.")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
    
    def export_to_json(self, json_file_path: str):
        """Export all events from DynamoDB to JSON file"""
        try:
            events = self.get_all_events()
            
            with open(json_file_path, 'w') as f:
                json.dump(events, f, indent=4, default=str)
            
            print(f"✅ Exported {len(events)} events to {json_file_path}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}") 