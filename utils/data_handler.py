import json
import os
import uuid
from typing import List, Dict, Optional
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def _get_file_path(data_type: str) -> str:
    """Returns the absolute path for the given data type's JSON file."""
    return os.path.join(DATA_DIR, f"{data_type}.json")

def load_data(data_type: str) -> List[Dict]:
    """Loads data from the specified JSON file."""
    file_path = _get_file_path(data_type)
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_data(data_type: str, data: List[Dict]) -> None:
    """Saves data to the specified JSON file."""
    file_path = _get_file_path(data_type)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def add_item(data_type: str, title: str, content: str, tags: list = None, is_favorite: bool = False) -> Dict:
    """Adds a new item to the storage."""
    data = load_data(data_type)
    new_item = {
        "id": str(uuid.uuid4()),
        "title": title,
        "content": content,
        "tags": tags or [],
        "is_favorite": is_favorite
    }
    data.append(new_item)
    save_data(data_type, data)
    return new_item

def update_item(data_type: str, item_id: str, title: str, content: str, tags: list = None, create_version: bool = False) -> bool:
    """Updates an existing item, optionally creating a version history entry."""
    data = load_data(data_type)
    for item in data:
        if item['id'] == item_id:
            # Handle versioning for saved prompts
            if create_version and data_type == "saved_prompts":
                if 'versions' not in item:
                    item['versions'] = []
                
                # archive current state
                item['versions'].append({
                    "timestamp": datetime.now().isoformat(),
                    "content": item['content']
                })

            item['title'] = title
            item['content'] = content
            if tags is not None:
                item['tags'] = tags
            save_data(data_type, data)
            return True
    return False

def duplicate_item(data_type: str, item_id: str, new_title_suffix: str = " (Copy)") -> bool:
    """Duplicates an existing item with a new ID."""
    data = load_data(data_type)
    original = next((i for i in data if i['id'] == item_id), None)
    
    if original:
        new_item = original.copy()
        new_item['id'] = str(uuid.uuid4())
        new_item['title'] = original['title'] + new_title_suffix
        new_item['is_favorite'] = False # Reset favorite status
        
        # Insert after original for better UX? Or append? Append is simpler.
        data.append(new_item)
        save_data(data_type, data)
        return True
    return False

def delete_item(data_type: str, item_id: str) -> bool:
    """Deletes an item by ID."""
    data = load_data(data_type)
    original_len = len(data)
    data = [item for item in data if item['id'] != item_id]
    
    if len(data) < original_len:
        save_data(data_type, data)
        return True
    return False

def toggle_favorite(data_type: str, item_id: str) -> bool:
    """Toggles the favorite status of an item."""
    data = load_data(data_type)
    for item in data:
        if item['id'] == item_id:
            item['is_favorite'] = not item.get('is_favorite', False)
            save_data(data_type, data)
            return True
    return False

# --- Blueprints ---
def save_blueprint(title: str, role_id: str, goal_id: str, context_ids: List[str], output_id: str) -> None:
    """Saves a prompt configuration (blueprint)."""
    blueprints = load_data("blueprints")
    new_bp = {
        "id": str(uuid.uuid4()),
        "title": title,
        "role_id": role_id,
        "goal_id": goal_id,
        "context_ids": context_ids,
        "output_id": output_id
    }
    blueprints.append(new_bp)
    save_data("blueprints", blueprints)

def get_blueprint(bp_id: str) -> Optional[Dict]:
    """Retrieves a specific blueprint."""
    blueprints = load_data("blueprints")
    for bp in blueprints:
        if bp['id'] == bp_id:
            return bp
    return None

# --- History ---
def add_to_history(prompt_text: str) -> None:
    """Adds a generated prompt to history, keeping only the last 20."""
    history = load_data("history")
    
    # Create history item with timestamp (optional, but good practice)
    # For now, just simple text + id
    new_entry = {
        "id": str(uuid.uuid4()),
        "content": prompt_text,
        "timestamp": None # Could add datetime if needed
    }
    
    # Prepend to list (newest first)
    history.insert(0, new_entry)
    
    # Truncate
    if len(history) > 20:
        history = history[:20]
        
    save_data("history", history)

def clear_history():
    save_data("history", [])

def export_library() -> str:
    """Exports all data to a single JSON string."""
    library = {}
    for dtype in ["roles", "goals", "context", "output", "saved_prompts"]:
        library[dtype] = load_data(dtype)
    return json.dumps(library, indent=2)

def import_library(json_data: str, merge: bool = True) -> bool:
    """Imports data from a JSON string."""
    try:
        library = json.loads(json_data)
        for dtype, items in library.items():
            current_data = load_data(dtype) if merge else []
            
            # Simple merge: append if ID not present, or just append all new?
            # Better: append distinct IDs.
            existing_ids = {item['id'] for item in current_data}
            
            for item in items:
                if item['id'] not in existing_ids:
                    current_data.append(item)
                elif not merge:
                     # If not merging and we want to overwrite, we should have cleared current_data
                     # But current_data is empty if merge is False, so just append.
                     current_data.append(item)
            
            save_data(dtype, current_data)
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False
