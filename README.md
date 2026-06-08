# n8n-mcp-workflow-setup

**Configure imported n8n workflows programmatically — bind credentials, pick models, and fix the
"author's-account" landmines — entirely through the [n8n-MCP](https://github.com/czlonkowski/n8n-mcp),
without clicking around the editor.**

When you import a community or course `*.json` workflow into your own n8n, it never just runs. The
export carries the *original author's* credential IDs and label IDs, so every node comes in
unauthenticated and a few nodes fail outright. The usual fix is a tedious manual pass: open every node,
pick your credential, select a model, hunt down the broken parameters.

This repo shows how to do that whole pass **as a small batch of declarative operations** an AI agent (or
you) can replay against the n8n-MCP `update_workflow` tool. It's reproducible, diffable, and version-controlled.

---

## Why this exists

A workflow export looks portable but isn't:

1. **Credentials don't travel.** n8n never exports secrets, and the author's credential *IDs* don't exist
   in your instance — so on import, every node loses its auth.
2. **Hard-coded resource IDs break.** Gmail label IDs, Slack channel IDs, Notion DB IDs, etc. are
   account-specific. The author's `Label_1` is meaningless in your account.
3. **Idempotency bugs surface on the *second* run.** e.g. a "create label" node returns
   `409 — Label name exists` once the label is there.
4. **Some fields ship blank.** Model pickers, in particular, often export empty.

You can fix all of that by hand. Or you can express it once, like this:

```jsonc
// update_workflow(workflowId, operations)
[
  { "type": "setNodeCredential", "nodeName": "Gmail Trigger",  "credentialKey": "gmailOAuth2",   "credentialId": "<YOUR_GMAIL_CRED_ID>",  "credentialName": "Gmail account" },
  { "type": "setNodeCredential", "nodeName": "OpenRouter Chat Model", "credentialKey": "openRouterApi", "credentialId": "<YOUR_OPENROUTER_CRED_ID>", "credentialName": "OpenRouter account" },
  { "type": "setNodeParameter",  "nodeName": "OpenRouter Chat Model", "path": "/model", "value": "openai/gpt-4.1-mini" },
  { "type": "setNodeDisabled",   "nodeName": "Create a label", "disabled": true },
  { "type": "setNodeParameter",  "nodeName": "Add label to message", "path": "/labelIds", "value": ["IMPORTANT"] }
]
```

---

## What's in here

```
workflows/    Two ready-to-import n8n workflows (credential-free templates)
operations/   The matching n8n-MCP update_workflow operation batches to configure each one
```

| Workflow | What it does |
|---|---|
| [`workflows/gmail-inbox-classifier.json`](workflows/gmail-inbox-classifier.json) | Polls Gmail → classifies each email (*Important / Newsletter / Subscription*) with an LLM → labels + AI-drafts a reply to important mail, routes newsletters to a cleanup branch. |
| [`workflows/personalized-newsletter.json`](workflows/personalized-newsletter.json) | Chat-triggered AI agent that researches a topic via Tavily web search and emails a curated newsletter through Gmail, with buffer memory. |

Both originate from the [Outskill AI Accelerator](https://outskill.com) Day-2 templates and are included
here as **generic, credential-free** starting points.

---

## Prerequisites

1. An n8n instance (Cloud or self-hosted).
2. The **[n8n-MCP](https://github.com/czlonkowski/n8n-mcp)** server connected to your AI client
   (Claude Code, Claude Desktop, Cursor, etc.). It talks to your n8n over the MCP endpoint, so it works
   even when the public REST API is disabled on your plan.
3. Credentials created **once** in n8n (Settings → Credentials): `gmailOAuth2`, `openRouterApi`,
   `tavilyApi`. The MCP references credentials by ID; it never handles the secret itself.

---

## How to use

### 1. Import the workflow

Either through the n8n UI (*Workflows → Import from File*) or with the MCP
`create_workflow_from_code`. Note the resulting **workflow ID**.

### 2. Find your credential IDs

```
list_credentials()
```

### 3. Apply the setup operations

Open the matching file in [`operations/`](operations/), replace the `<YOUR_*_ID>` placeholders with your
own IDs, and pass the array to:

```
update_workflow(workflowId = "<YOUR_WORKFLOW_ID>", operations = [ ... ])
```

`update_workflow` is **atomic** — if any operation fails (bad node name, missing credential), the whole
batch is rejected and nothing changes. Re-check node names with `get_workflow_details` and retry.

### 4. Reload and run

⚠️ n8n does **not** live-refresh an editor tab that was already open before an API edit — reload the
workflow page, then *Execute*.

---

## The operation cheat-sheet

| Need | Operation |
|---|---|
| Attach a credential to a node | `setNodeCredential` (`nodeName`, `credentialKey`, `credentialId`, `credentialName`) |
| Set a parameter inside `parameters` | `setNodeParameter` (`nodeName`, `path` e.g. `/model`, `value`) |
| Skip a node without rewiring | `setNodeDisabled` — **a disabled node passes data straight through** |
| Re-route a branch | `removeConnection` + `addConnection` |
| Rename / move | `renameNode` / `setNodePosition` |

### Debugging a failed run

`get_execution(executionId, includeData: true)` returns the failing node, the branch that was taken, and
the raw provider error body — this is how you confirm, e.g., a `409 Label name exists or conflicts`
instead of guessing.

---

## Worked example: the Gmail classifier

The raw template fails in three documented ways; here's the complete fix as one reproducible flow — see
[`operations/gmail-inbox-classifier.ops.json`](operations/gmail-inbox-classifier.ops.json):

1. **Bind credentials** on all Gmail + OpenRouter nodes.
2. **`409 Label name exists`** → disable the `Create a label` node (it's pass-through, so the chain holds).
3. **Invalid label IDs** → set `Add label to message` to the valid `["IMPORTANT"]` system label.
4. *(Optional reply mode)* swap `AI Agent → Reply to a message` for `AI Agent → Create a draft` to review
   replies as unsent drafts instead of auto-sending.

---

## License

[MIT](LICENSE).

Workflow templates are derived from publicly distributed course material and are provided as-is for
educational use. The n8n-MCP project is © its respective authors.
