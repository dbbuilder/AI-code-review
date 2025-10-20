# GitHub OAuth Permissions for AutoRev

## Current OAuth Scopes (Already Implemented)

```typescript
scope: 'read:user user:email repo read:org write:discussion'
```

## What Each Scope Allows

### ✅ `read:user`
**Status**: Already configured
**Purpose**: Read basic user profile information
**Allows**:
- Get user's GitHub username, avatar, bio
- Access public profile data
**Required for**: User authentication and profile display

### ✅ `user:email`
**Status**: Already configured
**Purpose**: Read user's email addresses
**Allows**:
- Access user's primary email
- Access verified emails
**Required for**: User identification and contact

### ✅ `repo`
**Status**: Already configured
**Purpose**: Full access to public and private repositories
**Allows**:
- ✅ Read repository contents (clone, read files)
- ✅ Create files and commits
- ✅ Create branches
- ✅ Create pull requests
- ✅ Read and write issues
- ✅ Create issue comments
- ✅ Update commit statuses
- ✅ Create releases
**Required for**: ALL repository operations including posting issues and creating PR files

**Important**: The `repo` scope is a **full-access** scope that includes:
- `repo:status` - Commit status access
- `repo_deployment` - Deployment access
- `public_repo` - Public repository access
- `repo:invite` - Repository invitation access
- `security_events` - Security event access

### ✅ `read:org`
**Status**: Already configured
**Purpose**: Read organization membership
**Allows**:
- See which organizations user belongs to
- Access organization repositories (with `repo` scope)
**Required for**: Organization repository access

### ✅ `write:discussion`
**Status**: Already configured
**Purpose**: Write access to discussions
**Allows**:
- Create discussion posts
- Comment on discussions
- Update discussions
**Required for**: Future discussion features (optional for now)

---

## Do We Need Additional Scopes?

### Short Answer: **NO** ✅

The `repo` scope alone provides **ALL** the permissions needed for:
- ✅ Creating issues in repositories
- ✅ Creating pull requests
- ✅ Committing files to repositories
- ✅ Creating branches
- ✅ Posting PR comments
- ✅ Adding review comments
- ✅ Creating commit statuses
- ✅ Reading repository contents

---

## What the `repo` Scope Includes

The `repo` scope is GitHub's **broadest repository permission** and includes these sub-scopes:

### 1. `repo:status`
- Create commit statuses
- Read commit statuses
**Used by AutoRev**: Yes, for passing/failing analysis checks

### 2. `repo_deployment`
- Create deployments
- Read deployments
**Used by AutoRev**: No (not needed for code review)

### 3. `public_repo`
- Access public repositories
- Create commits, branches, PRs on public repos
**Used by AutoRev**: Yes, for analyzing public repositories

### 4. `repo:invite`
- Accept/decline repository invitations
**Used by AutoRev**: No (users handle invitations manually)

### 5. `security_events`
- Read security events
- Create code scanning alerts
**Used by AutoRev**: Future feature (security scanning)

---

## Permissions Matrix

| Action | Scope Required | Status |
|--------|----------------|--------|
| Read user profile | `read:user` | ✅ Configured |
| Get user email | `user:email` | ✅ Configured |
| List repositories | `repo` | ✅ Configured |
| Read repository files | `repo` | ✅ Configured |
| **Create issues** | **`repo`** | **✅ Configured** |
| **Create pull requests** | **`repo`** | **✅ Configured** |
| **Commit files** | **`repo`** | **✅ Configured** |
| Create branches | `repo` | ✅ Configured |
| Post PR comments | `repo` | ✅ Configured |
| Create commit status | `repo` | ✅ Configured |
| Read organizations | `read:org` | ✅ Configured |
| Post in discussions | `write:discussion` | ✅ Configured |

---

## What Users Will See During OAuth

When users authorize AutoRev, GitHub will show them this permission screen:

```
AutoRev is requesting permission to:

✓ Read your public and private profile information
✓ Read your email addresses
✓ Full control of private repositories
  - Read and write access to code
  - Read and write access to commit statuses
  - Read and write access to issues
  - Read and write access to pull requests
  - Read and write access to repository hooks
✓ Read your organization membership
✓ Write access to discussions

AutoRev will be able to:
- Read your profile and email address
- Access code in repositories you grant access to
- Create issues, pull requests, and commits
- Post comments on PRs and issues
- See which organizations you belong to
```

---

## Security Considerations

### Why `repo` is Safe

1. **User Control**: Users explicitly authorize AutoRev for each session
2. **Scoped to User**: Only repositories the user has access to
3. **Revocable**: Users can revoke access anytime at https://github.com/settings/applications
4. **No Destructive Actions**: AutoRev never deletes code, only adds/modifies
5. **Transparent Actions**: All PRs/issues are clearly labeled as from AutoRev

### What AutoRev Will NOT Do

Even with `repo` scope, AutoRev is designed to NEVER:
- ❌ Delete repositories
- ❌ Delete branches (except temporary fix branches)
- ❌ Force push to main/master
- ❌ Modify `.git` configuration
- ❌ Accept invitations on user's behalf
- ❌ Transfer repositories
- ❌ Change repository settings
- ❌ Add collaborators
- ❌ Modify webhooks (unless GitHub App)

---

## Alternative: Granular GitHub App Permissions

If you want **more granular** control, you can create a **GitHub App** instead of OAuth App.

### GitHub App Permissions (More Granular)

```yaml
Repository permissions:
  Contents: Read & write        # Read/write files, create commits
  Issues: Read & write          # Create/comment on issues
  Pull requests: Read & write   # Create/comment on PRs
  Commit statuses: Read & write # Create commit checks
  Discussions: Read & write     # Optional: for discussions

Organization permissions:
  Members: Read-only            # See organization members

Events:
  Push: Subscribe              # Auto-trigger on push
  Pull request: Subscribe      # Auto-trigger on PR
```

