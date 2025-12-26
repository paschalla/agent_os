import sqlite3
import os
import json
from datetime import datetime

def export_chats():
    # Database path
    home = os.path.expanduser("~")
    db_path = os.path.join(home, ".andy-os", "memory.db")
    
    if not os.path.exists(db_path):
        print(f"No database found at {db_path}")
        return

    # Output directory
    export_dir = os.path.join(os.getcwd(), "exports")
    os.makedirs(export_dir, exist_ok=True)
    print(f"Exporting chats to: {export_dir}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all conversations
    cursor.execute("SELECT id, created_at, summary FROM conversations ORDER BY created_at DESC")
    conversations = cursor.fetchall()

    count = 0
    for conv in conversations:
        conv_id = conv['id']
        date_str = conv['created_at'].split()[0] # YYYY-MM-DD
        filename = f"chat_{conv_id}_{date_str}.md"
        filepath = os.path.join(export_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Conversation {conv_id}\n")
            f.write(f"**Date**: {conv['created_at']}\n")
            if conv['summary']:
                f.write(f"**Summary**: {conv['summary']}\n")
            f.write("\n---\n\n")

            # Messages
            cursor.execute(
                "SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", 
                (conv_id,)
            )
            messages = cursor.fetchall()
            
            for msg in messages:
                role = msg['role'].capitalize()
                content = msg['content']
                timestamp = msg['created_at']
                
                f.write(f"### {role} ({timestamp})\n")
                f.write(f"{content}\n\n")
        
        count += 1
        print(f"Exported: {filename}")

    print(f"\nSuccessfully exported {count} conversations.")
    conn.close()

if __name__ == "__main__":
    export_chats()
