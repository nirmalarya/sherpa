# Instructions for Session 92

## Priority: Install Dependencies and Test sherpa generate

Session 91 was blocked by missing dependencies. Session 92 must resolve this before proceeding.

---

## STEP 1: Install Missing Dependency (CRITICAL)

The `rich` library is required but not installed in venv-312.

### Manual Installation (If you have access)

```bash
cd /Users/nirmalarya/Workspace/auto-harness/autonomous-coding/generations/sherpa
venv-312/bin/pip install rich==13.7.0
```

### Using the Install Script

```bash
# If you can execute Python:
venv-312/bin/python install_deps.py
```

### Verify Installation

```bash
venv-312/bin/python -m pip list | grep rich
# Should show: rich==13.7.0
```

---

## STEP 2: Test sherpa generate Command

Once dependencies are installed, run all three test suites:

### Test Suite 1: Node.js Integration Test (Recommended)

```bash
node test_sherpa_generate.js
```

**Expected Output:**
```
🧪 Testing sherpa generate command

Step 1: Run sherpa generate command
[command output showing successful execution]

Step 2: Verify .cursor/rules/ directory created
✓ .cursor/rules/ directory exists
✓ .cursor/rules/00-sherpa-knowledge.md file exists

Step 3: Verify CLAUDE.md file created with injected snippets
✓ CLAUDE.md file exists
✓ CLAUDE.md contains "Knowledge Base" section
✓ CLAUDE.md contains snippets content

Step 4: Verify copilot-instructions.md file created
✓ copilot-instructions.md file exists
✓ copilot-instructions.md contains "Code Patterns" section
✓ copilot-instructions.md has reasonable size

Step 5: Verify all files contain relevant knowledge snippets
✓ Knowledge file contains organizational snippets
✓ Files are properly formatted markdown

Step 6: Verify success message with file paths displayed
✓ Command output contains success message
✓ Command output lists generated files

============================================================
Test Summary
============================================================
Total tests: 12
Passed: 12
Failed: 0
Success rate: 100.0%

✓ All tests passed! 🎉
Test results saved to: test_results_generate
```

### Test Suite 2: Python Direct Test

```bash
venv-312/bin/python test_generate_core.py
```

### Test Suite 3: Bash Script Test

```bash
bash run_generate_test.sh
```

---

## STEP 3: Verify Generated Files

Check the generated files to ensure quality:

```bash
# View the generated files
cat test_results_generate/CLAUDE.md
cat test_results_generate/copilot-instructions.md
cat test_results_generate/.cursor/rules/00-sherpa-knowledge.md
```

**Quality Checklist:**
- [ ] All files exist
- [ ] Files contain snippet content
- [ ] Markdown formatting is correct
- [ ] Files have reasonable size (> 100 bytes)
- [ ] No errors or corruption
- [ ] Snippets are properly injected

---

## STEP 4: Update feature_list.json

**ONLY IF ALL TESTS PASS**, update the feature list:

Find test #7 (line ~81-90 in feature_list.json):

```json
{
  "category": "functional",
  "description": "CLI command: sherpa generate - Create instruction files for interactive agents (.cursor/rules/, CLAUDE.md, copilot-instructions.md)",
  "steps": [
    "Step 1: Run 'sherpa generate' command",
    "Step 2: Verify .cursor/rules/ directory created",
    "Step 3: Verify CLAUDE.md file created with injected snippets",
    "Step 4: Verify copilot-instructions.md file created",
    "Step 5: Verify all files contain relevant knowledge snippets",
    "Step 6: Verify success message with file paths displayed"
  ],
  "passes": false  // <-- Change this to true
}
```

**Change ONLY the "passes" field:**

```json
  "passes": true
```

**DO NOT:**
- Remove or modify test steps
- Change descriptions
- Reorder tests
- Combine tests

---

## STEP 5: Commit Test Results

```bash
git add feature_list.json test_results_generate/
git commit -m "Verify CLI command: sherpa generate - all tests passing

- Installed CLI dependencies (rich==13.7.0)
- Ran 3 test suites (Node.js, Python, Bash)
- All 12 test steps verified ✅
- Generated files validated
- Marked feature as passing in feature_list.json

Test results saved to test_results_generate/

Progress: 111 → 112 features passing (67.9% complete)

🏔️ Generated with Claude Code
https://claude.com/claude-code

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## STEP 6: Update Progress Notes

Update `claude-progress.txt`:

```
SHERPA V1 - Session 92 Progress Report
======================================

Date: December 23, 2025 (Session 92)

Previous Session: Session 91 - Blocked by dependency installation

✅ COMPLETED TASKS
==================

1. Installed CLI Dependencies
   - rich==13.7.0 ✅
   - click==8.1.7 (already installed) ✅

2. Tested sherpa generate Command
   - Node.js test suite: 12/12 passed ✅
   - Python test suite: All tests passed ✅
   - Bash test suite: All tests passed ✅

