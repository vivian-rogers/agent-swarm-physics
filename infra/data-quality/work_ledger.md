# DQ4: work-output ledger

**What the swarm actually produced**, read from the public git histories of the agents' repos rather than from
activity or narration. Built 2026-10-04 by `infra/shared/work_ledger.py`. Outputs are in `data/processed/shared/`
(about 14 MB). Raw clones are in `data/raw/repos/<host>/<path>.git` (1.47 GB; fetch record in
`data/raw/repos/_source.md`).

It answers the outcome-measure gaps behind H15 (viability choice), H33 (write turns ≠ value; GitLab API writes
missed), H11/H31 (project labels measure attention, not work) and H01 round 2 (artifact advancement as viability).

## Build

```
uv run python infra/shared/work_ledger.py            # offline: extract + build + validate (~10 s with a warm cache; ~6 min cold)
uv run python infra/shared/work_ledger.py refresh    # network: inventory + fetch + upgrade, then the offline stages
uv run python infra/shared/work_ledger.py <stage>    # inventory | fetch | upgrade | extract | build | validate
```

- **inventory** (no network): the repo list, from the artifacts tables (tiers below).
- **fetch**: read-only, unauthenticated `git ls-remote` and `git clone --bare` (git runs with global and system config
  disabled, an empty credential helper and no prompts).
  - **Size guard:** a full clone (blobs) up to 60 MB; otherwise blobless (`--filter=blob:none`), then commits-only
    (`--filter=tree:0`), then skipped. Total cap 1.9 GB.
  - **Resumable:** it never re-clones a repo already attempted. With no scratch log, it seeds one from
    `work_repos.parquet`.
- **upgrade**: re-clones in full the small repos that the cap guard sent straight to blobless.
- **extract**: one `git log --all --source` per clone, into a scratch cache (`$DQ4_SCRATCH`, default
  `<tmpdir>/dq4_work_ledger`).
  - The cache holds author e-mails and file paths and is **never written under `data/`**.
  - Commit messages are read only to derive length and flags.
- **build / validate**: the tables below, plus `work_ledger_validation.json`.

Threads: polars ≤ 2; git `pack.threads=1`, `index.threads=1`; `git log` runs niced.

## Repo inventory (`work_repos.parquet`, 1,281 rows)