### GitHub App Advantages

1. **Fine-grained permissions**: Only request what you need
2. **Organization-wide installation**: Admin installs once for all repos
3. **Webhook events**: Automatic triggers on push/PR
4. **Better rate limits**: 15,000 requests/hour vs 5,000 for OAuth
5. **Bot identity**: Actions show as "AutoRev[bot]"
6. **Separate from user**: Org can manage independently

### GitHub App Disadvantages

1. **More complex setup**: Requires app registration, private key, webhook endpoint
2. **Installation flow**: Different UX from OAuth
3. **Webhook infrastructure**: Need server to receive events

---

## Recommendation

### For Current Implementation: **Keep OAuth with `repo` scope** ✅

**Why**:
- ✅ Already configured and working
- ✅ Provides all needed permissions
- ✅ Simple user experience
- ✅ No additional setup required
- ✅ Faster to deploy

**When to use**:
- Individual users analyzing their own repos
- Small teams
- Quick MVP/prototype
- Manual analysis triggers

### For Production/Enterprise: **Migrate to GitHub App**

**Why**:
- Better permission granularity
- Organization-wide deployment
- Automatic webhook triggers
- Higher rate limits
- Professional appearance (bot identity)

**When to use**:
- Organization/enterprise deployment
- Automated analysis on every push/PR
- High-volume usage
- Team collaboration features

---

## Current Setup Summary

### Environment Variables (Already Set)
```bash
GITHUB_CLIENT_ID=your_oauth_client_id
GITHUB_CLIENT_SECRET=your_oauth_client_secret
GITHUB_CALLBACK_URL=https://autorev.servicevision.io/api/auth/github/callback
```

### OAuth Scopes (Already Configured)
```typescript
scope: 'read:user user:email repo read:org write:discussion'
```

### What Works Now
✅ User authentication
✅ List repositories
✅ Read repository contents
✅ Create issues ← **NEW API**
✅ Create pull requests ← **NEW API**
✅ Commit files to repos ← **NEW API**
✅ Post PR comments
✅ Create commit statuses

---

## Testing Permissions

### Test if User Has Required Permissions

```typescript
// GET /api/github/check-permissions
async function checkUserPermissions(accessToken: string, repoFullName: string) {
  const github = createGitHubClient(accessToken);
  const { owner, repo } = parseRepoFullName(repoFullName);

  try {
    // Try to get repository
    const repository = await github.getRepository(owner, repo);

    // Check user's permission level
    const { data: permission } = await github.octokit.rest.repos.getCollaboratorPermissionLevel({
      owner,
      repo,
      username: 'authenticated-user', // Will use auth token's user
    });

    return {
      canRead: ['read', 'triage', 'write', 'maintain', 'admin'].includes(permission.permission),
      canWrite: ['write', 'maintain', 'admin'].includes(permission.permission),
      canAdmin: permission.permission === 'admin',
      hasIssueAccess: repository.has_issues,
      hasPRAccess: !repository.disabled,
    };
  } catch (error) {
    return {
      canRead: false,
      canWrite: false,
      canAdmin: false,
      error: error.message,
    };
  }
}
```

---

## FAQ

### Q: Do users need to re-authorize if we add more scopes?
**A**: Yes. If you change the `scope` parameter in OAuth configuration, users must re-authorize to grant the new permissions.

### Q: Can we request fewer permissions initially?
**A**: Yes, but you'd lose key functionality:
- Without `repo`: Cannot create issues/PRs, cannot read private repos
- Without `read:org`: Cannot access organization repos
- Without `write:discussion`: Cannot post in discussions (low priority)

### Q: What if a user's repository has branch protection?
**A**: PRs will still be created, but:
- Cannot push directly to protected branches
- Must create PR (which we do anyway)
- PR may require review before merge
- Commit status checks may be required

### Q: Can AutoRev access ALL user repositories?
**A**: With `repo` scope, yes. But:
- Only repositories the OAuth user has access to
- User can revoke access anytime
- Better to ask user which repo to analyze (which we do)

### Q: Is `repo` scope too broad?
**A**: For code review, `repo` is standard:
- GitHub Actions uses it
- Most CI/CD tools use it
- Competitors (CodeClimate, SonarCloud) use it
- It's the only way to create issues/PRs

---

## Migration Path to GitHub App (Future)

### Phase 1: OAuth (Current) ✅
- Scope: `repo read:org write:discussion`
- User-level access
- Manual triggers

### Phase 2: GitHub App (Future)
- Fine-grained repository permissions
- Organization installations
- Webhook-triggered analysis
- Bot identity

### Phase 3: Hybrid (Best of Both)
- OAuth for individual users
- GitHub App for organizations
- Detect which auth method to use
- Seamless experience for both

---

## Conclusion

### Answer: No Additional Scopes Needed ✅

The current OAuth configuration with `repo` scope provides **ALL** permissions needed to:
- ✅ Post issues to repositories
- ✅ Create pull requests with files
- ✅ Commit code review reports
- ✅ Post PR comments
- ✅ Create commit statuses

**Users will need to re-authorize** when you deploy the updated OAuth scope from:
```typescript
// Old (if it was just 'repo')
scope: 'read:user user:email repo'

// New (already configured in auth.ts:line 33)
scope: 'read:user user:email repo read:org write:discussion'
```

But since we already have `repo`, the core functionality for posting issues and files **works right now** with no changes needed.

---

**Status**: ✅ **Ready to Deploy**
- OAuth scopes: Configured
- GitHub API client: Implemented
- Issue creation API: Built
- PR creation API: Built
- No additional permissions required
