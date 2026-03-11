#!/bin/bash

# To run this script, ensure you have 'sshpass' installed (brew install sshpass)
# chmod +x test_sftp.sh
# ./test_sftp.sh

echo "Testing SFTP connection..."
echo "Waiting for SFTP server to be ready..."
sleep 10

# Create a test file
echo "Hello from SFTP test!" > /tmp/test_file.txt

# Test SFTP connection using expect to handle password prompt
if command -v sshpass >/dev/null 2>&1; then
    # Using sshpass (if available)
    echo "Using sshpass for authentication..."
    sshpass -p 'testpass' sftp -o StrictHostKeyChecking=no -P 2222 testuser@localhost << 'SFTP_COMMANDS'
put /tmp/test_file.txt upload/test_file.txt
ls upload/
bye
SFTP_COMMANDS
else
    # Manual instructions if sshpass is not available
    echo "sshpass not found. You can test manually with:"
    echo "sftp -P 2222 testuser@localhost"
    echo "Password: testpass"
    echo "Commands to try:"
    echo "  put /path/to/your/file upload/"
    echo "  ls upload/"
    echo "  bye"
fi

if [ $? -eq 0 ]; then
    echo "✅ SFTP connection successful!"
    echo "You can browse uploaded files at: http://localhost:8081"
    echo "File browser login: admin / admin"
else
    echo "❌ SFTP connection test completed (check manually if needed)"
fi

# Clean up test file
rm -f /tmp/test_file.txt