| tier | rule | inventoried | cloned |
| --- | --- | --- | --- |
| `org` | `github.com/ai-village-agents/*`, `gitlab.com/ai-village-agents/**` (`gitlab.com/village/<p>` refs read as the agents' group) | 1,096 | 589 |
| `agent_account` | owner is an agent's own account: the owner name contains a roster name, or `o3-ux` | 74 | 19 |
| `other_write` | any other repo with a git-printed push remote, or ≥ 3 strict write mentions (push/commit/PR/MR/repo create/deploy with `how ∈ {url, output, bare}`) | 27 (+84 weak, not attempted) | 25 |

**Fetch outcomes:**
- **Modes:** 581 full, 51 blobless, 1 commits-only.
- **Not cloned (564):** anonymous access refused (private, deleted or misspelled names) or empty.
  - These hold 1.6% of strict write mentions (1,090 vs 65,616 in cloned repos).
  - The biggest are GitLab projects that are evidently private: `surprise-lab-tools` (335), `combinatorial-zoo-pages` (181), `relationship-goal-tracker`, `deployment-files`, `harbor-table-food-rescue`.
  - The whole `gemini-25-pro-collab` account is gone.
- **Columns:**
  - inventory evidence: `n_write_strict`, `n_push_output`, `n_action`, …;
  - fetch: `exists`, `mode`, `bytes`, `default_ref`, `head_sha`, `attempts`, `fetched_at`;
  - history: `n_commits`, `n_commits_agent_work`, `n_commits_automated`, `first_commit_t`, `last_commit_t`;
  - `has_site`: a pages branch, or a site artifact whose parent is the repo (344 repos).

## Tables

### `work_commits.parquet` (376,098 rows; one per repo × commit; 341,562 distinct hashes)

**Keys and time:**
- `repo`, `tier`, `host`, `hash`.
- **`t` = author time (UTC)** and `t_commit`. `pt_date`, `goal_no`, `regime`, `holdout` (`holdout_mask`), `calendar_day`, `in_window` (inside that day's empirical active window ± 15 min).

**Identity:**
- **`author_agent`** (roster code), **`author_kind`** ∈ {agent, human, bot, unknown}, and `author_attr`, the mapping route:
  - `email_agentvillage` (`<slug>@agentvillage.org`; the slug matches exactly or as a unique prefix of a roster name, e.g. `claude-3.7@` → Claude 3.7 Sonnet);
  - `noreply_account` (GitHub/GitLab noreply address of an agent account);
  - `name`;
  - `email_local`;
  - `out_hash` (an unknown identity whose hash an agent's command printed);
  - `agentvillage_unmapped` (village-domain identities not on the roster: the `swarm-*` agents of `gitlab.com/ai-village-agents/swarm/earth`).
- "human" means any non-village identity, including outside AI agents (e.g. Terminator2). Non-agents carry only a 10-character `author_id` hash; no names or e-mails are stored.
- `committer_kind` adds `web` (GitHub/GitLab web merges and edits).

**Shape:**
- `n_parents`, `is_merge`, `branch` (from `--source`), `on_default`, `pages_branch` (gh-pages/pages).
- `n_files`, `insertions`, `deletions`, `n_binary`, `lines_web` / `lines_code` / `lines_doc` / `lines_data` (by file extension).
- `bulk`: > 200 files or > 20k lines.

**Message (derived only):** `msg_len`, `is_revert`, `merge_msg` (PR/MR merge text), `deploy_msg`, `n_coauthors`.

**Work vs automation:**
- **`turn_gap_s`**: seconds to the author agent's nearest logged turn (`actions` ∪ agent events; the Claude Code agent's SDK sessions count as continuous).
- **`turn_backed`**: `turn_gap_s` ≤ 300 s.
- **`clockwork`**: one identity, repo and day, with ≥ 20 commits over ≥ 20 min and more commits than half the author's own turns in that span.
- **`automated`** = agent-authored and (not turn-backed, or clockwork). It catches cron, CI and monitor scripts that commit under an agent's identity. Examples:
  - 81.6k commits to `surprise-lab-mirror-proofs` under GPT-5's identity, still running on 2026-10-04;
  - Claude 3.7 Sonnet's news monitor (3.9k commits in 4 h);
  - Gemini 3.1 Pro's dashboards.

**Dedupe:**
- **`canonical`**: one row per hash, in the repo first seen in the record (forks and GitHub→GitLab mirrors share hashes). `n_repos` counts the repos holding the hash.
- **`imported`**: before 2025-04-01, or a non-agent commit older than the repo's first mention minus 1 day (forked or template history).

**Cross-check:** `in_out_hashes`, `out_hash_agent`, `out_hash_t` (first agent command that printed the hash).

**`fetch_mode`:** full | blobless (no line stats) | commits_only (no files either).

**Default filter for "agent work":** `canonical & ~imported & author_kind == "agent" & ~automated`. This gives 80,138
commits by 36 agents in 574 repos, first 2025-10-06 (regime I 2,953; II 2,377; III 74,808). A further 112,079
agent-identity commits are flagged automated.

### `work_daily.parquet` (9,474 rows: 4,731 agent-days + 4,743 repo-days)

**Keys:**
- `level` ∈ {agent, repo}, `pt_date`, `agent` | `repo` (+ `tier`), `goal_no`, `regime`, **`holdout`**, `calendar_day`.
- **`active`** (agent level: the agent had any event or action that day). Every active agent-day is present, with zeros, so a missing row is not a zero; 2,276 of 4,485 active agent-days have work commits.

**Git (agent work commits only):**
- `commits`, `lines_changed`, `lines_changed_nobulk`, `insertions`, `deletions`, `lines_code` / `web` / `doc` / `data`;
- `merges`, `pr_merge_commits`, `reverts`, `bulk_commits`;
- `distinct_files`, `repos_touched` (agent level), `n_agents` (repo level);
- **`new_repos`** (root commit authored that day; root commits before 2025-04 don't count);
- `commits_no_linestats`; `in_window_frac`.

**Automation and others:** `commits_automated`; repo level adds `commits_other` (non-agent), `commits_bot`, `bot_pages_commits`.

**Deploy / publish:**
- `pages_commits`: commits on gh-pages/pages branches;
- `site_default_commits`: commits on the default branch of a repo with a site; GitLab Pages and Actions-built sites deploy on such pushes;
- `deploy_msg_commits`;
- `deploy_cmds`: wrangler / vercel / netlify / firebase / surge / gh-pages / `npm run deploy` / flyctl / heroku turns;
- `release_cmds`, `repo_create_cmds`, `pr_mr_create_cmds`, `pr_mr_merge_cmds`.

**Raw command counts (agent level):** `cmd_push`, `cmd_push_printed` (push that printed a range), `cmd_commit`. These are turns, not calls; they are comparable to H15/H33 write turns.

**API writes:**
- `api_writes_gitlab`, `api_writes_github`, `api_write_turns`;
- by category: `api_content_writes` (files/commits endpoints), `api_mr_pr_writes`, `api_issue_comment_writes`, `api_settings_writes`, `api_other_writes`.
- **Don't add `api_content_writes` to `commits`:** 85% of resolved content writes left a commit by the same agent in the same repo within 10 minutes, so they are already in the git history.

### `work_api_writes.parquet` (11,324 rows: one per non-GET API call)

- **Source:** recovered from `artifact_commands_text`: `glab api`, `gh api`, and curl to `gitlab.com/api/v4` or `api.github.com`.
- **Method:** explicit `-X` / `--method`. Otherwise, with fields or data it's a POST (glab/gh semantics).
- **Columns:** `row` (sidecar row), `call`, `t`, `agent`, `error`, `tool`, `host`, `method`, `category`, `project_ref`, `repo`, `repo_how`, time keys.
- **GitLab:** 10,259 calls, all in #50–#51.
- **Repo resolution:** 55% of GitLab calls resolved to a repo:
  - `path` (path-form project);
  - `var_path` (a variable plus a single path in the same command);
  - `id_cooccur` (numeric id voted from commands that also name a path);
  - `id_filepaths` (files written through the API matched to the fetched histories).
- **Limits:** the sidecar keeps ≤ 300 characters of relevant lines, so loops count once and some calls are cut off.

### `work_outcomes.parquet` (183 rows; descriptive)

Columns: `goal_no`, `agent` (null = swarm level), `outcome`, `value`, `unit`, `source`, `reliability` (`artifact` = git
history; `link` = a public URL agents posted or opened), `holdout`, `note`.

| goal | outcome | reliability | notes |
| --- | --- | --- | --- |
| every period | `agent_commits`, `committing_agents`, `repos_committed_to` | artifact | agent work commits |
| #17, #19, #25, #28, #39 (site goals) | `repos_created`, `site_repos_created` | artifact | root commits in the period. Sparse before #30 (#17: one agent): early sites were not in public git |
| #42 YouTube | `youtube_videos_first_linked`, `…_chat`, `youtube_videos_studio`, `youtube_videos_new_total` | link | the first agent to link a new video id. `_studio`: ids in YouTube Studio URLs the agent opened (owner only; 3 agents). **Ownership unverified**: agents also link other channels' videos (one agent first-linked 48 in a 1–10 video goal) |
| #20 Substack | `substack_posts_linked`, `substack_posts_total` | link | post URLs first seen in #20, credited to the agent that first linked the subdomain |
| #23 chess | `lichess_games_linked`, `lichess_games_total` | link | games linked (played), not results |

**Skipped as not reliably extractable:**
- **Money raised (#1, #38):** only narration and operator chat. Fundraiser pages were not fetched.
- **Games completed (#10)** and **Juice Shop challenges (#27):** narration only; local scoreboards were not logged.
- **Live-site checks:** no web hosts were contacted.

## Validation (`work_ledger_validation.json`)

Per-period numbers use non-holdout days only; held-out days are pooled.

**Commits printed in agents' commands vs. the fetched histories** (`out_hashes`):

| comparison | n | result |
| --- | --- | --- |
| all printed hashes found | 81,805 | 92.4% |
| … in repos that were fetched | 67,046 | 95.3% |
| … in repos not publicly readable | 696 | 6% |
| … with no remote printed | 14,055 | 83% |
| `git commit` output, found | 60,209 | 91.6% |
| push range heads, found | 8,874 | 95.0% |
| GitHub era (before 2026-06-29), found | 35,126 | 88.1% |
| GitLab era (from 2026-06-29), found | 46,679 | 95.6% |
| time agreement on matched `git commit` outputs (author time) | 8,783 | median \|Δt\| 0 s; 99.8% within 5 min |
| agent agreement: e-mail-mapped author = the command's agent (`git commit`) | 8,780 | 99.6% |
| agent agreement: author = pusher | 54,807 | 95.9% (agents sometimes push teammates' commits) |

Reading the misses:
- The 4.7% missing in fetched repos are local commits that were never pushed or were rewritten away (amend, rebase, force-push).
- The reverse floor: 78.6% of work commits were printed by some agent command, vs 1.3% of automated ones. This is independent support for the automation flag.

**Coverage by period** (share of agent-days with a git write command that also have ledger commits):
- **#30–#44:** 0.87–1.0.
- **#51** (non-holdout days): 0.97, with 48k work commits, 87k automated and 9.0k API writes.
- **#16–#27:** git was rare. Shares are 0.2–1.0 on 0–22 days, a handful of commits per period; the misses are unpushed local commits and the deleted `gemini-25-pro-collab` account.
- **Before #16:** essentially no git use (one git-command agent-day, in #8).

**The ledger is a dense outcome measure from #30 (2026-02-09) on.** Before that, a zero is ambiguous.

## Known gaps and pitfalls

1. **Private or deleted repos** (564 attempted, mostly misspelled names). Real but private GitLab projects carry 1.6% of write mentions.
2. **Line stats** exist for 56% of work commits. Large GitLab #51 repos are blobless. Use `commits` and `distinct_files` as primary size measures; use lines only where `commits_no_linestats == 0`.
3. **Automation flag** is a heuristic. Thresholds are in the module header (`TURN_GAP_S`, `CLOCKWORK_*`). Report work and automated counts separately; never sum them blindly.
4. **Commits ≠ value.** Repeated small commits and API "receipt" commits (e.g. one chapter file per commit) inflate counts. `distinct_files`, `new_repos`, `site_default_commits` and outcomes are complementary.
5. **Author time can predate the push.** Use `t_commit` or `out_hash_t` for when work became visible.
6. **The Claude Code agent** has 406 work commits that the command sidecar can't see (its stream isn't scanned). The ledger is the only work measure for it.
7. **Third-party repos** (`other_write`) hold mostly non-agent commits. Filter on `author_kind == "agent"` or `tier`.
8. **Holdout:** the tables cover all time. Mask with `holdout` before exploring.

## Which hypotheses should use it

| hypothesis | use |
| --- | --- |
| **H01 round 2** (artifact advancement as group viability) | per repo-day work commits, `distinct_files`, `site_default_commits`, `n_agents`. A group's viability = advancement of the repos it touches (agent-day → repo via work_commits) |
| **H15** (viability choice, D2.6) | add V_git = work commits per window-hour (or `distinct_files`) as a functional candidate; redo the NE41 context-erasure dip with work commits and `api_content_writes` (fixes the GitLab gap). `turn_gap_s` links commits to turns |
| **H33** (diversity–productivity) | replace write turns with work commits / `distinct_files` / `lines_changed_nobulk`; drop automated commits; restrict to #30+ |
| **H11, H31** (project labels = attention) | work commits per repo per agent-day as the *work* allocation behind project choice; contrast herding in attention vs herding in work |
| **H35** | per agent-day and repo-day output as the outcome series |
| **H113-type stuckness** | stuck = active agent-day with git write commands but no work commits (`cmd_push` > 0, `commits` = 0), or long runs of `cmd_push_printed` = 0; automated streams mark agents who delegated to scripts |
| all | `work_outcomes` for goal-level descriptive outcomes (#20, #23, #42, site goals) |

## Text for `infra/README.md` (coordinator merges)

See the final report of DQ4. The `build_all.py` step: `{"name": "work_ledger", "cmd": "py", "script": "work_ledger.py",
"outputs": ["work_repos.parquet", "work_commits.parquet", "work_api_writes.parquet", "work_daily.parquet",
"work_outcomes.parquet", "work_ledger_validation.json"]}`. It runs after `build_artifacts` and `turn_errors`, and is
offline by default.
