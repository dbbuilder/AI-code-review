# GitHub Integration Strategy for AutoRev

## Current Implementation vs. Enhanced Integration

### Current Setup (Basic OAuth)
- User authentication only
- Access to basic profile information
- List repositories (read-only)
- **Limitation**: Cannot access repository content, create PRs, post comments, or trigger webhooks

### Enhanced Integration Goals
1. **Read repository contents** - Clone/analyze code directly
2. **Create pull requests** - Submit automated fixes
3. **Post review comments** - Inline code suggestions
4. **Webhook integration** - Auto-trigger analysis on push/PR
5. **Commit status checks** - Show analysis results in GitHub UI
6. **Installation-based access** - Organization-wide deployment

---

## Two Paths Forward

### Option 1: Enhanced OAuth App (Easier, Faster)
**Pros**:
- Use existing OAuth infrastructure
- Quick to implement (add scopes)
- User-level permissions
- No app installation required

**Cons**:
- Limited to user's personal access
- Cannot post as "AutoRev bot"
- No webhook events
- User must re-authorize

**Best for**: MVP, individual users, quick deployment

### Option 2: GitHub App (Recommended, Production)
**Pros**:
- Organization-wide installation
- Fine-grained repository permissions
- Webhook events (push, PR, comments)
- Commit status checks
- Posts as "AutoRev[bot]"
- Better security (short-lived tokens)
- Organization admins can manage

**Cons**:
- More complex setup
- Requires app registration
- Installation flow different

**Best for**: Production, enterprise, team collaboration

---

## Recommended Approach: Hybrid Strategy

### Phase 1: Enhanced OAuth (Immediate - 1-2 hours)
Upgrade existing OAuth to request additional scopes:
- `repo` - Full repository access (read/write)
- `read:org` - Organization membership
- `write:discussion` - Post comments/reviews

### Phase 2: GitHub App (Production - 4-6 hours)
Convert to GitHub App for:
- Webhook-triggered analysis
- Automated PR comments
- Commit status checks
- Organization installations

---

## Implementation Plan

### Phase 1: Enhanced OAuth Scopes

#### 1.1 Update OAuth Scope Request
**File**: `/site/app/api/auth/github/route.ts`

```typescript
// Current (basic):
scope: 'read:user user:email'

// Enhanced:
scope: 'read:user user:email repo read:org write:discussion'
```

**Scopes Explained**:
- `repo` - Full repository access (clone, read files, create PRs)
- `read:org` - See which organizations user belongs to
- `write:discussion` - Post comments on PRs and issues

#### 1.2 Store Access Token Securely
**File**: `/site/lib/auth.ts`

Add encrypted token storage:
```typescript
interface GitHubSession {
  user: GitHubUser;
  accessToken: string;      // Encrypted
  tokenExpiry: number;
  scope: string;
  refreshToken?: string;
}
```

#### 1.3 Create GitHub API Client
**File**: `/site/lib/github-client.ts`

```typescript
class GitHubClient {
  // Repository content access
  async getFileContent(repo: string, path: string, ref?: string)
  async getTree(repo: string, ref: string)
  async cloneRepository(repo: string, ref: string)

  // Pull request operations
  async createPullRequest(repo: string, title: string, body: string, head: string, base: string)
  async createReview(repo: string, prNumber: number, comments: ReviewComment[])
  async createReviewComment(repo: string, prNumber: number, body: string, path: string, line: number)

  // Commit operations
  async createCommit(repo: string, message: string, tree: string, parents: string[])
  async createBranch(repo: string, branch: string, sha: string)

  // Status checks
  async createCommitStatus(repo: string, sha: string, state: 'pending' | 'success' | 'failure', context: string)
}
```

#### 1.4 Update Repository List API
**File**: `/site/app/api/repositories/route.ts`

Add filtering and permissions:
```typescript
// Return repositories with analysis permissions
const repos = await octokit.repos.listForAuthenticatedUser({
  visibility: 'all',
  affiliation: 'owner,collaborator,organization_member',
  sort: 'updated',
  per_page: 100
});

// Filter to repos where user has write access
return repos.data.filter(repo => repo.permissions?.push === true);
```

---

### Phase 2: GitHub App Setup

