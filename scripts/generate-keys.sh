#!/bin/bash
# Generate JWT RSA keys for authentication

set -e

KEYS_DIR="./keys"
PRIVATE_KEY="$KEYS_DIR/private_key.pem"
PUBLIC_KEY="$KEYS_DIR/public_key.pem"

mkdir -p "$KEYS_DIR"

if [ -f "$PRIVATE_KEY" ] && [ -f "$PUBLIC_KEY" ]; then
    echo "Keys already exist. Skipping generation."
    echo "To regenerate, delete the keys directory first."
    exit 0
fi

echo "Generating RSA key pair..."
openssl genrsa -out "$PRIVATE_KEY" 2048
openssl rsa -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY"

echo "Keys generated:"
echo "  Private: $PRIVATE_KEY"
echo "  Public:  $PUBLIC_KEY"

# Set permissions
chmod 600 "$PRIVATE_KEY"
chmod 644 "$PUBLIC_KEY"

echo "Done!"