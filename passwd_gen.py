import secrets
import string
import hashlib
import time

def generate_strong_password(length=16):
    """
    Generates a strong password with a mix of uppercase letters,
    lowercase letters, digits, and the '$' special character,
    incorporating SHA1 into the generation process.
    """
    if length < 8:
        raise ValueError("Password length should be at least 8 characters for strength.")

    # Define character sets
    lowercase_chars = string.ascii_lowercase
    uppercase_chars = string.ascii_uppercase
    digit_chars = string.digits
    special_chars = '$' # Only '$' allowed as special character

    all_allowed_chars = lowercase_chars + uppercase_chars + digit_chars + special_chars

    password_chars = []

    # Ensure at least one character from each required set
    password_chars.append(secrets.choice(lowercase_chars))
    password_chars.append(secrets.choice(uppercase_chars))
    password_chars.append(secrets.choice(digit_chars))
    password_chars.append(secrets.choice(special_chars)) # Ensure at least one '$'

    # Use SHA1 as a source of "randomness" for the remaining characters
    # Generate a seed using current time and a cryptographically secure random number
    seed_data = str(time.time()).encode('utf-8') + secrets.token_bytes(32)
    sha1_hash = hashlib.sha1(seed_data).hexdigest()

    # Extend the SHA1 hash if needed to provide enough characters
    while len(sha1_hash) < length:
        seed_data = sha1_hash.encode('utf-8') + secrets.token_bytes(16)
        sha1_hash += hashlib.sha1(seed_data).hexdigest()

    # Fill the remaining length with characters derived from SHA1 hash and general random choices
    for i in range(length - len(password_chars)):
        # Use SHA1 hex characters, but map them to the allowed set
        # This is a simplified mapping; a more robust one would be complex
        char_index = int(sha1_hash[i % len(sha1_hash)], 16) % len(all_allowed_chars)
        password_chars.append(all_allowed_chars[char_index])

    # Shuffle the password list to ensure randomness and mix the guaranteed characters
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)

if __name__ == "__main__":
    try:
        password = generate_strong_password()
        print(f"Generated strong password: {password}")
    except ValueError as e:
        print(f"Error: {e}")
