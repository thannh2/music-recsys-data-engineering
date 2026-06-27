import time

def parse_interaction(parts):
    if len(parts) < 3: return None
    try:
        return {
            "user_id": parts[0].strip(),
            "album_id": parts[1].strip(),
            "timestamp": time.time(), 
            "num_repeat": float(parts[3]) if len(parts) > 3 else 1.0
        }
    except ValueError: return None

def parse_user(parts):
    if len(parts) < 6: return None
    try:
        return {
            "user_id": parts[0].strip(),
            "country": parts[1].strip(),
            "age": int(parts[2]) if parts[2].strip().isdigit() else -1,
            "gender": parts[3].strip(),
            "playcount": int(parts[4]) if parts[4].strip().isdigit() else 0,
            "registered_timestamp": int(parts[5]) if parts[5].strip().isdigit() else 0
        }
    except ValueError: return None

def parse_album(parts):
    if len(parts) < 3: return None
    return {
        "album_id": parts[0].strip(),
        "album_name": parts[1].strip(),
        "artist_id": parts[2].strip()
    }