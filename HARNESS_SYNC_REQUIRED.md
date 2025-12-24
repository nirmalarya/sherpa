# ⚠️ SHERPA Harness Code - Sync Required

## Critical Dependency

SHERPA contains a **copy** of autonomous-harness code in:
```
sherpa/core/harness/
├── agent_client.py
├── autonomous_runner.py
└── prompts.py
```

**These files came from:** `/Users/nirmalarya/Workspace/auto-harness/autonomous-coding/`

---

## 🚨 When autonomous-harness is Enhanced

**SHERPA's harness code MUST be updated!**

### Enhancements Planned for autonomous-harness v2.0:
1. Brownfield/enhancement mode
2. Stop condition (prevent infinite work)
3. TODO prevention (quality gate)
4. File organization rules
5. Linear tracker
6. Regression testing

**All of these improvements should flow to SHERPA!**

---

## 🔄 Sync Strategy

### Option 1: Git Submodule (Recommended)
```bash
# In SHERPA repo
git submodule add https://github.com/nirmalarya/autonomous-harness harness
```

**Pros:**
- ✅ Always in sync
- ✅ One source of truth
- ✅ Easy to update

**Cons:**
- ⚠️ Adds dependency

### Option 2: Import as Package
```bash
# In SHERPA
pip install autonomous-harness

# In code
from autonomous_harness import run_autonomous_session
```

**Pros:**
- ✅ Standard Python packaging
- ✅ Versioned dependencies

**Cons:**
- ⚠️ Requires autonomous-harness to be published

### Option 3: Manual Sync (Current)
```bash
# Manually copy when autonomous-harness updates
cp -r ../autonomous-harness/agent.py sherpa/core/harness/
```

**Pros:**
- ✅ Full control

**Cons:**
- ❌ Easy to forget
- ❌ Version drift

---

## 📋 Sync Checklist

**When autonomous-harness v2.0 releases:**

- [ ] Review changes in autonomous-harness
- [ ] Update SHERPA's harness code:
  - [ ] sherpa/core/harness/agent_client.py
  - [ ] sherpa/core/harness/autonomous_runner.py
  - [ ] sherpa/core/harness/prompts.py
- [ ] Test SHERPA still works
- [ ] Update SHERPA version (v1.1 or v2.0)
- [ ] Document changes in CHANGELOG
- [ ] Push to GitHub

---

## 🎯 Future: Make SHERPA Use autonomous-harness

**v2.0 Goal:**
```python
# Instead of embedded copy, import from package
from autonomous_harness import AutonomousAgent

# SHERPA just adds its knowledge layer on top
class SherpaAgent(AutonomousAgent):
    def inject_knowledge(self, prompt):
        snippets = self.knowledge_base.query(prompt)
        return f"{prompt}\n\nRelevant Snippets:\n{snippets}"
```

**Benefits:**
- ✅ Always latest harness features
- ✅ No duplicate code
- ✅ Easier to maintain

---

**Action Required:** When autonomous-harness v2.0 is ready, sync SHERPA!

