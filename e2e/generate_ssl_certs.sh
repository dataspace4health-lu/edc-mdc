#!/bin/bash

# SSL Certificate Generation Script for PostgreSQL
# This script generates self-signed certificates for development/testing

set -e

CERTS_DIR="./e2e/certs"
COUNTRY="LU"
STATE="LU"
CITY="Esch-sur-Alzette"
ORG="Luxembourg National Data Service"
OU="IT Department"
CN="localhost"

# Create certificates directory
mkdir -p "$CERTS_DIR"
cd "$CERTS_DIR"

echo "Generating SSL certificates for PostgreSQL..."

# 1. Generate CA private key
echo "1. Generating CA private key..."
openssl genrsa -out ca-key.pem 4096

# 2. Generate CA certificate
echo "2. Generating CA certificate..."
openssl req -new -x509 -key ca-key.pem -days 365 -out ca-cert.pem -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=$OU/CN=CA"

# 3. Generate server private key
echo "3. Generating server private key..."
openssl genrsa -out server-key.pem 4096

# 4. Generate server certificate signing request
echo "4. Generating server certificate signing request..."
openssl req -new -key server-key.pem -out server.csr -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=$OU/CN=$CN"

# 5. Generate server certificate signed by CA
echo "5. Generating server certificate..."
openssl x509 -req -in server.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 365

# 6. Generate client private key
echo "6. Generating client private key..."
openssl genrsa -out client-key.pem 4096

# 7. Generate client certificate signing request
echo "7. Generating client certificate signing request..."
openssl req -new -key client-key.pem -out client.csr -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=$OU/CN=client"

# 8. Generate client certificate signed by CA
echo "8. Generating client certificate..."
openssl x509 -req -in client.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client-cert.pem -days 365

# 9. Set proper permissions
echo "9. Setting proper permissions..."
chmod 600 *-key.pem
chmod 644 *-cert.pem ca-cert.pem

# 10. Clean up CSR files
echo "10. Cleaning up temporary files..."
rm -f server.csr client.csr

echo "SSL certificates generated successfully in $CERTS_DIR/"
echo ""
echo "Files created:"
echo "  ca-cert.pem     - Certificate Authority certificate"
echo "  ca-key.pem      - Certificate Authority private key"
echo "  server-cert.pem - PostgreSQL server certificate"
echo "  server-key.pem  - PostgreSQL server private key"
echo "  client-cert.pem - Client certificate"
echo "  client-key.pem  - Client private key"
echo ""
echo "You can now use these certificates with your PostgreSQL setup."
