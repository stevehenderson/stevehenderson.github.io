# Security Policy

This is a static [Jekyll](https://jekyllrb.com/) site hosted on GitHub Pages. It has no
backend, runs no server-side code, and stores no user data.

## Reporting a vulnerability

If you find a security issue (e.g. a mixed-content link, an outdated embedded dependency,
or a content-injection vector), please report it responsibly via LinkedIn DM:

- https://www.linkedin.com/in/stevenjhenderson

Please do **not** open a public GitHub issue for security reports.

## Posture

- Dependencies are managed by GitHub's `github-pages` gem and monitored by Dependabot.
- Every push and pull request is scanned for secrets (Gitleaks) and built/validated in CI.
- External scripts are loaded with Subresource Integrity (SRI) where the source supports it.
- Defense-in-depth response headers are applied via `<meta>` equivalents (CSP,
  referrer-policy, `X-Content-Type-Options`) since GitHub Pages cannot set HTTP headers.
