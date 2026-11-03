#!/bin/bash
# Start Chrome with remote debugging on port 9222 (macOS/Linux)
# Uses a separate profile so it doesn't interfere with your normal Chrome
# Auto-hides the Chrome window so it runs invisibly in the background

PORT="${1:-9222}"
PROFILE_DIR="${HOME}/ChromeDebugProfile"

# Detect Chrome path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif command -v google-chrome &>/dev/null; then
    CHROME="google-chrome"
elif command -v google-chrome-stable &>/dev/null; then
    CHROME="google-chrome-stable"
else
    echo "Chrome not found. Install Google Chrome first."
    exit 1
fi

# Check if already running
if curl -s "http://localhost:${PORT}/json/version" &>/dev/null; then
    echo "Debug Chrome already running on port ${PORT}"
    exit 0
fi

echo "Starting Chrome with remote debugging on port ${PORT}..."

# Start Chrome off-screen so it's invisible
"$CHROME" \
    --remote-debugging-port="$PORT" \
    --user-data-dir="$PROFILE_DIR" \
    --no-first-run \
    --no-default-browser-check \
    --window-position=-32000,-32000 &

# On macOS: hide Chrome from Dock and Cmd+Tab after launch
if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 2
    osascript -e 'tell application "System Events" to set visible of process "Google Chrome" to false' 2>/dev/null
fi

echo "Chrome debug started and hidden (port ${PORT})"
echo "Verify: http://localhost:${PORT}/json/version"
