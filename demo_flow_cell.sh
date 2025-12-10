#!/bin/bash

# Flow Cell Demo Script
# Quick demonstration of the flow cell scanner

echo "======================================================================"
echo "FLOW CELL SCANNER DEMONSTRATION"
echo "======================================================================"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo "1. Running system diagnostics..."
echo "----------------------------------------------------------------------"
python diagnose_flow_cell.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Diagnostics failed. Please fix issues before demo."
    exit 1
fi

echo ""
echo "======================================================================"
echo "2. Camera Test"
echo "======================================================================"
echo "This will open a live camera feed window."
echo "Press 'q' to close the window and continue."
echo ""
read -p "Press Enter to test camera..."

python test_flow_cell.py --camera 0

echo ""
echo "======================================================================"
echo "3. Flow Cell Scan Demo"
echo "======================================================================"
echo "This will run a 30-second demonstration scan."
echo "You'll see:"
echo "  - Live video feed with overlay"
echo "  - Real-time statistics in this console"
echo "  - Final summary when complete"
echo ""
echo "Press 'q' in the video window to stop early, or let it run 30 seconds."
echo ""
read -p "Press Enter to start demo scan..."

python flow_cell_scanner.py --camera 0 --duration 30 --flow-rate 2.0 --interval 1.0

echo ""
echo "======================================================================"
echo "4. View Results"
echo "======================================================================"

# Find most recent results directory
LATEST_RESULTS=$(ls -td results/flow_cell_* 2>/dev/null | head -1)

if [ -n "$LATEST_RESULTS" ]; then
    echo "Results saved to: $LATEST_RESULTS"
    echo ""

    if [ -f "$LATEST_RESULTS/session_summary.txt" ]; then
        echo "Session Summary:"
        echo "----------------------------------------------------------------------"
        cat "$LATEST_RESULTS/session_summary.txt"
        echo "----------------------------------------------------------------------"
    fi

    echo ""
    echo "Files created:"
    ls -lh "$LATEST_RESULTS" | grep -v "^total" | awk '{print "  " $9 " (" $5 ")"}'
else
    echo "No results found."
fi

echo ""
echo "======================================================================"
echo "DEMO COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Assemble your flow cell (slides + masking tape)"
echo "  2. Mount on microscope and connect camera"
echo "  3. Calibrate flow rate"
echo "  4. Run full demo: python flow_cell_scanner.py --camera 0 --duration 120"
echo ""
echo "Documentation:"
echo "  Quick Start: FLOW_CELL_QUICK_START.md"
echo "  Cheat Sheet: FLOW_CELL_CHEAT_SHEET.md"
echo "  Full Manual: FLOW_CELL_SYSTEM.md"
echo ""
echo "Good luck! 🚀"
