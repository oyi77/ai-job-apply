#!/bin/bash

# Generate self-signed SSL certificates for development/testing
# Usage: ./generate-ssl.sh [domain]

DOMAIN=${1:-localhost}
SSL_DIR="./nginx/ssl"

mkdir -p "$SSL_DIR"

if [ -f "$SSL_DIR/cert.pem" ]; then
    echo "Certificate already exists at $SSL_DIR/cert.pem"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo "Generating self-signed certificate for $DOMAIN..."

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/key.pem" \
    -out "$SSL_DIR/cert.pem" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"

echo "Certificate generated successfully."
echo "Key: $SSL_DIR/key.pem"
echo "Cert: $SSL_DIR/cert.pem"
