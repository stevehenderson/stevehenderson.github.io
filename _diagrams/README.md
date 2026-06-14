# Diagram sources

Mermaid source for diagrams used in posts. This folder is `_`-prefixed, so Jekyll
does **not** publish it — only the rendered PNGs in `images/diagrams/` ship.

We render to PNG offline (no browser-side Mermaid, keeps the CSP tight) using
`@mermaid-js/mermaid-cli` driven by the system Chrome.

## Re-render after editing a `.mmd`

```bash
# one-time: tell puppeteer to use the system browser instead of downloading one
cat > /tmp/puppeteer.json <<'EOF'
{ "executablePath": "/usr/bin/google-chrome", "args": ["--no-sandbox", "--disable-gpu"] }
EOF

# render (run from repo root); -s 2 = 2x scale for crisp retina output
PUPPETEER_SKIP_DOWNLOAD=1 npx --yes @mermaid-js/mermaid-cli \
  -i _diagrams/lab1-inspect.mmd  -o images/diagrams/lab1-inspect.png  \
  -t neutral -b white -s 2 -p /tmp/puppeteer.json

PUPPETEER_SKIP_DOWNLOAD=1 npx --yes @mermaid-js/mermaid-cli \
  -i _diagrams/lab2-detonate.mmd -o images/diagrams/lab2-detonate.png \
  -t neutral -b white -s 2 -p /tmp/puppeteer.json

PUPPETEER_SKIP_DOWNLOAD=1 npx --yes @mermaid-js/mermaid-cli \
  -i _diagrams/lab3-trigger-sequence.mmd -o images/diagrams/lab3-trigger-sequence.png \
  -t neutral -b white -s 2 -p /tmp/puppeteer.json
```

| source | rendered | used in |
|---|---|---|
| `lab1-inspect.mmd`         | `images/diagrams/lab1-inspect.png`         | XZ backdoor post — inspection lab |
| `lab2-detonate.mmd`        | `images/diagrams/lab2-detonate.png`        | XZ backdoor post — detonation lab |
| `lab3-trigger-sequence.mmd`| `images/diagrams/lab3-trigger-sequence.png`| XZ backdoor post — trigger/hook sequence |
