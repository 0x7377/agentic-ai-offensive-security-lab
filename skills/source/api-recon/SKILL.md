---
name: api-recon
description: Build a compact, evidence-based map of visible web routes, forms, API endpoints, parameters, objects, roles, and file operations before vulnerability validation. Use for authorized black-box application reconnaissance.
---

# API Recon

Use only the HTTP(S) service attached to the current Task. This Skill maps the normal application surface; it does not authorize exploitation by itself.

1. Open the landing page and follow visible navigation as a normal user.
2. Record page/route, UI action, HTTP method, endpoint, parameter names, authentication state, returned object identifiers, and file operations.
3. Inspect client JavaScript only as delivered to the browser. Do not read server files, another Task's workspace, source maps that are not publicly served, or local Compose source.
4. Prefer browser-observed requests and Traffic records over guessing paths. Limit discovery to visible links and calls triggered by normal workflows.
5. Group candidates by trust boundary: user input, stored output, object ownership, role-only function, file/path, and exact component version.
6. Return the compact map to `adaptive-web-assessment`; do not claim a vulnerability without a specialist differential test.

In comprehensive mode, one pass through each visible business area is enough. Avoid directory brute force and large wordlists.
