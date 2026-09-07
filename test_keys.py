import base64

priv = "aBpLtuZ17xfQ+WSOufVQjs7fbVVzFWs6OM6Kir1VLFI="
pub = "k1q3s2th3eF0PabTO012TBWAacgydpNkYZ2I2tqYZwc="
psk = "0A6zqhEb/3Blp5bTHYGeomFa7kXhbW+M3B+p6h3XBlo="

for name, k in [("priv", priv), ("pub", pub), ("psk", psk)]:
    b = base64.b64decode(k)
    print(f"{name}: len={len(b)} bytes (valid={len(b)==32})")
