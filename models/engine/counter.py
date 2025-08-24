import os
import string

ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
BASE = len(ALPHABET)

def _encode_base62(num: int, length: int) -> str:
    """Convert integer to base62 string with fixed length."""
    chars = []
    while num > 0:
        num, rem = divmod(num, BASE)
        chars.append(ALPHABET[rem])
    while len(chars) < length:  # pad with "0"
        chars.append(ALPHABET[0])
    return ''.join(reversed(chars))[:length]

def next_id(length=6, filename="./settings/last_id.txt") -> str:
    """Generate the next unique ID of given length, persistent via file."""
    counter = -1
    
    # ✅ Load last counter safely
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                counter = int(content)

    # ✅ Increment counter
    counter += 1

    # ✅ Save new counter immediately (persists across runs)
    with open(filename, "w") as f:
        f.write(str(counter))

    # ✅ Return encoded ID
    return _encode_base62(counter, length)