#### 2.1 Create GitHub App
**GitHub Settings** → **Developer settings** → **GitHub Apps** → **New GitHub App**

**App Configuration**:
```yaml
Name: AutoRev Code Review
Homepage URL: https://autorev.servicevision.io
Callback URL: https://autorev.servicevision.io/api/auth/github/app/callback
Webhook URL: https://autorev.servicevision.io/api/webhooks/github
Webhook Secret: [generate secure secret]

Permissions:
  Repository permissions:
    - Contents: Read & write
    - Pull requests: Read & write
    - Commit statuses: Read & write
    - Webhooks: Read & write
    - Issues: Read & write

  Organization permissions:
    - Members: Read-only

Events (Subscribe to):
  - Push
  - Pull request
  - Pull request review
  - Pull request review comment
  - Repository
```

#### 2.2 Implement Installation Flow
**File**: `/site/app/api/auth/github/app/install/route.ts`

```typescript
export async function GET() {
  const installUrl = `https://github.com/apps/autorev-code-review/installations/new`;
  return NextResponse.redirect(installUrl);
}
```

**File**: `/site/app/api/auth/github/app/callback/route.ts`

```typescript
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const installationId = searchParams.get('installation_id');
  const setupAction = searchParams.get('setup_action');

  if (setupAction === 'install') {
    // Store installation ID
    // Associate with user account
    // Enable webhook processing
  }

  return NextResponse.redirect('/dashboard?installed=true');
}
```

#### 2.3 Implement Webhook Handler
**File**: `/site/app/api/webhooks/github/route.ts`

```typescript
import { Webhooks } from '@octokit/webhooks';

const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET!
});

webhooks.on('push', async ({ payload }) => {
  // Trigger analysis on push
  const { repository, ref, commits } = payload;

  // Queue analysis job
  await queueAnalysis({
    repoFullName: repository.full_name,
    ref: ref,
    installationId: payload.installation?.id
  });
});

webhooks.on('pull_request.opened', async ({ payload }) => {
  // Trigger analysis on PR open
  const { pull_request, repository } = payload;

  await queuePullRequestAnalysis({
    repoFullName: repository.full_name,
    prNumber: pull_request.number,
    headSha: pull_request.head.sha,
    installationId: payload.installation?.id
  });
});

export async function POST(request: Request) {
  const body = await request.text();
  const signature = request.headers.get('x-hub-signature-256')!;
  const id = request.headers.get('x-github-delivery')!;

  await webhooks.verifyAndReceive({
    id,
    name: request.headers.get('x-github-event') as any,
    signature,
    payload: body
  });

  return new Response('OK', { status: 200 });
}
```

#### 2.4 Generate Installation Access Tokens
**File**: `/site/lib/github-app.ts`

```typescript
import { App } from '@octokit/app';

const app = new App({
  appId: process.env.GITHUB_APP_ID!,
  privateKey: process.env.GITHUB_APP_PRIVATE_KEY!,
  webhooks: {
    secret: process.env.GITHUB_WEBHOOK_SECRET!
  }
});

export async function getInstallationOctokit(installationId: number) {
  const octokit = await app.getInstallationOctokit(installationId);
  return octokit;
}

export async function getRepositoryContent(
  installationId: number,
  owner: string,
  repo: string,
  path: string,
  ref?: string
) {
  const octokit = await getInstallationOctokit(installationId);
  const { data } = await octokit.rest.repos.getContent({
    owner,
    repo,
    path,
    ref
  });
  return data;
}
```

---

## Integration Features to Implement

### 1. Repository Content Access
**Purpose**: Clone and analyze repository code

```typescript
// Clone repository to temporary directory
async function cloneRepository(repoUrl: string, ref: string) {
  const tempDir = `/tmp/autorev-${Date.now()}`;
  await execAsync(`git clone --depth 1 --branch ${ref} ${repoUrl} ${tempDir}`);
  return tempDir;
}

