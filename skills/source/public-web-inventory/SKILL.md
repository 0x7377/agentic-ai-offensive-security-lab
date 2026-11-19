---
name: public-web-inventory
description: Inventory the observable attack surface of one authorized public web origin without exploitation. Use when asked to find same-origin paths, endpoints, APIs, forms, input fields, or mutable parameters from public HTML and JavaScript. Produce an evidence table and do not guess paths or follow links outside the allowed origin.
license: Apache-2.0
compatibility: opencode
metadata:
  audience: security-training
  workflow: public-web-recon
---

# Public Web Inventory

## Scope gate

1. Extract the exact allowed origin from the request.
2. Do not access another scheme, host, or port.
3. Treat external links as inventory only. Record but never follow them.
4. Use read-only GET or HEAD requests. Do not submit forms or change state.
5. Stop after 20 HTTP requests or five minutes, whichever comes first.

## Workflow

1. Record the root page title, status, and response headers.
2. Read `/robots.txt` and `/sitemap.xml` if present.
3. Enumerate same-origin navigation links, forms, input fields, and query parameters from public pages.
4. Inspect referenced JavaScript text for same-origin endpoint and API paths. Do not guess endpoints.
5. Record the observed source for every item: HTML link, form action, script reference, JavaScript text, or response header.
6. Do not visit a path excluded by `robots.txt`. Record it as excluded evidence.
7. Deduplicate normalized paths and classify them as page, endpoint, API, form action, or external boundary.

Read `references/report-schema.md` before writing the result.

## Stop and report

Stop immediately if the target redirects outside the allowed origin, authentication is requested, or a state-changing action is required. Report incomplete coverage and the reason instead of expanding scope.
