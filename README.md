# stevehenderson.github.io

Personal site, built with [Jekyll](https://jekyllrb.com/) and published via
GitHub Pages. The live build runs automatically on push — the steps below are
only for previewing changes locally before you push.

## Test locally

Requires Ruby (3.x is fine) with Bundler. One-time setup, then serve:

```bash
# 1. Install gems into a project-local folder (the system gem dir is usually
#    not writable, and vendor/ is git-ignored so this won't get committed).
bundle config set --local path 'vendor/bundle'
bundle install

# 2. Build and serve with live reload at http://localhost:4000
bundle exec jekyll serve --livereload
```

Edit a file, save, and the browser refreshes automatically. Stop the server
with `Ctrl-C`.

Other handy commands:

```bash
bundle exec jekyll build          # one-off build into _site/ (no server)
bundle exec jekyll serve --drafts # also render posts in _drafts/
```

### Notes

- **First run is slow** — `bundle install` compiles the full `github-pages`
  gem set. Subsequent runs reuse `vendor/bundle`.
- **Styling** lives in `style.scss` and `_sass/`. Colors are centralized in
  [`_sass/_variables.scss`](_sass/_variables.scss) (ink/paper palette, accent,
  C64 rainbow) — change them there and every page updates.
- **Diagrams** are rendered offline; see [`_diagrams/README.md`](_diagrams/README.md).
- `vendor/`, `.bundle/`, and `_site/` are git-ignored and `vendor`/`.bundle`
  are excluded in `_config.yml` so Jekyll never tries to build the gem sources.
