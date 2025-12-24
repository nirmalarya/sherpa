#!/bin/bash
# Second cleanup pass - Clean root directory to essentials only

set -e

echo "🧹 Final cleanup - organizing root directory..."

# Move all run scripts to scripts/
echo "Moving run scripts..."
mv run_*.sh scripts/ 2>/dev/null || true
mv run.sh scripts/ 2>/dev/null || true

# Move install scripts to scripts/
echo "Moving install scripts..."
mv install-*.sh scripts/ 2>/dev/null || true

# Move start scripts to scripts/
echo "Moving start scripts..."
mv start*.sh scripts/ 2>/dev/null || true

# Move fix scripts to scripts/
echo "Moving fix scripts..."
mv fix_*.sh scripts/ 2>/dev/null || true

# Move setup scripts to scripts/
echo "Moving setup scripts..."
mv setup*.sh scripts/ 2>/dev/null || true
mv setup.py scripts/ 2>/dev/null || true
mv verify-setup.sh scripts/ 2>/dev/null || true

# Move verify scripts to scripts/verify/
echo "Moving remaining verify scripts..."
mv verify_*.py scripts/verify/ 2>/dev/null || true

# Move utility Python scripts to scripts/
echo "Moving utility scripts..."
mv delete_db.py scripts/ 2>/dev/null || true
mv final_stats.js scripts/ 2>/dev/null || true

# Move .sessions if exists
if [ -d ".sessions" ]; then
    echo ".sessions/ directory already exists (good!)"
else
    mkdir -p .sessions
    mv SESSION_*.md .sessions/ 2>/dev/null || true
    mv NEXT_SESSION_*.md .sessions/ 2>/dev/null || true
fi

# Create docs/archive for old session files if not in .sessions
mkdir -p docs/archive
mv session_*.txt docs/archive/ 2>/dev/null || true
mv session_*.html docs/archive/ 2>/dev/null || true

# Move test_results to scripts/
mv test_results_generate scripts/ 2>/dev/null || true

# Move specs examples to docs/
mkdir -p docs/examples
mv specs/ docs/examples/ 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Root directory now contains:"
ls -1
echo ""
echo "File count:"
ls -1 | wc -l
echo ""
echo "Should be ~15-20 essential files only!"

