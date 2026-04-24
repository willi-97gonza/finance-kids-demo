# Contributing Guide

## Branch model
- `main`: stable branch for production-ready code.
- `develop`: integration branch.
- Feature branches: `feat/<short-name>`.
- Fix branches: `fix/<short-name>`.

## Local setup
1. Create virtual env: `python -m venv .venv`
2. Activate env:
   - PowerShell: `.venv\\Scripts\\Activate.ps1`
   - Bash: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` from `.env.example` and adjust values.
5. Run migrations: `python manage.py migrate`
6. Run tests: `python manage.py test`

## Definition of Done
- Code runs locally.
- Existing tests pass.
- Add or update tests when behavior changes.
- No secrets in commits.
- PR description includes context, changes, and test evidence.

## Pull request checklist
- [ ] I rebased with latest `develop`.
- [ ] I ran `python manage.py test`.
- [ ] I added/updated tests when needed.
- [ ] I updated docs if setup or behavior changed.
- [ ] I validated database-impacting changes.

## Database changes
- Use Django migrations for model changes.
- For manual SQL changes, document rollback steps in PR.
- Always backup before running destructive operations in shared environments.
