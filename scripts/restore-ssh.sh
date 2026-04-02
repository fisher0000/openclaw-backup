#!/bin/bash
# SSH Key Restore Script
# 当 ~/.ssh/ 目录丢失时，从备份恢复

BACKUP_DIR="/home/node/.openclaw/workspace/.ssh-backup"
SSH_DIR="$HOME/.ssh"

if [ ! -d "$SSH_DIR" ]; then
    echo "SSH directory missing. Restoring from backup..."
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"
    
    if [ -f "$BACKUP_DIR/id_ed25519" ]; then
        cp "$BACKUP_DIR/id_ed25519" "$SSH_DIR/"
        cp "$BACKUP_DIR/id_ed25519.pub" "$SSH_DIR/"
        chmod 600 "$SSH_DIR/id_ed25519"
        chmod 644 "$SSH_DIR/id_ed25519.pub"
        echo "✓ SSH keys restored successfully"
    else
        echo "✗ Backup keys not found"
        exit 1
    fi
else
    echo "SSH directory already exists"
fi
