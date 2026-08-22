# cli-anything-browser — Browser Automation CLI

A command-line interface for browser automation using [DOMShell](https://github.com/apireno/DOMShell)'s MCP server. Maps Chrome's Accessibility Tree to a virtual filesystem for agent-native browser automation.

## Features

- **Filesystem-first navigation**: Use `ls`, `cd`, `cat` to explore web pages
- **Search**: `grep` for text patterns in the accessibility tree
- **Actions**: `click`, `type` to interact with elements
- **JSON output**: `--json` flag for machine-readable output
- **Interactive REPL**: Stateful session with command history
- **Daemon mode**: Optional persistent connection for faster interactive use
- **DNS-pinned egress**: Every ordinary Chrome connection is made by a private
  loopback proxy that resolves once, rejects non-global addresses, then opens
  the socket to that numeric address. A URL cannot rebind to localhost or an
  intranet after the CLI validates it.

## Installation

### Prerequisites

1. **Node.js 18+ and npm** (required only for the verified one-time setup):
   ```bash
   # Install Node.js from https://nodejs.org/
   node --version
   npm --version
   ```

   Install the compatible managed-browser launcher once:
   ```bash
   npm install -g agent-browser@0.34.0
   agent-browser install
   ```

2. **A locally built, trusted DOMShell extension**:
   - Build the extension from the audited DOMShell source and store its build
     output in a user-owned directory that is not group/world-writable.
   - Point the CLI to that directory before first use. The CLI launches its
     own isolated Chrome profile; it does not attach to an existing Chrome.
   ```bash
   export CLI_ANYTHING_DOMSHELL_EXTENSION_DIR="$HOME/.local/share/cli-anything/domshell-extension"
   cli-anything-browser secure install
   cli-anything-browser secure start
   ```

   `secure install` uses the bundled lockfile and `npm ci --ignore-scripts`.
   It verifies package integrity during installation; ordinary CLI commands
   run only the resulting owner-private local files and never use `npx`.

   The extension control socket gets one random-port, token-authenticated
   loopback exception. General page traffic remains proxied and cannot reach
   arbitrary localhost, private, link-local, or mixed-DNS destinations.

3. **Python 3.10+**:
   ```bash
   python --version
   ```

### Install CLI

```bash
cd browser/agent-harness
pip install -e .
```

Verify installation:
```bash
cli-anything-browser --help
cli-anything-browser secure status
```

`DOMSHELL_TOKEN` and `DOMSHELL_PORT` from the legacy unmanaged integration are
not used. The managed runtime creates its own private credentials and never
prints them.

## Usage

### One-Shot Commands

```bash
# Open a page
cli-anything-browser page open https://example.com

# List elements at root
cli-anything-browser fs ls /

# Navigate into a section
cli-anything-browser fs cd /main

# List elements in current directory
cli-anything-browser fs ls

# Read element content
cli-anything-browser fs cat /main/button[0]

# Search for text
cli-anything-browser fs grep "Login"

# Click an element
cli-anything-browser act click /main/button[0]

# Type into an input
cli-anything-browser act type /main/input[0] "Hello, World!"

# Get page info
cli-anything-browser page info

# Navigate back/forward
cli-anything-browser page back
cli-anything-browser page forward
```

**Note:** One-shot commands each start with a fresh session (no URL or working directory). For stateful workflows (like `cd` followed by `ls` without a path), use the REPL instead.

### JSON Output

```bash
# Get machine-readable output
cli-anything-browser --json fs ls /

# Returns:
{
  "path": "/",
  "entries": [
    {
      "name": "main",
      "role": "landmark",
      "path": "/main"
    }
  ]
}
```

### Daemon Mode (Persistent Connection)

For faster interactive use, start daemon mode within a REPL session:

```bash
# Start REPL with daemon mode
cli-anything-browser --daemon

# Or start daemon within REPL
session daemon-start

# Run commands (uses persistent connection)
fs ls /
fs cd /main

# Stop daemon when done
session daemon-stop
```

**Note:** Daemon mode only works within a single running process (REPL or `--daemon` flag). State does not persist across separate CLI invocations.

### Interactive REPL

Run without arguments to enter interactive mode:

```bash
cli-anything-browser
```

REPL commands:
- `page open <url>` — Open a URL
- `fs ls [path]` — List elements
- `fs cd <path>` — Change directory
- `fs cat [path]` — Read element
- `fs grep <pattern>` — Search for text
- `fs pwd` — Print working directory
- `act click <path>` — Click element
- `act type <path> <text>` — Type text
- `session status` — Show session state
- `help` — Show commands
- `quit` — Exit REPL

## Command Groups

### `page` — Page Navigation
- `open <url>` — Navigate to URL
- `reload` — Reload current page
- `back` — Navigate back in history
- `forward` — Navigate forward in history
- `info` — Show current page info

### `fs` — Filesystem Commands
- `ls [path]` — List elements at path
- `cd <path>` — Change directory
- `cat [path]` — Read element content
- `grep <pattern> [path]` — Search for text
- `pwd` — Print working directory

### `act` — Action Commands
- `click <path>` — Click an element
- `type <path> <text>` — Type text into input

### `session` — Session Management
- `status` — Show session status
- `daemon-start` — Start persistent daemon mode
- `daemon-stop` — Stop daemon mode

### `secure` — Managed Browser Runtime
- `secure status` — Display non-secret runtime status without starting Chrome
- `secure start` — Launch the isolated Chrome, pinned MCP server, and egress proxy
- `secure stop` — Stop all three managed runtime processes

## Path Syntax

DOMShell uses a filesystem-like path syntax for the Accessibility Tree:

```
/                           — Root (page)
/main                       — Main landmark
/main/div[0]                — First div in main
/main/div[0]/button[2]      — Third button in first div
```

Array indices are 0-based. Use relative paths with `..` to go up.

## Examples

### Basic Navigation
```bash
# Open a page
cli-anything-browser page open https://example.com

# Explore structure
cli-anything-browser fs ls /
cli-anything-browser fs cd /main
cli-anything-browser fs ls

# Go back to root
cli-anything-browser fs cd /
```

### Search and Click
```bash
# Open page and search for login button
cli-anything-browser page open https://example.com/login
cli-anything-browser fs grep "Login"

# Click the login button (adjust path as needed)
cli-anything-browser act click /main/button[0]
```

### Form Fill
```bash
# Type into form fields
cli-anything-browser act type /main/input[0] "user@example.com"
cli-anything-browser act type /main/input[1] "password123"

# Click submit
cli-anything-browser act click /main/button[0]
```

## Testing

Run tests:

```bash
# Unit tests (no Chrome required)
pytest cli_anything/browser/tests/test_core.py -v

# E2E tests (requires Chrome + DOMShell)
pytest cli_anything/browser/tests/test_full_e2e.py -v
```

## Troubleshooting

### "DOMShell runtime is not installed"
Install Node.js 18+ from https://nodejs.org/, then run:

```bash
cli-anything-browser secure install
```

### "CLI_ANYTHING_DOMSHELL_EXTENSION_DIR must point ..."
Build the trusted DOMShell extension and set that variable to its directory
containing `manifest.json`. The directory is loaded only into CLI-Anything's
isolated browser profile.

### "Managed DOMShell ..."
Run `cli-anything-browser secure status`, confirm the local runtime is installed,
then run `cli-anything-browser secure start`. Do not work around this by
pointing the CLI at an existing Chrome or exporting a long-lived DOMShell token.

### Setup is incomplete
Run `cli-anything-browser secure install`. This is the only command that
downloads the lockfile-pinned DOMShell packages; npm install scripts remain
disabled. Use `--daemon` mode for persistent connections after setup.

## Architecture

This CLI follows the [CLI-Anything harness methodology](https://github.com/HKUDS/CLI-Anything/tree/main/cli-anything-plugin/HARNESS.md):

- **Backend**: pinned DOMShell MCP server via stdio transport
- **Browser boundary**: isolated Chrome profile and local DNS-pinning proxy
- **State**: Page state (URL, working directory, navigation history)
- **Pattern**: Filesystem-first commands map to Accessibility Tree

## Links

- [DOMShell GitHub](https://github.com/apireno/DOMShell)
- [CLI-Anything](https://github.com/HKUDS/CLI-Anything)
- [Issue #90](https://github.com/HKUDS/CLI-Anything/issues/90)

## License

Apache License 2.0 — See [CLI-Anything](https://github.com/HKUDS/CLI-Anything) for details.