// Or use GitHub API for file-by-file access
async function getRepositoryFiles(installationId: number, repo: string, ref: string) {
  const octokit = await getInstallationOctokit(installationId);
  const { data: tree } = await octokit.rest.git.getTree({
    owner: repo.split('/')[0],
    repo: repo.split('/')[1],
    tree_sha: ref,
    recursive: 'true'
  });
  return tree.tree;
}
```

### 2. Automated Pull Requests
**Purpose**: Submit code fixes as PRs

```typescript
async function createFixPullRequest(
  installationId: number,
  repo: string,
  baseBranch: string,
  fixes: CodeFix[]
) {
  const octokit = await getInstallationOctokit(installationId);
  const [owner, repoName] = repo.split('/');

  // Create branch
  const branchName = `autorev-fixes-${Date.now()}`;
  const { data: ref } = await octokit.rest.git.getRef({
    owner,
    repo: repoName,
    ref: `heads/${baseBranch}`
  });

  await octokit.rest.git.createRef({
    owner,
    repo: repoName,
    ref: `refs/heads/${branchName}`,
    sha: ref.object.sha
  });

  // Commit changes
  for (const fix of fixes) {
    await octokit.rest.repos.createOrUpdateFileContents({
      owner,
      repo: repoName,
      path: fix.path,
      message: fix.message,
      content: Buffer.from(fix.content).toString('base64'),
      branch: branchName
    });
  }

  // Create PR
  const { data: pr } = await octokit.rest.pulls.create({
    owner,
    repo: repoName,
    title: 'AutoRev: Automated code quality improvements',
    head: branchName,
    base: baseBranch,
    body: generatePRBody(fixes)
  });

  return pr;
}
```

### 3. Inline PR Comments
**Purpose**: Suggest changes directly on code

```typescript
async function postReviewComments(
  installationId: number,
  repo: string,
  prNumber: number,
  findings: Finding[]
) {
  const octokit = await getInstallationOctokit(installationId);
  const [owner, repoName] = repo.split('/');

  const comments = findings.map(finding => ({
    path: finding.file,
    position: finding.line,
    body: `**${finding.severity}**: ${finding.message}\n\n${finding.recommendation}`
  }));

  await octokit.rest.pulls.createReview({
    owner,
    repo: repoName,
    pull_number: prNumber,
    event: 'COMMENT',
    comments
  });
}
```

### 4. Commit Status Checks
**Purpose**: Show pass/fail in GitHub UI

```typescript
async function updateCommitStatus(
  installationId: number,
  repo: string,
  sha: string,
  analysisResult: AnalysisResult
) {
  const octokit = await getInstallationOctokit(installationId);
  const [owner, repoName] = repo.split('/');

  const state = analysisResult.criticalIssues > 0 ? 'failure' : 'success';
  const description = `Found ${analysisResult.totalIssues} issues (${analysisResult.criticalIssues} critical)`;

  await octokit.rest.repos.createCommitStatus({
    owner,
    repo: repoName,
    sha,
    state,
    target_url: `https://autorev.servicevision.io/results/${analysisResult.id}`,
    description,
    context: 'AutoRev Code Review'
  });
}
```

### 5. Webhook-Triggered Analysis
**Purpose**: Auto-analyze on push/PR

```typescript
// Queue system for background processing
interface AnalysisJob {
  id: string;
  repoFullName: string;
  ref: string;
  sha: string;
  installationId: number;
  trigger: 'push' | 'pull_request' | 'manual';
  status: 'queued' | 'processing' | 'completed' | 'failed';
}

