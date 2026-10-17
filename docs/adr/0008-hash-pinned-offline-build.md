# ADR 0008: Hash pinned offline build

## Status
Accepted.

## Context
Deployment profile B is an office network with no outbound traffic, and a reviewer may need to open the tool from a file or a USB stick. A normal Vite build uses module scripts and separate assets that need a server. Inlining everything into one file solves that, but a strict Content-Security-Policy blocks inline script and style, and loosening it to allow any inline code would remove the protection the policy is there to give.

## Options considered
1. Ship the normal build and ask the reader to run a local server.
2. Inline everything and allow `'unsafe-inline'` for scripts and styles.
3. Inline everything and rewrite the page policy to allow exactly the inline blocks present, identified by their SHA-256 hashes.

## Decision
We chose option 3, implemented in `site/vite.single.config.ts` and run by `npm run build:offline`. The plugin moves the entry script and the stylesheet into the page, then rewrites the meta Content-Security-Policy to `default-src 'none'`, with `script-src` and `style-src` set to the SHA-256 of the one inline script and the one inline style. Fonts are allowed only as `data:`, images only as `data:` and `blob:`, and `base-uri` and `form-action` are set to `'none'`. The output is one file, `dist-offline/index.html`.

## Consequences
- The file opens from `file://` with no network access, and a browser test checks that it shows the headline.
- Any change to the script or style changes its hash. The hash is computed at build time, so the policy always matches the file it ships in, and injected inline code does not run.
- `style-src-attr 'unsafe-inline'` is still allowed, because the interface sets inline style attributes. This is a known residual weakness.
- A meta policy cannot set `frame-ancestors`, so framing protection depends on how the file is served.
