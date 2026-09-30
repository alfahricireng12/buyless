# Install once, use in new chats

BuyLess is an Agent Skill with a small offline installer. The repository stays the source of truth; installing copies the runtime instructions, references, examples, license and two optional Python helpers to a host-discovered folder. No shopping server or model API is included.

## Host profiles

| Profile | Project directory | Global directory | Invocation |
|---|---|---|---|
| `codex` | `.agents/skills/buyless` | `~/.agents/skills/buyless` | `$buyless` in Codex CLI/IDE; use the skill selector in the desktop host |
| `claude` | `.claude/skills/buyless` | `~/.claude/skills/buyless` | `/buyless` in Claude Code |
| `cursor` | `.cursor/skills/buyless` | `~/.cursor/skills/buyless` | Select the installed skill or ask to use BuyLess |
| `universal` | `.agents/skills/buyless` | `~/.agents/skills/buyless` | Host-specific; only hosts reading this standard location |

`~` means the current OS user's home directory. These are local discovery profiles, not a promise that a host has web access or that every model will invoke the skill automatically. Install either `codex` or `universal` for the same scope; they share the same destination.

Directory conventions were checked against [OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills), [Claude Code skill documentation](https://code.claude.com/docs/en/skills), and [Cursor skill documentation](https://cursor.com/docs/skills). Host policies can disable skills. Cloud/remote sessions need files in their own environment or the host's separate sync/distribution flow.

## Commands

Run these from the extracted BuyLess repository. Installation needs Node.js 20+; Python is only for optional shopping helpers.

```sh
node bin/buyless.mjs init --ai codex --global --dry-run
node bin/buyless.mjs init --ai codex --global
node bin/buyless.mjs doctor --ai codex --global
```

For a single project:

```sh
node bin/buyless.mjs init --ai claude --project "/path/to/my project"
node bin/buyless.mjs doctor --ai claude --project "/path/to/my project"
```

`init` preflights file conflicts, copies missing files, and leaves unrelated files alone. Repeating it with the same version is safe. It rejects symbolic links/junctions rather than writing through them. A permissions or disk failure may leave an incomplete copy; rerun the same version to fill missing files. `doctor` reports missing or different files relative to this downloaded release and exits with code 1 when any are found. Invalid arguments and installation errors exit with code 2.

For upgrades, back up and move your existing `buyless` skill directory outside the host's skill-discovery folders, then run the new release's installer. There is deliberately no force overwrite or recursive uninstall command. To uninstall, remove only the installed `buyless` folder after preserving your changes. Installing the CLI with npm and installing skill files are separate operations; removing one does not remove the other.

## Verify in another chat

1. Start a new session in the installed host and correct project/scope.
2. Check that BuyLess appears in the host's skill selector. If absent, restart the host and check its skill permissions and configured directories.
3. Ask: `Use BuyLess. I want to buy a Flipper Zero in Miami.`
4. Confirm it uses Miami, searches real sources, reports in English by default, and separates unverified costs and authenticity claims. The host must have search/page-reading tools for a live test.

The installer tests exercise filesystem behavior in isolated directories. They do not certify runtime behavior in Claude Code, Cursor or every Codex release.

## ChatGPT and Codex plugin

This local installer does not modify your ChatGPT account. The repository also contains a skills-only plugin at `plugins/buyless` and a repo marketplace manifest at `.agents/plugins/marketplace.json`. The plugin packages the same BuyLess runtime instructions without an MCP server or BuyLess API.

For local testing in the ChatGPT desktop app:

1. Open this repository as the active project and restart the app so it discovers the repo marketplace.
2. Open **Plugins**, select the **BuyLess Community** source, open **BuyLess**, and install it.
3. Start a new Chat or Work conversation. Describe the purchase naturally or select `@BuyLess` explicitly.
4. Confirm the chat has usable web search or browser access. Installation provides the workflow, not web access.

After changing `SKILL.md`, `agents`, `references`, examples, or helper scripts, run `python scripts/build_plugin.py` before validation so `plugins/buyless/skills/buyless` stays synchronized.

Supported ChatGPT surfaces can use an installed plugin in Chat or Work, but actual web tools and workspace permissions still apply. The repository marketplace can be shared publicly through a Git repository. Universal directory listing requires submission, review, and publication through OpenAI's plugin process. Do not claim this repository is already in the universal Plugins Directory.

## Public release

The package deliberately has `private: true` because public plugin distribution does not require npm publication. Publish the repository for Git marketplace distribution, or upload the prepared skills-only archive through the OpenAI plugin submission portal for universal directory review. See [publication.md](publication.md).
