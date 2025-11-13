# DEVOP2 Assessment 1

## Description

This project is based on the one I handed in for DatOp2-Assessment1. The goal of this extended version was to implement a **complete release management workflow** including **versioning, tagging, rolling releases, environment branches, hotfixes, and rollback strategies**.

Key highlights of the project:

* Initial release management using Git tags.
* Promotion of releases through `dev`, `staging`, and `main` (production) branches.
* Hotfix workflow for quickly addressing critical bugs.
* Semantic versioning for tracking patches, minor, and major changes.

---

# Full Git Release and Hotfix Guide

This markdown file summarizes all steps from initial release, tagging, environment merges, rollback, and hotfixes.

---

## 1️. Initial Release

```bash
# Make sure all changes are committed
git add .
git commit -m "Initial release v1.0.0"

# Create a tag for version 1.0.0
git tag -a v1.0.0 -m "Version 1.0.0"

# Push tag to GitHub
git push origin v1.0.0
```

### Visualize Tags

```bash
git tag        # list all tags
git show v1.0.0 # show commit for the tag
```

---

## 2️. Deploy Tag to Environment Branches

```bash
# Switch to dev branch
git checkout dev

# Merge or reset to the tag v1.0.0
git merge v1.0.0    # merges changes from tag into dev

# Push changes
git push origin dev
```

> Repeat similar steps for `staging` and `main` branches to promote the release.

---

## Rollback Example

### Making the ROllback

Here the Rollback was made in Production.

```bash
git reset --hard v1.0.0  # Give version name to go back
git push origin main --force
```

> Rollback is usually only needed for production (`main`). Dev can continue with ongoing changes.

---

### Create a Hotfix Branch

```bash
# Create hotfix branch from the buggy tag
git checkout -b hotfix/1.0.1 v1.0.1

# Apply bug fix
git add .
git commit -m "Fix critical bug in v1.0.1"
```

---

### Merge Hotfix into Environment Branches

Merge to Dev

```bash
git checkout dev
git merge hotfix/1.0.1
git push origin dev
```
---

Merge to Staging

```bash
git checkout staging
git merge hotfix/1.0.1
git push origin staging
```

---

Merge to Production (Main)

```bash
git checkout main
git merge hotfix/1.0.1
git push origin main
```

> Test hotfix in dev/staging before production deploy.

---

### Tag the Hotfix Release

```bash
# Create new tag for hotfix release
git tag -a v1.0.2 -m "v1.0.2 hotfix release"
git push origin v1.0.2
```

> Hotfixes should always get a new patch version, not reuse an old tag.

---

## Notes

* Dev branch is the main development integration branch.
* Use feature branches for multiple developers to avoid conflicts.
* Rollback is usually needed only for production.
* Always increment patch version for hotfixes (v1.0.1 → v1.0.2).



curl -k -u elastic:'VC5-ezWHTaquc9p5p6AF' -X POST \
"http://localhost:9200/bookride-logs/_doc?refresh=true" \
-H 'Content-Type: application/json' -d '{
  "service": "bookride-api",
  "level": "INFO",
  "@timestamp": "2025-11-12T10:45:00Z",
  "user_id": "U12345",
  "action": "Book Ride",
  "response_time_ms": 230,
  "status_code": 200,
  "message": "Ride successfully booked"
}'

curl http://localhost:9200/bookride-logs/_search?pretty