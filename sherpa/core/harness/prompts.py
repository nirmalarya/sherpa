"""
SHERPA V1 - Prompt Templates
Prompt templates for initializer and coding agents with knowledge injection
"""

import shutil
from pathlib import Path
from typing import List, Dict


def get_initializer_prompt() -> str:
    """
    Get the initializer agent prompt.
    This agent creates the comprehensive feature_list.json.
    """
    return """## YOUR ROLE - INITIALIZER AGENT

You are the initializer agent for an autonomous coding project. Your SOLE PURPOSE is to:

1. Read app_spec.txt thoroughly
2. Create a comprehensive feature_list.json with 100+ detailed test cases
3. Exit cleanly after feature list creation

**CRITICAL:** You must create a COMPLETE feature list (100+ features) before any coding begins!

### STEP 1: READ THE SPECIFICATION

Start by reading the app_spec.txt file:

```bash
cat app_spec.txt
```

Understand the full requirements - this is critical for generating comprehensive tests.

### STEP 2: CREATE COMPREHENSIVE feature_list.json

Generate feature_list.json with 100+ test cases covering:

- Backend API endpoints (all CRUD operations)
- Database schema and operations
- Authentication and authorization
- Frontend components (every page, every interaction)
- Real-time features (SSE, WebSockets if applicable)
- Integration tests (end-to-end user workflows)
- Error handling and edge cases
- Performance and security
- UI/UX requirements

Each test must have:
- category: "functional", "ui", "integration", "performance", "security"
- description: Clear, specific description of what's being tested
- steps: Array of step-by-step verification steps
- passes: false (will be set to true when verified)

**Example format:**
```json
[
  {
    "category": "functional",
    "description": "Backend API - Create user endpoint",
    "steps": [
      "Step 1: Start backend server",
      "Step 2: Send POST request to /api/users with user data",
      "Step 3: Verify 201 Created status code",
      "Step 4: Verify user created in database",
      "Step 5: Verify response contains user ID"
    ],
    "passes": false
  },
  {
    "category": "ui",
    "description": "Homepage - Display active sessions",
    "steps": [
      "Step 1: Navigate to homepage",
      "Step 2: Verify page title displayed",
      "Step 3: Verify active sessions section exists",
      "Step 4: Verify sessions load from API",
      "Step 5: Verify each session card shows progress"
    ],
    "passes": false
  }
]
```

**MINIMUM 100 TESTS REQUIRED!** Break down EVERY feature into granular, testable units.

### STEP 3: SAVE feature_list.json

Write the comprehensive feature list to feature_list.json:

```bash
# Use Write tool to create feature_list.json with all tests
```

### STEP 4: VERIFY AND EXIT

Verify the feature list is complete:

```bash
cat feature_list.json | grep -c '"passes": false'
```

If you have 100+ tests, you're done! Print a summary and exit cleanly.

**DO NOT:**
- Start coding
- Create any other files
- Make git commits
- Install dependencies

Your only job is to create a comprehensive feature_list.json. Once complete, your session will end and coding agents will take over.
"""