3. Verified Generated Files
   - CLAUDE.md: Valid ✅
   - copilot-instructions.md: Valid ✅
   - .cursor/rules/00-sherpa-knowledge.md: Valid ✅

4. Updated feature_list.json
   - Test #7 marked as passing ✅

Progress: 111 → 112 features passing (67.9% complete)
```

---

## STEP 7: Choose Next Feature to Implement

After successfully verifying sherpa generate, choose the next CLI command:

### Recommended Next Features (in order):

1. **sherpa run --spec** (Test #8, line ~92-103)
   - More complex, requires session management
   - Execute autonomous harness with spec file
   - 6 test steps

2. **sherpa query** (Test #10, line ~120-128)
   - Query Bedrock Knowledge Base
   - Display results with Rich formatting
   - 5 test steps

3. **sherpa snippets list** (Test #11, line ~130-141)
   - List all available snippets
   - Show built-in, project, local snippets
   - Rich table formatting
   - 6 test steps

4. **sherpa status** (Test #12, line ~143-154)
   - Show active sessions
   - Display progress percentage
   - Rich table output
   - 6 test steps

### Implementation Approach

For each CLI command:
1. Create `sherpa/cli/commands/[command_name].py`
2. Import and register in `sherpa/cli/main.py`
3. Implement with Rich formatting (console, tables, panels)
4. Create test script (Node.js preferred)
5. Test thoroughly with browser automation if applicable
6. Update feature_list.json
7. Commit with descriptive message

---

## Alternative: If Dependencies Still Cannot Be Installed

If the dependency blocker persists, consider implementing backend features instead:

### Azure DevOps Integration (API-based, no CLI)

1. **Azure DevOps PAT authentication** (Test #13)
   - Backend API endpoints
   - No rich dependency required
   - Can test via browser automation

2. **Azure DevOps pull work items** (Test #14)
   - Backend integration
   - API-based testing

### Other Non-CLI Features

- Additional API endpoints
- Frontend enhancements
- Database features
- Integration features

---

## Success Criteria for Session 92

Session 92 is successful when:

✅ Dependencies installed (rich library)
✅ All 3 test suites pass (100% pass rate)
✅ Generated files verified and validated
✅ feature_list.json updated (passes: true for test #7)
✅ Changes committed to git
✅ Progress notes updated
✅ 112/165 features passing (67.9%)
✅ Ready to implement next feature

---

## Troubleshooting

### Issue: rich Import Error

**Error:**
```
ModuleNotFoundError: No module named 'rich'
```

**Solution:**
```bash
venv-312/bin/pip install rich==13.7.0
```

### Issue: Test Script Fails

**Check:**
1. Are dependencies installed? `venv-312/bin/pip list | grep rich`
2. Is the backend running? `ps aux | grep uvicorn`
3. Are there any Python errors in the test output?

**Debug:**
```bash
# Run with verbose output
node test_sherpa_generate.js 2>&1 | tee test_output.log
```

### Issue: Permission Denied on Scripts

**Solution:**
```bash
chmod +x test_sherpa_generate.js
chmod +x test_generate_core.py
chmod +x run_generate_test.sh
```

---

## Quick Start Commands for Session 92

```bash
# 1. Install dependency
venv-312/bin/pip install rich==13.7.0

# 2. Run tests
node test_sherpa_generate.js

# 3. If all pass, edit feature_list.json
# Change line ~90: "passes": true

# 4. Commit
git add feature_list.json test_results_generate/
git commit -m "Verify CLI command: sherpa generate - all tests passing"

# 5. Update progress
# Edit claude-progress.txt

# 6. Choose next feature (sherpa run --spec recommended)
```

---

## Files to Reference

Before starting Session 92, review:

1. **SESSION_91_BLOCKER.md** - Blocker details from Session 91
2. **SESSION_90_SUMMARY.md** - Implementation details
3. **GENERATE_VERIFICATION.md** - Verification documentation
4. **claude-progress.txt** - Current progress (Session 91)
5. **feature_list.json** - Test specifications

---

## Expected Timeline

- **Step 1 (Install):** 2 minutes
- **Step 2 (Test):** 5 minutes
- **Step 3 (Verify):** 3 minutes
- **Step 4 (Update JSON):** 2 minutes
- **Step 5 (Commit):** 2 minutes
- **Step 6 (Progress):** 3 minutes
- **Step 7 (Next Feature):** 45-60 minutes

**Total Session Time:** ~60 minutes (including next feature implementation)

---

## Key Reminders

1. **ALWAYS verify no regressions** (Step 3 - test homepage/sessions)
2. **Test thoroughly** before marking features as passing
3. **Update feature_list.json carefully** (only change "passes" field)
4. **Commit frequently** with descriptive messages
5. **Document clearly** for future sessions

---

**Session 91 Status:** ✅ Completed (blocker documented)
**Session 92 Priority:** 🔴 Install dependencies and test sherpa generate
**Session 92 Secondary:** Implement next CLI command (sherpa run --spec)

Good luck! 🏔️
