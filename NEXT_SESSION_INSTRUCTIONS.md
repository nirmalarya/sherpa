# Instructions for Session 91

## CRITICAL: Start Here

Session 90 implemented `sherpa generate` but **could not test it** due to missing dependencies.

## Step 1: Install CLI Dependencies (MANDATORY)

Before doing ANYTHING else, install the required libraries:

```bash
venv-312/bin/pip install click==8.1.7 rich==13.7.0
```

**Alternative:** Use the install script:
```bash
chmod +x install-cli.sh
./install-cli.sh
```

**Verify Installation:**
```bash
venv-312/bin/python -c "import rich; print(f'Rich version: {rich.__version__}')"
venv-312/bin/python -c "import click; print(f'Click version: {click.__version__}')"
```

## Step 2: Test sherpa generate

Run all three test scripts to verify functionality:

### Test 1: Node.js Integration Test
```bash
node test_sherpa_generate.js
```

**Expected Output:**
- All 6 steps should pass
- Files created in /tmp/sherpa_generate_test
- Summary showing 100% pass rate

### Test 2: Python Direct Test
```bash
venv-312/bin/python test_generate_direct.py
```

**Expected Output:**
- All verification steps pass
- Files saved to test_results_generate/

### Test 3: Bash Script Test
```bash
bash run_generate_test.sh
```

**Expected Output:**
- All checks pass (✓ symbols)
- Results saved to test_results_generate/

## Step 3: Verify Generated Files

Check that the generated files are correct:

```bash
# View generated files
cat test_results_generate/CLAUDE.md
cat test_results_generate/copilot-instructions.md
cat test_results_generate/00-sherpa-knowledge.md
```

**Verify:**
- All files contain snippet content
- Markdown formatting is correct
- Files have reasonable size (> 100 bytes)
- No obvious errors or corruption

## Step 4: Mark Feature as Passing

**ONLY IF ALL TESTS PASS**, update feature_list.json:

Find line 90 (feature: "CLI command: sherpa generate"):
```json
"passes": false
```

Change to:
```json
"passes": true
```

**IMPORTANT:** Only change the "passes" field, nothing else!

## Step 5: Commit Test Results

```bash
git add feature_list.json test_results_generate/
git commit -m "Verify CLI command: sherpa generate - all tests passing

- Installed CLI dependencies (click, rich)
- Ran 3 test suites (Node.js, Python, Bash)
- All 6 test steps verified
- Generated files validated
- Marked feature as passing in feature_list.json

Test results saved to test_results_generate/

Progress: 111 → 112 features (67.9% complete)

🏔️ Generated with Claude Code
https://claude.com/claude-code

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## Step 6: Update Progress

Update `claude-progress.txt` with:
- Session 91 completed
- sherpa generate tested and verified
- 112/165 features passing (67.9%)

## Step 7: Choose Next Feature

After sherpa generate is verified, implement the next CLI command:

**Priority Order:**
1. ✅ sherpa init (Session 89 - DONE)
2. ✅ sherpa generate (Session 90 - DONE, Session 91 - VERIFY)
3. ⏭️ sherpa run --spec (NEXT - line 107 in feature_list.json)
4. ⏭️ sherpa query (line 149)
5. ⏭️ sherpa snippets list (line 163)

**Recommended:** Implement `sherpa run --spec` in Session 91 after verification

## Common Issues & Solutions

### Issue 1: Rich Import Error
**Error:** `ModuleNotFoundError: No module named 'rich'`
**Solution:** Run Step 1 above (install dependencies)

### Issue 2: Tests Fail
**Error:** Test scripts exit with errors
**Solution:**
1. Check error message
2. Verify dependencies installed
3. Check if backend/frontend servers running
4. Review test output for specific failure

### Issue 3: Permission Denied
**Error:** Cannot execute test scripts
**Solution:**
```bash
chmod +x test_sherpa_generate.js
chmod +x test_generate_direct.py
chmod +x run_generate_test.sh
```

## Files to Review

Before starting Session 91, review these files:

1. **SESSION_90_SUMMARY.md** - What was done
2. **GENERATE_VERIFICATION.md** - Implementation details
3. **CLI_SETUP.md** - Setup instructions
4. **session_90_progress.txt** - Full progress report

## Success Criteria

Session 91 is successful when:

✅ CLI dependencies installed
✅ All 3 test scripts pass (100% pass rate)
✅ Generated files verified and validated
✅ feature_list.json updated (passes: true)
✅ Changes committed to git
✅ Progress notes updated
✅ 112/165 features passing (67.9%)

## After Successful Verification

Move on to implementing `sherpa run --spec` command:

**Feature Requirements (line 107):**
- Create test spec file
- Run sherpa run --spec command
- Verify session created
- Verify feature_list.json generated
- Verify initializer agent starts
- Verify progress tracked

This will be a more complex feature requiring:
- Session management
- Autonomous harness integration
- Progress tracking
- Database operations

**Estimated Time:** 60-90 minutes

## Quick Start Commands

```bash
# Session 91 Quick Start
./install-cli.sh                    # Install deps
node test_sherpa_generate.js        # Test
# Edit feature_list.json (line 90: passes: true)
git add feature_list.json
git commit -m "Verify sherpa generate"
# Implement sherpa run --spec
```

---

**Session 90 Status:** ✅ Implementation Complete
**Session 91 Priority:** 🔴 TEST & VERIFY sherpa generate
**Session 91 Secondary:** Implement sherpa run --spec

Good luck! 🏔️
