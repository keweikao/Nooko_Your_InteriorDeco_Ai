# Development Guidelines - Sales AI Automation V2.0

**Purpose**: Define mandatory practices for all development activities to ensure continuity across different AI assistants.

**Status**: Enforced from 2025-01-29
**Applies to**: All AI assistants, developers, and contributors

---

## 🚨 Core Principle

### Every development activity MUST be recorded before the session ends

This is not optional. Failure to record development activities breaks continuity and wastes time for future AI assistants.

> 想快速了解完整作業流程，請參考 `docs/ai-collaboration-playbook.md`（AI 協作手冊），其中彙整了標準開發順序、紀錄方式與交接模板。

---

## 📋 Mandatory Recording Rules

### Rule 1: Record Every Session ✅ REQUIRED

**WHEN**: At the end of every development session, before saying goodbye to the user

**WHERE**: `DEVELOPMENT_LOG.md`

**HOW**: Add a new session entry using the provided template

**Template Location**: See bottom of `DEVELOPMENT_LOG.md`

**What to Record**:

- [ ] Session duration and AI model used
- [ ] Objectives completed (checked/unchecked)
- [ ] Files created or modified (with line counts if significant)
- [ ] Key discussions and decisions (with user quotes)
- [ ] Technical highlights (architecture, performance, costs)
- [ ] Known issues and risks (with mitigation strategies)
- [ ] Open questions (with status)
- [ ] Next session preparation (action items for next AI)

**Example**:

```markdown
### Session 2: 2025-02-01 (POC 1-3 Execution)

**Duration**: 4 hours
**AI Model**: Claude Sonnet 4.5
**User**: Stephen

### Objectives Completed ✅
- [x] Execute POC 1: Whisper performance test
- [x] Execute POC 2: Multi-agent parallel test
- [x] Execute POC 3: Gemini structured output test
- [ ] Execute POC 4-6 (deferred to next session)

### Files Created/Modified
**Created**:
- `specs/001-sales-ai-automation/poc-tests/results/poc1_results.json`
- `specs/001-sales-ai-automation/poc-tests/results/poc2_results.json`

**Modified**:
- `specs/001-sales-ai-automation/plan.md` (Updated with validated Whisper config)

### Key Discussions & Decisions
### 1. Whisper Model Selection
**User Request**: "POC 1 結果顯示 large-v3 太慢，我們應該用 medium 嗎？"
**Decision**: Continue with large-v3, enable GPU acceleration
**Rationale**: large-v3 quality (92%) significantly better than medium (78%). GPU adds only $12/month.

...
```text

---

### Rule 2: Update Quick Reference When Needed ✅ REQUIRED

**WHEN**: When a new critical decision is made OR project status changes

**WHERE**: `DEVELOPMENT_LOG.md` → "Quick Reference for New AI Assistants" section

**WHAT**: Update the decision table, feature list, or current status

**Example Updates**:

- New technology choice (e.g., switched from Firestore to PostgreSQL)
- New feature added (e.g., added Agent 7 for email analysis)
- Budget change (e.g., budget increased to $60/month)
- Current phase change (e.g., from Phase 0 to Phase 1)

---

### Rule 3: Create Session Summary for User ✅ REQUIRED

**WHEN**: At the end of every session, after updating DEVELOPMENT_LOG.md

**WHERE**: As a message to the user (not a file)

**FORMAT**:

```markdown
## 📋 Session Summary

**Today's Work** (X hours):
- ✅ Completed objective 1
- ✅ Completed objective 2
- ⏸️ Partially completed objective 3 (reason)

**Key Decisions**:
1. Decision 1 (rationale)
2. Decision 2 (rationale)

**Files Changed**:
- Created: file1.md, file2.py
- Modified: file3.md (reason)

**Next Steps**:
- [ ] Action item 1
- [ ] Action item 2

**For Next AI Assistant**:
- Must read: DEVELOPMENT_LOG.md Session X
- Current status: [phase/milestone]
- Blockers: [any blockers or dependencies]

✅ All work has been recorded in DEVELOPMENT_LOG.md Session X
```text

