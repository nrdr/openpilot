#!/usr/bin/env bash
#
# Fix Data Permissions - Repairs ownership and permissions for /data and /data/openpilot
#
# Usage:
#   bash scripts/fix_data_permissions.sh
#   OR via SSH:
#   ssh comma@10.0.1.125 'bash -s' < scripts/fix_data_permissions.sh
#

set -e

echo "================================================"
echo "BluePilot Data Permissions Fixer"
echo "================================================"
echo ""

# Safety check: Only run on Comma devices
if [ ! -d "/data/params" ] && [ ! -f "/COMMA" ]; then
    echo "✗ ERROR: This script can only run on a Comma device!"
    echo ""
    echo "This script modifies critical system directories and should"
    echo "only be executed on a Comma device, not on development machines."
    echo ""
    exit 1
fi

echo "✓ Comma device detected"
echo ""

# Check if running as root or comma user
CURRENT_USER=$(whoami)
echo "Running as: $CURRENT_USER"
echo ""

# Function to check current permissions
check_permissions() {
    local path=$1
    local owner=$(stat -c '%U:%G' "$path" 2>/dev/null || stat -f '%Su:%Sg' "$path" 2>/dev/null)
    local perms=$(stat -c '%a' "$path" 2>/dev/null || stat -f '%A' "$path" 2>/dev/null | cut -c4-6)
    echo "  Current: $path"
    echo "    Owner: $owner"
    echo "    Permissions: $perms"
}

# Step 1: Check current /data permissions
echo "[1/4] Checking current /data permissions..."
if [ -d "/data" ]; then
    check_permissions "/data"
else
    echo "  ✗ ERROR: /data directory does not exist!"
    exit 1
fi
echo ""

# Step 2: Check current /data/openpilot permissions
echo "[2/4] Checking current /data/openpilot permissions..."
if [ -d "/data/openpilot" ]; then
    check_permissions "/data/openpilot"
else
    echo "  ✗ ERROR: /data/openpilot directory does not exist!"
    exit 1
fi
echo ""

# Step 3: Fix /data permissions
echo "[3/4] Fixing /data permissions..."
if sudo chown comma:comma /data 2>/dev/null; then
    echo "  ✓ Set owner to comma:comma"
else
    echo "  ⚠ Warning: Could not change owner (may already be correct)"
fi

if sudo chmod 755 /data 2>/dev/null; then
    echo "  ✓ Set permissions to 755"
else
    echo "  ⚠ Warning: Could not change permissions (may already be correct)"
fi
echo ""

# Step 4: Fix /data/openpilot permissions (recursive)
echo "[4/4] Fixing /data/openpilot permissions (recursive)..."
echo "  This may take a moment..."

if sudo chown -R comma:comma /data/openpilot 2>/dev/null; then
    echo "  ✓ Set owner to comma:comma (recursive)"
else
    echo "  ⚠ Warning: Could not change owner recursively"
fi

if sudo chmod -R 755 /data/openpilot 2>/dev/null; then
    echo "  ✓ Set permissions to 755 (recursive)"
else
    echo "  ⚠ Warning: Could not change permissions recursively"
fi
echo ""

# Verify the changes
echo "================================================"
echo "Verification"
echo "================================================"
echo ""

echo "Final permissions:"
check_permissions "/data"
echo ""
check_permissions "/data/openpilot"
echo ""

echo "================================================"
echo "Fix Complete!"
echo "================================================"
echo ""
echo "Summary:"
echo "  ✓ /data owner: comma:comma"
echo "  ✓ /data permissions: 755"
echo "  ✓ /data/openpilot owner: comma:comma (recursive)"
echo "  ✓ /data/openpilot permissions: 755 (recursive)"
echo ""
echo "Note: If you see permission warnings above, the permissions"
echo "      may have already been correct or you may need to run"
echo "      this script with appropriate privileges."
echo ""

