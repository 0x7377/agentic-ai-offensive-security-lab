---
name: hunt-path-traversal
description: Safely validate path traversal in an observed download, archive, export, template, or file-reading workflow using bounded baseline-versus-proof comparisons.
---

# Path Traversal

Use only after a normal workflow exposes a file name or path parameter.

1. Capture a legitimate in-scope file request and its expected content fingerprint.
2. Determine the application's visible naming convention from file lists, help/status metadata, download metadata, error messages, response headers, or adjacent legitimate objects. Inspect these sources before guessing names. Do not start with operating-system files.
3. Change only the path component. Try one sibling and one parent-relative form derived from the observed convention; use at most two encoding variants if normalization is evident.
4. Confirm only when content outside the intended directory is returned and has a distinct, recognizable fingerprint. Echoed paths, `200`, generic errors, or response-length changes alone are insufficient.
5. Do not read credentials, private keys, environment files, system password files, or unrelated user documents. Prefer the training application's harmless internal marker/configuration file.
6. Stop after the first harmless proof and bind legitimate baseline plus traversal Traffic to the Finding.

If the application supplies no filename convention or discoverable adjacent object, close the row as `not verified`; do not guess large filename lists.
