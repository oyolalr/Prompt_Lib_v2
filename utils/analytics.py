from typing import Dict, List, Any
from collections import Counter
from utils.data_handler import load_data

def get_library_stats() -> Dict[str, Any]:
    """Calculates statistics for the library."""
    data_types = ["roles", "goals", "context", "output", "saved_prompts"]
    stats = {
        "counts": {},
        "top_tags": {},
        "total_items": 0,
        "favorites": 0
    }
    
    all_tags = []
    
    for dtype in data_types:
        items = load_data(dtype)
        count = len(items)
        stats["counts"][dtype] = count
        stats["total_items"] += count
        
        # Count favorites
        stats["favorites"] += sum(1 for i in items if i.get('is_favorite'))
        
        # Collect tags
        for item in items:
            if item.get('tags'):
                all_tags.extend(item['tags'])
                
    # Top 10 tags
    stats["top_tags"] = dict(Counter(all_tags).most_common(10))
    
    return stats
