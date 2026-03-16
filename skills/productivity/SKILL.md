# Productivity Skill

Use this skill when the user wants a real productivity system, not just one-off motivation. It should cover goals, projects, tasks, habits, planning, reviews, overload triage, and situation-specific constraints in one coherent operating model.

## Architecture

Productivity lives in ~/productivity/. If ~/productivity/ does not exist yet, run setup.md.

```
~/productivity/
├── memory.md # Work style, constraints, energy, preferences
├── inbox/
│   ├── capture.md # Quick capture before sorting
│   └── triage.md # Triage rules and current intake
├── dashboard.md # High-level direction and current focus
├── goals/
│   ├── active.md # Outcome goals and milestones
│   └── someday.md # Goals not committed yet
├── projects/
│   ├── active.md # In-flight projects
│   └── waiting.md # Blocked or delegated projects
├── tasks/
│   ├── next-actions.md # Concrete next steps
│   ├── this-week.md # This week's commitments
│   ├── waiting.md # Waiting-for items
│   └── done.md # Completed items worth keeping
├── habits/
│   ├── active.md # Current habits and streak intent
│   └── friction.md # Things that break consistency
├── planning/
│   ├── daily.md # Daily focus and must-win
│   ├── weekly.md # Weekly plan and protected time
│   └── focus-blocks.md # Deep work and recovery blocks
├── reviews/
│   ├── weekly.md # Weekly reset
│   └── monthly.md # Monthly reflection and adjustments
├── commitments/
│   ├── promises.md # Commitments made to self or others
│   └── delegated.md # Handed-off work to track
├── focus/
│   ├── sessions.md # Deep work sessions and patterns
│   └── distractions.md # Repeating focus breakers
├── routines/
│   ├── morning.md # Startup routine and first-hour defaults
│   └── shutdown.md # End-of-day reset and carry-over logic
└── someday/
    └── ideas.md # Parked ideas and optional opportunities
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup and routine | setup.md |
| Memory structure | memory-template.md |
| Productivity system template | system-template.md |
| Cross-situation frameworks | frameworks.md |
| Common mistakes | traps.md |
| Student context | situations/student.md |
| Executive context | situations/executive.md |
| Freelancer context | situations/freelancer.md |
| Parent context | situations/parent.md |
| Creative context | situations/creative.md |
| Burnout context | situations/burnout.md |
| Entrepreneur context | situations/entrepreneur.md |
| ADHD context | situations/adhd.md |
| Remote work context | situations/remote.md |
| Manager context | situations/manager.md |
| Habit context | situations/habits.md |
| Guilt and recovery context | situations/guilt.md |

## What This Skill Sets Up

| Layer | Purpose | Default location |
|-------|---------|------------------|
| Capture | Catch loose inputs fast | ~/productivity/inbox/ |
| Direction | Goals and active bets | ~/productivity/dashboard.md + goals/ |
| Execution | Next actions and commitments | ~/productivity/tasks/ |
| Projects | Active and waiting project state | ~/productivity/projects/ |
| Habits | Repeated behaviors and friction | ~/productivity/habits/ |
| Planning | Daily, weekly, and focus planning | ~/productivity/planning/ |
| Reflection | Weekly and monthly reset | ~/productivity/reviews/ |
| Commitments | Promises and delegated follow-through | ~/productivity/commitments/ |
| Focus | Deep work protection and distraction logs | ~/productivity/focus/ |
| Routines | Startup and shutdown defaults | ~/productivity/routines/ |
| Parking lot | Non-committed ideas | ~/productivity/someday/ |
| Personal fit | Constraints, energy, preferences | ~/productivity/memory.md |

## Quick Queries

| User says | Action |
|-----------|--------|
| "Set up my productivity system" | Create the ~/productivity/ baseline and explain the folders |
| "What should I focus on?" | Check dashboard + tasks + commitments + focus, then surface top priorities |
| "Help me plan my week" | Use goals, projects, commitments, routines, and energy patterns to build a weekly plan |
| "I'm overwhelmed" | Triage commitments, cut scope, and reset next actions |
| "Turn this goal into a plan" | Convert goal → project → milestones → next actions |
| "Do a weekly review" | Update wins, blockers, carry-overs, and next-week focus |
| "Help me with habits" | Use habits/ to track what to keep, drop, or redesign |
| "Help me reset my routine" | Use routines/ and planning/ to simplify startup and shutdown loops |
| "Remember this preference" | Save it to ~/productivity/memory.md after explicit confirmation |

## Core Rules

### 1. Build One System, Not Five Competing Ones
- Prefer one trusted productivity structure over scattered notes, random task lists, and duplicated plans.
- Route goals, projects, tasks, habits, routines, focus, planning, and reviews into the right folder instead of inventing a fresh system each time.
- If the user already has a good system, adapt to it rather than replacing it for style reasons.

### 2. Start With the Real Bottleneck
- Diagnose whether the problem is priorities, overload, unclear next actions, bad estimates, weak boundaries, or low energy.
- Give the smallest useful intervention first.
- Do not prescribe a full life overhaul when the user really needs a clearer next step.

### 3. Separate Goals, Projects, and Tasks Deliberately
- Goals describe outcomes.
- Projects package the work needed to reach an outcome.
- Tasks are the next visible actions.
- Habits are repeated behaviors that support the system over time.
- Never leave a goal sitting as a vague wish without a concrete project or next action.

### 4. Adapt the System to Real Constraints
- Use the situation guides when the user's reality matters more than generic advice.
- Energy, childcare, deadlines, meetings, burnout, and ADHD constraints should shape the plan.
- A sustainable system beats an idealized one that collapses after two days.

### 5. Reviews Matter More Than Constant Replanning
- Weekly review is where the system regains trust.
- Clear stale tasks, rename vague items, and reconnect tasks to real priorities.
- If the user keeps replanning daily without progress, simplify and review instead.

### 6. Save Only Explicitly Approved Preferences
- Store work-style information only when the user explicitly asks you to save it or clearly approves.
- Before writing to ~/productivity/memory.md, ask for confirmation.
- Never infer long-term preferences from silence, patterns, or one-off comments.

## Common Traps
- Giving motivational talk when the problem is actually structural.
- Treating every task like equal priority.
- Mixing goals, projects, and tasks in the same vague list.
- Building a perfect system the user will never maintain.
- Recommending routines that ignore the user's real context.
- Preserving stale commitments because deleting them feels uncomfortable.

## Scope

This skill ONLY:
- builds or improves a local productivity operating system
- gives productivity advice and planning frameworks
- reads included reference files for context-specific guidance
- writes to ~/productivity/ only after explicit user approval

This skill NEVER:
- accesses calendar, email, contacts, or external services by itself
- monitors or tracks behavior in the background
- infers long-term preferences from observation alone
- writes files without explicit user confirmation
- makes network requests
- modifies its own SKILL.md or auxiliary files

## Security & Privacy

Data that leaves your machine:
- Nothing. This skill performs no network calls.

Data stored locally:
- Only the productivity files the user explicitly approves in ~/productivity/
- Work preferences, constraints, priorities, and planning artifacts the user chose to save

This skill does NOT:
- access internet or third-party services
- read calendar, email, contacts, or system data automatically
- run scripts or commands by itself
- monitor behavior in the background
- infer hidden preferences from passive observation
