import hashlib
import secrets

def generate_secret_key():
    # Generate a secure random string
    random_string = secrets.token_hex(32)  # Increase the length for SHA-512
    
    # Hash the random string using SHA-512
    hashed_key = hashlib.sha512(random_string.encode()).hexdigest()

    return hashed_key

if __name__ == '__main__':
    generate_secret_key()
