import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

def to_base64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

# Generate EC key pair (P-256 / prime256v1)
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Serialize Private Key (Integer)
private_value = private_key.private_numbers().private_value
private_bytes = private_value.to_bytes(32, byteorder='big')
vapid_private = to_base64url(private_bytes)

# Serialize Public Key (Uncompressed format: 0x04 + x + y)
public_numbers = public_key.public_numbers()
x = public_numbers.x.to_bytes(32, byteorder='big')
y = public_numbers.y.to_bytes(32, byteorder='big')
public_bytes = b'\x04' + x + y
vapid_public = to_base64url(public_bytes)

print(f"VAPID_PUBLIC_KEY={vapid_public}")
print(f"VAPID_PRIVATE_KEY={vapid_private}")
