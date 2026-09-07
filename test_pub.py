import base64
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

priv_b64 = "aBpLtuZ17xfQ+WSOufVQjs7fbVVzFWs6OM6Kir1VLFI="
priv_bytes = base64.b64decode(priv_b64)
priv_key = x25519.X25519PrivateKey.from_private_bytes(priv_bytes)
pub_key = priv_key.public_key()
pub_b64 = base64.b64encode(pub_key.public_bytes(Encoding.Raw, PublicFormat.Raw)).decode("ascii")
print(f"Derived Public Key: {pub_b64}")
