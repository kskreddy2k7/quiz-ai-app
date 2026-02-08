"""
Database Migration Script v2
Adds current_class and preferred_language fields to User table
"""
from sqlalchemy import create_engine, text
from sqlalchemy import inspect
import os
from dotenv import load_dotenv

def migrate_database():
    load_dotenv()
    
    # Get database URL
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./sql_app.db')
    
    # Create engine
    engine = create_engine(
        DATABASE_URL, 
        connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
    )
    
    # Check existing columns
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('users')]
    
    # Define new columns to add
    new_columns = {
        'current_class': 'VARCHAR',
        'preferred_language': 'VARCHAR'
    }
    
    print("🔄 Starting database migration v2...")
    
    # Add missing columns
    with engine.connect() as conn:
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    conn.execute(text(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}'))
                    conn.commit()
                    print(f'✅ Added {column_name} column')
                except Exception as e:
                    print(f'❌ Error adding {column_name}: {e}')
            else:
                print(f'⏭️  {column_name} already exists, skipping')
    
    # Verify migration
    inspector = inspect(engine)
    updated_columns = [col['name'] for col in inspector.get_columns('users')]
    
    if all(col in updated_columns for col in new_columns.keys()):
        print('\n✅ Migration completed successfully!')
        return True
    else:
        missing = [col for col in new_columns.keys() if col not in updated_columns]
        print(f'\n⚠️  Migration incomplete. Missing columns: {missing}')
        return False

if __name__ == '__main__':
    success = migrate_database()
    exit(0 if success else 1)