---

### Rule 4: Update Project Status ✅ REQUIRED

**WHEN**: When phase or major milestone changes

**WHERE**:

1. `DEVELOPMENT_LOG.md` → "Current Status" section
2. `PROJECT_README.md` → "Project Status" section
3. `QUICK_START_FOR_AI.md` → "Start Here" section

**WHAT**: Update current phase, last updated date, next steps

---

### Rule 5: Document New Files ✅ REQUIRED

**WHEN**: Every time you create a new file

**WHERE**: `DEVELOPMENT_LOG.md` → Current session → "Files Created/Modified"

**FORMAT**:

```markdown
**Created**:
- `path/to/file.ext` (description, line count if >100 lines)
```text

---

### Rule 6: Complete the PR Checklist ✅ REQUIRED

**WHEN**: Before開 PR、合併分支或請求審查時

**WHERE**: `docs/checklists/pr.md`

**WHAT**:
- 勾選所有適用項目（特別是 `DEVELOPMENT_LOG.md` 活動紀錄與待辦追蹤欄位）
- 在 PR 描述中註明已完成的核對清單項目（若由語言模型執行，也須在回覆中摘要）
- 若有項目無法完成，需明確說明原因與風險並標註負責人

**Example**:

```markdown
**Created**:
- `services/transcription-service/src/main.py` (FastAPI app, 234 lines)
- `services/transcription-service/Dockerfile` (Container config)
```text

---

### Rule 7: Document All Decisions ✅ REQUIRED

**WHEN**: Every time you make a technical or design decision

**WHERE**: `DEVELOPMENT_LOG.md` → Current session → "Key Discussions & Decisions"

**FORMAT**:

```markdown
### [Number]. [Decision Topic]
**User Request**: "[Original user quote if applicable]"
**Decision**: [What was decided]
**Rationale**: [Why this decision was made]
**Alternatives Considered**: [Other options considered]
**Trade-offs**: [What was gained/lost]
```text

**Example**:

```markdown
### 3. Database Choice for POC
**User Request**: "Firestore 太慢了，可以用 PostgreSQL 嗎？"
**Decision**: Switch to PostgreSQL for POC phase only
**Rationale**:
- POC needs faster queries for testing (Firestore: 300ms, PostgreSQL: 50ms)
- Easier to seed test data
- Can still use Firestore for production if POC validates performance
**Alternatives Considered**:
- Redis (too volatile for POC)
- MySQL (team less familiar)
**Trade-offs**:
- Gained: Faster development, easier testing
- Lost: One more migration step if we keep PostgreSQL for production
```text

---

## 🧱 Architectural Principles

### Rule 8: Feature Componentization ✅ REQUIRED

**WHEN**: When developing new features, especially on the frontend (React).

**WHAT**: Encapsulate distinct features into their own standalone components. A parent component should act as a container, composing these feature components, rather than defining large blocks of feature logic internally.

**WHY**:
- **Modularity**: Makes the codebase easier to understand, navigate, and maintain.
- **Reusability**: Components can be reused in different parts of the application.
- **Flexibility**: Features can be easily added, removed, or swapped out by changing the composition in the parent component, without requiring large-scale refactoring.
- **Testability**: Independent components are easier to unit test in isolation.

**Example**:
- **Bad**: A single `FinalResult.jsx` component that contains all the JSX and logic for displaying a spec sheet, a budget analysis, a quote, and a feedback form.
- **Good**:
    - `FinalResult.jsx`: Acts as a container, managing layout and state.
    - `components/results/SpecCard.jsx`: A component dedicated to displaying the spec sheet.
    - `components/results/BudgetCard.jsx`: A component for the budget analysis.
    - `components/results/QuoteTable.jsx`: A component for the quote.
    - `components/FeedbackFlow.jsx`: A component that handles the entire multi-step feedback and booking process.
    - `FinalResult.jsx` then imports and composes these components.