async function queueAnalysis(job: Omit<AnalysisJob, 'id' | 'status'>) {
  const jobId = generateId();

  // Store in database
  await db.analysisJobs.create({
    id: jobId,
    ...job,
    status: 'queued',
    createdAt: new Date()
  });

  // Trigger background worker
  await triggerWorker(jobId);

  return jobId;
}
```

---

## Database Schema Updates

### User Sessions with Tokens
```sql
CREATE TABLE user_sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  access_token_encrypted TEXT NOT NULL,
  refresh_token_encrypted TEXT,
  token_expiry TIMESTAMP NOT NULL,
  scope TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  last_used_at TIMESTAMP
);
```

### GitHub Installations
```sql
CREATE TABLE github_installations (
  id UUID PRIMARY KEY,
  installation_id BIGINT UNIQUE NOT NULL,
  account_login TEXT NOT NULL,
  account_type TEXT NOT NULL, -- 'User' or 'Organization'
  repositories TEXT[], -- Array of repo IDs with access
  permissions JSONB,
  installed_by UUID REFERENCES users(id),
  installed_at TIMESTAMP DEFAULT NOW(),
  suspended_at TIMESTAMP
);
```

### Analysis Jobs
```sql
CREATE TABLE analysis_jobs (
  id UUID PRIMARY KEY,
  repo_full_name TEXT NOT NULL,
  ref TEXT NOT NULL,
  sha TEXT NOT NULL,
  installation_id UUID REFERENCES github_installations(id),
  trigger TEXT NOT NULL, -- 'push', 'pull_request', 'manual'
  status TEXT NOT NULL,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  result_id UUID REFERENCES analysis_results(id),
  error TEXT
);
```

---

## Environment Variables Required

### OAuth App (Current)
```bash
GITHUB_CLIENT_ID=your_oauth_client_id
GITHUB_CLIENT_SECRET=your_oauth_client_secret
GITHUB_CALLBACK_URL=https://autorev.servicevision.io/api/auth/github/callback
```

### GitHub App (New)
```bash
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_APP_CLIENT_ID=your_app_client_id
GITHUB_APP_CLIENT_SECRET=your_app_client_secret
```

### Encryption
```bash
ENCRYPTION_KEY=your_32_byte_encryption_key_for_tokens
```

---

## NPM Packages to Install

```bash
npm install @octokit/app @octokit/webhooks @octokit/rest
npm install @octokit/auth-app @octokit/plugin-rest-endpoint-methods
npm install crypto-js  # For token encryption
```

---

## Migration Path

### Week 1: Enhanced OAuth
- ✅ Update OAuth scopes
- ✅ Add token storage
- ✅ Create GitHub API client
- ✅ Implement repository cloning
- ✅ Enable manual PR creation

### Week 2: GitHub App Foundation
- Register GitHub App
- Implement installation flow
- Set up webhook endpoint
- Store installation data
- Generate installation tokens

### Week 3: Automation Features
- Webhook-triggered analysis
- Automated PR comments
- Commit status checks
- Background job processing

### Week 4: Polish & Testing
- Error handling
- Rate limiting
- Retry logic
- End-to-end testing
- Documentation

---

## Security Considerations

### Token Storage
- Encrypt access tokens at rest
- Use environment-specific encryption keys
- Rotate encryption keys regularly
- Never log tokens

### Webhook Security
- Verify webhook signatures
- Use HTTPS only
- Validate payload structure
- Rate limit webhook endpoint

### API Rate Limits
- GitHub OAuth: 5,000 requests/hour
- GitHub App: 15,000 requests/hour per installation
- Implement caching
- Use conditional requests (ETags)

### Permission Scoping
- Request minimum required permissions
- Explain why each permission is needed
- Allow users to revoke access easily

---

## User Experience Flow

### Enhanced OAuth Flow
1. User clicks "Sign in with GitHub"
2. GitHub shows permission request (now includes `repo` scope)
3. User authorizes
4. AutoRev stores encrypted token
5. User can now analyze private repos and create PRs

### GitHub App Installation Flow
1. Organization admin clicks "Install AutoRev"
2. GitHub shows App installation page
3. Admin selects repositories to enable
4. AutoRev receives installation webhook
5. AutoRev enables auto-analysis for selected repos
6. Push events trigger automatic code reviews

---

## Next Steps

### Immediate (Today)
1. Update OAuth scopes in existing implementation
2. Add token encryption and storage
3. Create GitHub API client wrapper
4. Test repository content access

### Short-term (This Week)
1. Register GitHub App
2. Implement installation flow
3. Set up webhook endpoint
4. Test webhook events

### Medium-term (Next 2 Weeks)
1. Implement automated PR creation
2. Add commit status checks
3. Create background job queue
4. Deploy webhook infrastructure

---

## Success Metrics

### Phase 1 (Enhanced OAuth)
- ✅ Users can analyze private repositories
- ✅ Users can manually create fix PRs
- ✅ API calls succeed with proper authentication

### Phase 2 (GitHub App)
- ✅ Organizations can install AutoRev
- ✅ Push events trigger automatic analysis
- ✅ PRs receive automated review comments
- ✅ Commit statuses appear in GitHub UI

---

**Recommendation**: Start with Phase 1 (Enhanced OAuth) immediately to enable repository content access, then plan Phase 2 (GitHub App) for production deployment with webhooks and automation.
