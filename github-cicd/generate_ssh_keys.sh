#!/bin/bash

# Ensure the .ssh directory exists and has correct permissions
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Generate ed25519 SSH key pair without a passphrase
KEY_NAME="github_CICD_keys"
ssh-keygen -t ed25519 -f ~/.ssh/$KEY_NAME -N ""

# Set correct permissions for the private key
chmod 600 ~/.ssh/$KEY_NAME

# Append the public key to authorized_keys
cat ~/.ssh/$KEY_NAME.pub >> ~/.ssh/authorized_keys

# Set correct permissions for authorized_keys
chmod 600 ~/.ssh/authorized_keys

echo "SSH key pair generated successfully:"
echo "Private key: ~/.ssh/$KEY_NAME"
echo "Public key: ~/.ssh/$KEY_NAME.pub"
echo "Public key added to ~/.ssh/authorized_keys"