### Rule 9: LLM Usage and Token Optimization ✅ REQUIRED

**WHEN**: Anytime an LLM (AI assistant) needs to retrieve information from project documentation (specs, plans, constitution, tasks).

**WHAT**:
- **DO NOT** directly read the full content of Markdown files (e.g., `spec.md`, `plan.md`, `tasks.md`, `constitution.md`).
- **INSTEAD**, use provided Code APIs or CLI tools (e.g., from `.specify/mcp-server/servers/` or `./.specify/llm`) to fetch only the necessary, summarized, or specific sections of information.
- **CONTROL TOKEN USAGE**: Always aim to minimize the number of tokens consumed for information retrieval.

**WHY**:
- **Cost Efficiency**: Directly reading large Markdown files consumes a significant amount of tokens, leading to higher operational costs.
- **Performance**: Reduces latency by processing smaller, more focused contexts.
- **Context Management**: Prevents context window overflow and improves the LLM's ability to focus on the most relevant information.

**Example**:
- **❌ Wrong**:
    ```
    請讀取 .specify/memory/constitution.md 的完整內容，
    我要了解專案的開發原則。
    ```
- **✅ Correct**:
    ```typescript
    // Assuming a Code API is available
    import * as constitution from './.specify/mcp-server/servers/constitution/index.js';
    const summary = await constitution.getConstitutionSummary();
    console.log(summary.summary); // Only uses ~300 tokens instead of 2,340 tokens!
    ```
    Or, if using a CLI:
    ```bash
    ./.specify/llm constitution-summary
    ```
- **❌ Wrong**:
    ```
    請讀取 spec.md、plan.md 和 tasks.md 的完整內容，
    找出任務 3.2 的資訊，然後協助我實作。
    ```
- **✅ Correct**:
    ```typescript
    // Assuming a Code API is available
    import * as tasks from './.specify/mcp-server/servers/tasks/index.js';
    const task = await tasks.getTaskById({ taskId: '3.2', includeContext: true });
    console.log(`任務: ${task.title}`); // Only uses ~1,200 tokens instead of 12,000 tokens!
    ```
    Or, if using a CLI:
    ```bash
    ./.specify/llm task --id 3.2 --context
    ```

### Rule 10: Subagent Usage and Best Practices ✅ REQUIRED

**WHEN**: When a task can be broken down into specialized sub-tasks or requires specific expertise.

**WHAT**:
- **UTILIZE SUBAGENTS**: Leverage specialized subagents (e.g., `speckit-implementer`, `speckit-planner`, `speckit-researcher`, `speckit-tester`, `speckit-documenter`, `speckit-debugger`) for their defined purposes.
- **CONTROL TOKEN BUDGETS**: Adhere to the token budgets specified for each subagent to maintain cost-efficiency and performance.
- **DEFINE CLEAR TASK BOUNDARIES**: Ensure each subagent's task has a clear scope, especially regarding file modifications, to prevent conflicts.
- **RESPECT DEPENDENCIES**: Execute tasks with dependencies in the correct sequence.
- **MONITOR PROGRESS**: Regularly check the status of subagent tasks and overall implementation progress.

**WHY**:
- **Speed**: Subagents enable parallel execution, significantly reducing overall task completion time.
- **Cost Efficiency**: Combined with MCP API usage, subagents optimize token consumption.
- **Quality**: Specialized agents provide more focused and higher-quality results.
- **Scalability**: Facilitates handling larger and more complex projects.

**Available Subagents (Examples)**:
- `speckit-implementer`: For implementing features, modifying code, writing unit tests. (Token budget: < 3,500 per task)
- `speckit-planner`: For analyzing task dependencies, creating execution plans, estimating workload. (Token budget: < 2,000)
- `speckit-researcher`: For investigating requirements, querying technical decisions, validating alignment. (Token budget: < 1,500)
- `speckit-tester`: For writing and executing tests, verifying coverage. (Token budget: < 2,500)
- `speckit-documenter`: For updating API documentation, writing user guides, updating technical documents. (Token budget: < 1,000)
- `speckit-debugger`: For analyzing logs, identifying root causes of errors, suggesting solutions. (Token budget: < 2,000)

