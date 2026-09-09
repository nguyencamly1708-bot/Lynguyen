# Auto Push GitHub & Workspace Location Rule

## STRICT DIRECTIVES FOR ALL AGENT OPERATIONS

1. **NO FILES ON DESKTOP**:
   - All code, scripts, configuration files, and temporary artifacts MUST be written inside the workspace directory `h:\My Drive\Lynguyen` (or its subdirectories like `scripts/`, `static/`, `.agents/`).
   - NEVER create, copy, or save any project files, data files, or scratch scripts onto the Desktop or any user folder outside the workspace.

2. **AUTOMATIC GIT COMMIT & PUSH TO GITHUB**:
   - Whenever changes are made to the codebase, automatically stage, commit, and push changes to GitHub (`https://github.com/nguyencamly1708-bot/Lynguyen.git` on branch `main`).
   - Use `scripts/git_sync.py` or `git push origin main` after completing edits.