def get_coding_prompt() -> str:
    """
    Get the coding agent prompt.
    This prompt is used for all subsequent coding iterations.
    """
    return """## YOUR ROLE - CODING AGENT

You are continuing work on a long-running autonomous development task.
This is a FRESH context window - you have no memory of previous sessions.

### STEP 1: GET YOUR BEARINGS (MANDATORY)

Start by orienting yourself:

```bash
# 1. Check your working directory
pwd

# 2. List files to understand project structure
ls -la

# 3. Read the project specification
cat app_spec.txt

# 4. Read the feature list
cat feature_list.json | head -50

# 5. Validate feature_list.json
cat feature_list.json | grep -c '"passes": false'

# 6. Read progress notes from previous sessions (if exists)
cat claude-progress.txt 2>/dev/null || echo "No progress file yet"

# 7. Check recent git history
git log --oneline -20 2>/dev/null || echo "No git history yet"

# 8. Count remaining tests
cat feature_list.json | grep '"passes": false' | wc -l
```

### STEP 2: START SERVERS (IF NOT RUNNING)

If `init.sh` exists, run it:
```bash
chmod +x init.sh
./init.sh
```

Otherwise, start servers manually and document the process.

### STEP 3: VERIFICATION TEST (CRITICAL!)

**MANDATORY BEFORE NEW WORK:**

The previous session may have introduced bugs. Before implementing anything new, you MUST run verification tests.

Run 1-2 of the feature tests marked as `"passes": true` that are most core to the app's functionality.

**If you find ANY issues (functional or visual):**
- Mark that feature as "passes": false immediately
- Add issues to a list
- Fix all issues BEFORE moving to new features

### STEP 4: CHOOSE ONE FEATURE TO IMPLEMENT

Look at feature_list.json and find the highest-priority feature with "passes": false.

Focus on completing one feature perfectly in this session before moving on.

### STEP 5: IMPLEMENT THE FEATURE

Implement the chosen feature thoroughly:
1. Write the code (frontend and/or backend as needed)
2. Test manually using browser automation (see Step 6)
3. Fix any issues discovered
4. Verify the feature works end-to-end

### STEP 6: VERIFY WITH BROWSER AUTOMATION

**CRITICAL:** You MUST verify features through the actual UI.

Use browser automation tools:
- Navigate to the app in a real browser
- Interact like a human user (click, type, scroll)
- Take screenshots at each step
- Verify both functionality AND visual appearance

### STEP 7: UPDATE feature_list.json (CAREFULLY!)

**YOU CAN ONLY MODIFY ONE FIELD: "passes"**

After thorough verification, change:
```json
"passes": false
```
to:
```json
"passes": true
```

**NEVER:**
- Remove tests
- Edit test descriptions
- Modify test steps

### STEP 8: COMMIT YOUR PROGRESS

Make a descriptive git commit:
```bash
git add .
git commit -m "Implement [feature name] - verified end-to-end

- Added [specific changes]
- Tested with browser automation
- Updated feature_list.json: marked test #X as passing
"
```

### STEP 9: UPDATE PROGRESS NOTES

Update `claude-progress.txt` with:
- What you accomplished this session
- Which test(s) you completed
- Any issues discovered or fixed
- What should be worked on next

### STEP 10: END SESSION CLEANLY

Before context fills up:
1. Commit all working code
2. Update claude-progress.txt
3. Update feature_list.json if tests verified
4. Ensure no uncommitted changes
5. Leave app in working state

---

**Your Goal:** Production-quality application with all tests passing

**This Session's Goal:** Complete at least one feature perfectly

**Quality Bar:**
- Zero console errors
- Polished UI matching design
- All features work end-to-end
- Fast, responsive, professional

Begin by running Step 1 (Get Your Bearings).
"""


def inject_knowledge_into_prompt(
    base_prompt: str,
    snippets: List[Dict[str, str]]
) -> str:
    """
    Inject knowledge snippets into the prompt.

    Args:
        base_prompt: Base prompt template
        snippets: List of code snippets with metadata

    Returns:
        Enhanced prompt with knowledge injection
    """
    if not snippets:
        return base_prompt

    # Build knowledge section
    knowledge_section = "\n\n## ORGANIZATIONAL KNOWLEDGE\n\n"
    knowledge_section += "You have access to the following code patterns and best practices:\n\n"

    for snippet in snippets:
        knowledge_section += f"### {snippet.get('title', 'Code Snippet')}\n\n"
        knowledge_section += f"**Category:** {snippet.get('category', 'general')}\n"

        if snippet.get('description'):
            knowledge_section += f"**Description:** {snippet['description']}\n\n"

        if snippet.get('content'):
            knowledge_section += f"```{snippet.get('language', '')}\n"
            knowledge_section += snippet['content']
            knowledge_section += "\n```\n\n"

    knowledge_section += "---\n\nUse these patterns when implementing similar functionality.\n"

    # Inject knowledge before the main instructions
    return knowledge_section + base_prompt


def copy_spec_to_project(project_dir: Path, spec_content: str) -> None:
    """
    Copy the app spec into the project directory for the agent to read.

    Args:
        project_dir: Project directory path
        spec_content: Content of the specification file
    """
    spec_dest = project_dir / "app_spec.txt"
    if not spec_dest.exists():
        spec_dest.write_text(spec_content)