**Best Practices**:
- Always use MCP API or file paths for information retrieval.
- Report token usage upon completion.
- Clearly define file modification scopes for parallel tasks.
- Execute dependent tasks sequentially.

### Rule 11: LLM Startup and Rule Adherence ✅ REQUIRED

**WHEN**: At the beginning of a new session, or when switching LLMs, or if the LLM seems to deviate from project rules.

**WHAT**:
- **INITIALIZE LLM**: Use a defined startup process to ensure the LLM understands and adheres to the project's rules, especially regarding token optimization and API usage.
- **VERIFY UNDERSTANDING**: After startup, test the LLM's comprehension of the rules (e.g., by asking for task information that requires API usage).
- **CORRECT DEVIATIONS**: If the LLM fails to follow rules, re-initialize it.

**WHY**:
- **Consistency**: Ensures all LLM interactions follow established best practices.
- **Efficiency**: Reinforces token optimization and correct API usage from the start.
- **Reliability**: Prevents misinterpretations and ensures the LLM operates within expected parameters.

**Startup Methods (Examples)**:
- **Full Startup (Recommended for first use/unfamiliar LLM)**: Execute a comprehensive initialization script (e.g., `.specify/STARTUP.md`).
- **Quick Startup (Daily use/familiar LLM)**: Provide a concise reminder of core rules (e.g., "Do not read full docs, use APIs, token budget < 1,500").
- **Minimal Startup (Highly familiar LLM)**: A very brief reminder (e.g., "Read .specify/QUICK-START.txt").

**Verification**:
- Test by asking for information that requires using the MCP API (e.g., "請協助我查看任務 3.2 的資訊。").
- Correct response should involve using the API; incorrect response (e.g., trying to read the full Markdown file) requires re-initialization.

### Rule 12: LLM Project Initialization and Mandatory Rules ✅ REQUIRED

**WHEN**: Upon entering a Speckit MCP project, or when an LLM needs a full re-initialization.

**WHAT**:
- **READ GUIDES**: Immediately read `.specify/LLM-USAGE-GUIDE.md` to understand MCP Code Execution core concepts, prohibitions, and API usage.
- **ADHERE TO MANDATORY RULES**:
    - **PROHIBITED ACTIONS**:
        - **DO NOT** directly read files: `.specify/memory/constitution.md`, `.specify/specs/*/spec.md`, `.specify/specs/*/plan.md`, `.specify/specs/*/tasks.md`.
        - **DO NOT** use `fs.readFileSync()`, `fs.readFile()`, `fs.promises.readFile()`, or any direct file reading methods for the above documents.
        - **DO NOT** request full document content from the user.
    - **MANDATORY USAGE**:
        - **ONLY** access information via TypeScript APIs (e.g., `constitution.getConstitutionSummary()`, `tasks.getTaskById()`) or CLI tools (e.g., `./.specify/llm constitution-summary`, `./.specify/llm task --id 3.2 --context`).
- **TOKEN USAGE TARGETS**:
    - Constitution Phase: < 500 tokens
    - Specify Phase: < 800 tokens
    - Plan Phase: < 1,000 tokens
    - Implement Single Task: < 1,500 tokens
    - Full Implement Process: < 2,000 tokens
- **SELF-CHECK BEFORE RESPONSE**: Before generating any response, perform a self-check:
    - ✅ Used MCP API or CLI tool.
    - ❌ Did not directly read prohibited files.
    - ❌ Did not use `fs.readFile*` for prohibited files.
    - ❌ Did not request full document content from the user.
    - 📊 Response token usage is within target.
    - 🔍 Estimated token count is noted at the end of the response.
- **CORRECT DEVIATIONS**: If any self-check fails, immediately correct the behavior before responding.

**WHY**:
- **Strict Adherence**: Ensures the LLM operates within the highly optimized and controlled environment of the Speckit MCP.
- **Efficiency & Cost**: Enforces token economy and prevents wasteful operations.
- **Project Integrity**: Maintains consistency in how information is accessed and processed across all LLM interactions.

---

## 🎯 Development Workflow with Recording

### Standard Development Cycle

> 🌐 詳細步驟與模板請參考 `docs/ai-collaboration-playbook.md`。下列為摘要：

```text
1. Read Context
   ├─ Read QUICK_START_FOR_AI.md (5 min)
   ├─ Read DEVELOPMENT_LOG.md (last session)
   └─ Read relevant spec/plan files

2. Understand Request
   ├─ Clarify ambiguities with user
   ├─ Check if decision was already made (DEVELOPMENT_LOG.md)
   └─ Confirm scope with user

3. Execute Work
   ├─ Write code / create files
   ├─ Test functionality
   └─ Fix issues

4. Record Work ⚠️ MANDATORY
   ├─ Update DEVELOPMENT_LOG.md (new session entry)
   ├─ Update QUICK_START_FOR_AI.md (if needed)
   ├─ Update PROJECT_README.md (if status changed)
   └─ Create session summary for user

5. Handoff
   ├─ Provide session summary to user
   ├─ Confirm all work is recorded
   └─ Provide clear next steps
```text

---

## 🧰 Tooling Requirements

### Markdown Formatting Compliance ✅ REQUIRED

- **WHEN**: Anytime Markdown files are added or modified (prompts, specs, docs, logs).  
- **COMMAND**: Run `npx markdownlint-cli2 --fix "**/*.md" "#node_modules"` from the repo root before committing or pushing.  
- **VERIFY**: Follow with `npx markdownlint-cli2 "**/*.md" "#node_modules"` to ensure zero lint errors.  
- **WHY**: Prevents CI failures (`Normalize markdown formatting for agent prompts #6`) and keeps prompts/specs consistent across agents.  
- **RECORD**: Note the lint pass in `DEVELOPMENT_LOG.md` when it resolves or prevents formatting issues.

> Tip: If `npx` prompts for install, run `npm install` once. Re-run the lint command after large prompt updates—especially agent prompt Markdown files.

---

## 🔍 Self-Check Before Ending Session

Before saying goodbye to the user, verify:

- [ ] I have added a new session entry to DEVELOPMENT_LOG.md
- [ ] All files created/modified are listed
- [ ] All decisions are documented with rationale
- [ ] All technical highlights are recorded
- [ ] Open questions are listed
- [ ] Next steps are clear for next AI assistant
- [ ] I have updated QUICK_START_FOR_AI.md if needed
- [ ] I have updated PROJECT_README.md if phase changed
- [ ] I have provided a session summary to the user
- [ ] User confirms the summary is accurate

### If ANY checkbox is unchecked, DO NOT end the session. Complete the recording first.

---

## 🚫 Common Mistakes to Avoid

### ❌ Mistake 1: "I'll record it later"

**Problem**: "Later" never comes. The next AI assistant has no context.

**Solution**: Record BEFORE ending the session. Make it the last task.

---

### ❌ Mistake 2: Vague descriptions

**Bad**: "Fixed some bugs"
**Good**: "Fixed Whisper timeout issue (increased timeout from 5min to 10min in transcription-service/src/transcriber.py:45)"

---

### ❌ Mistake 3: Not recording decisions

**Bad**: Silently switch from Firestore to PostgreSQL
**Good**: Document why, what user said, trade-offs, and update plan.md

---

### ❌ Mistake 4: Not documenting failed attempts

**Bad**: Only record successful work
**Good**: Record what was tried, why it failed, what was learned

**Example**:

```markdown
### Known Issues & Risks
1. **POC 2 failed with rate limit errors**
   - Attempted: Parallel execution of 10 cases (50 Gemini calls)
   - Result: 30% rate limit errors
   - Root Cause: Free tier limited to 15 RPM
   - Mitigation: Implemented token bucket (max 10 calls/min)
   - Status: Re-running POC 2 tomorrow
```text

---

### ❌ Mistake 5: Incomplete handoff

**Bad**: "I did the POCs. Bye!"
**Good**: "I completed POC 1-3. Results in `poc-tests/results/`. POC 1 GO, POC 2 GO with mitigation, POC 3 NO-GO (need to switch to function calling). Next AI should: 1) Review POC 3 failure, 2) Implement Gemini function calling, 3) Re-run POC 3, 4) Continue with POC 4-6. All details in DEVELOPMENT_LOG.md Session 2."

---

## 📚 Documentation Hierarchy

### Level 1: Session Record (DEVELOPMENT_LOG.md)

- **Purpose**: Complete historical record
- **Audience**: Future AI assistants
- **Update Frequency**: Every session
- **Detail Level**: High (include everything)

### Level 2: Quick Reference (QUICK_START_FOR_AI.md)

- **Purpose**: Fast onboarding for new AI
- **Audience**: New AI assistants (first 5 minutes)
- **Update Frequency**: When critical info changes
- **Detail Level**: Medium (key decisions only)

### Level 3: Project Overview (PROJECT_README.md)

- **Purpose**: Project status and navigation
- **Audience**: Humans and AI (project overview)
- **Update Frequency**: When phase/status changes
- **Detail Level**: Low (high-level summary)

### Level 4: Technical Specs (spec.md, plan.md, research.md)

- **Purpose**: Detailed specifications
- **Audience**: Implementers
- **Update Frequency**: When requirements/design changes
- **Detail Level**: Very High (implementation details)

---

## 🔧 Special Scenarios

### Scenario 1: Emergency Stop (User Needs to Leave)

**If user must leave unexpectedly**:

1. Immediately save current work
2. Create a minimal session entry:

   ```markdown
   ### Session X: YYYY-MM-DD (Incomplete Session)

   **Status**: ⚠️ INCOMPLETE - User had to leave
   **Duration**: X hours (interrupted)
   **AI Model**: [Your model]

   #### Work in Progress
   - Started: [what you were doing]
   - Completed: [what was finished]
   - Not completed: [what was not finished]
   - Current state: [file changes, partial code, etc.]

   #### Next AI Must
   1. Review incomplete work in [file paths]
   2. Decide: Keep or discard partial implementation
   3. Continue from [specific point]

   #### Files with Unsaved Changes
   - `path/to/file` (has uncommitted changes)
```text

3. Inform user: "I've saved an incomplete session record. Next AI will continue from here."

---

### Scenario 2: Pure Discussion (No Code Changes)

**If session was only discussion/planning**:

Still record it! Document:

- What was discussed
- Decisions made (even if not implemented yet)
- Questions answered
- Context clarified

**Example**:

```markdown
### Session X: YYYY-MM-DD (Planning Discussion)

**Duration**: 30 minutes
**AI Model**: Claude Sonnet 4.5
**User**: Stephen

### Objectives Completed ✅
- [x] Clarified questionnaire feature requirements
- [x] Discussed cost optimization strategies

### Files Created/Modified
None (discussion only)

### Key Discussions & Decisions
### 1. Questionnaire Auto-Completion Scope
**User Question**: "Agent 5 應該支援多少個功能？"
**Discussion**: Reviewed iCHEF product catalog, identified 22 features
**Decision**: Support all 22 features in prompt (not just top 5)
**Rationale**: Better user experience, minimal cost increase

### Next Session Preparation
**For Next AI**:
- Begin implementing Agent 5 with 22-feature support
- Use template in `poc-tests/poc6_questionnaire/agent5_prompts/v1.md`
```text

---

### Scenario 3: Bug Fix or Hot Fix

**Record all bug fixes** (even small ones):

```markdown
### Bug Fixes
1. **Whisper timeout on long audio**
   - Symptom: 60-min audio files failed with timeout
   - Root Cause: Fixed 5-min timeout in config
   - Fix: Increased to 10-min in `transcription-service/config.py:23`
   - Affected Files: `services/transcription-service/src/config.py`
   - Tested: Verified with 60-min test audio (passed)
```text

---

### Scenario 4: Reverted Changes

**Always document reversions**:

```markdown
### Reverted Changes
1. **Switched back from PostgreSQL to Firestore**
   - Original Change: Session 3 switched to PostgreSQL for POC
   - Reason for Revert: PostgreSQL migration too complex for timeline
   - Decision: Use Firestore, accept slower POC queries
   - User Quote: "時程比效能重要，先用 Firestore"
   - Reverted Files:
     - Deleted `services/database/postgres_client.py`
     - Restored `services/database/firestore_client.py`
   - Updated: plan.md (removed PostgreSQL references)
```text

---

## 📊 Recording Metrics

Track these metrics in each session entry:

### Time Metrics

- Session duration (hours)
- Time spent on each major task

### Work Metrics

- Files created (count)
- Files modified (count)
- Lines of code written
- Tests written (if applicable)

### Quality Metrics

- Objectives completed vs planned
- Open questions resolved
- Decisions made
- Risks identified

---

## 🎓 Training for New AI Assistants

### First Session Checklist

When a new AI assistant starts their first session:

1. [ ] Read `QUICK_START_FOR_AI.md` (5 min)
2. [ ] Read `DEVELOPMENT_LOG.md` (all sessions, 10-15 min)
3. [ ] Read `DEVELOPMENT_GUIDELINES.md` (this file, 5 min)
4. [ ] Read latest spec/plan files relevant to current work
5. [ ] Confirm understanding of recording requirements
6. [ ] Begin work
7. [ ] **Record session before ending** ⚠️ MANDATORY

---

## ✅ Recording Template Quick Access

### Full Template

See bottom of `DEVELOPMENT_LOG.md` for complete template.

### Quick Template (Copy & Paste)

```markdown
### Session X: YYYY-MM-DD (Title)

**Duration**: X hours
**AI Model**: [Model Name]
**User**: Stephen

### Objectives Completed ✅
- [ ] Objective 1
- [ ] Objective 2

### Files Created/Modified
**Created**:
- `path/to/file` (description)

**Modified**:
- `path/to/file` (changes made)

### Key Discussions & Decisions
### 1. Decision Topic
**User Request**: "..."
**Decision**: ...
**Rationale**: ...

### Technical Highlights
- Key implementation detail 1
- Key implementation detail 2

### Known Issues & Risks
1. **Issue**: Description
   - Mitigation: Solution

### Open Questions
1. **Question**: ...
   - Status: Pending/Resolved

### Next Session Preparation
**For Next AI Assistant**:
- Action item 1
- Action item 2
- Must read: [specific files]
- Blockers: [if any]
```text

---

## 🚨 Enforcement

### For AI Assistants

**At the end of EVERY session, you MUST**:

1. Ask yourself: "Have I recorded this session?"
2. If NO → Do not end session, record first
3. If YES → Verify using self-check checklist
4. Only then → Provide session summary to user

### For Users

**If an AI assistant tries to end session without recording**:

Say: "請先記錄這次 session 到 DEVELOPMENT_LOG.md，然後更新 session summary 給我。"

---

## 📝 Summary

### The Golden Rule

### "Every session MUST be recorded before it ends. No exceptions."

### The Three Must-Updates

Every session MUST update:

1. ✅ DEVELOPMENT_LOG.md (new session entry)
2. ✅ Session summary (message to user)
3. ✅ QUICK_START_FOR_AI.md (if critical changes)

### The Self-Check Question

**Before saying goodbye**: "Have I updated DEVELOPMENT_LOG.md and given user a session summary?"

- If YES → ✅ Good to go
- If NO → ❌ Do it now

---

### This guideline is effective immediately and applies to all development activities.

*Last Updated: 2025-01-29*
*Version: 1.0*
