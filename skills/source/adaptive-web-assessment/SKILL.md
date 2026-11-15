---
name: adaptive-web-assessment
description: Route an authorized, time-boxed black-box web assessment from observed application behavior to one focused validation path without assuming the vulnerability class in advance. Use when the asset is known but its technology and likely weakness are not.
---

# Adaptive Web Assessment

Use only the companies and assets attached to the current Task. Do not inherit Traffic, Findings, transcripts, credentials, or files from another Task.

## Outcome and operating mode

Do not assume a vulnerability type from the company name, page theme, URL, or Task wording.

- **Focused mode:** when the Task goal requests one issue or a short exercise, independently verify at most one meaningful issue and stop.
- **Comprehensive mode:** when the Task goal requests broad coverage or multiple findings, continue through the coverage matrix below until every applicable row is tested or explicitly marked `not applicable` / `not verified`. Do not stop merely because the first issue was confirmed.

Always invoke this Skill through the `Skill` tool before issuing target requests. Specialist procedures must also be invoked through the `Skill` tool rather than recalled from model memory. The Skill usage ledger is part of the course evidence.

## Phase 0: resolve the attached company scope

Do this once before concluding that the Task has no target:

1. Call `list_assets` for the current Task.
2. Continue only when it returns at least one explicit HTTP(S) service and every returned service belongs to the same attached company. Use only that company's service and continue to Phase 1.
3. If it returns zero services, services from more than one company, or a service without a company association, do **not** call `list_companies`, scan the Docker network, guess hostnames, or inspect another Task. Stop and report `scope unresolved` so a person can correct the Task-company selection.

The course Compose links only the exact HTTP(S) URL manually entered in the company scope to the selected Task. Worker access to `list_companies` is intentionally disabled; a Worker never needs to enumerate other companies to recover its scope.

## Mandatory version gate

Immediately after the first service response, inspect headers and visible metadata for exact product or runtime versions. If any exact version is directly observed, complete one bounded `known-vulnerability-triage` pass before reading application JavaScript, submitting a form, changing a parameter, or guessing a path:

1. Load `known-vulnerability-triage`.
2. Use the CVE Intelligence MCP's exact CPE lookup when vendor/product coordinates can be established. Do not substitute a generic keyword search.
3. Classify the version result as `applicable`, `not-affected`, or `inconclusive`, including required deployment prerequisites.
4. If no High/Critical candidate plausibly reaches an exposed feature, close this gate and continue to business-request testing. Do not repeat version searches for the same product.
5. If a High/Critical candidate and its deployment prerequisites match, use that as the selected route before any speculative input testing.
6. If that same response explicitly declares a safe command or vulnerability emulator, do not close the candidate as `applicable-unconfirmed` and do not continue to generic form testing. Load `authorized-exploit-validation`, read the conditional reference for the identified CVE, and perform only its safe-emulator branch. This step is mandatory before leaving the version route.

A generic language or server version may produce no applicable web-facing candidate; that is an acceptable quick result. The purpose of this gate is to avoid missing a strong known-vulnerability path, not to force every banner into a Finding. A version disclosure alone is never a Finding.

## Phase 1: establish a compact baseline

1. Use the HTTP service resolved in Phase 0. Do not widen scope or discover unrelated hosts.
2. Open the service as a normal user. Record the landing response, security-relevant headers, visible technology/version evidence, authentication state, and the application's primary business function.
3. In focused mode, exercise at most two high-signal business interactions. In comprehensive mode, visit each visible business area once and build a compact endpoint/input/object map. Capture normal requests and responses before changing anything. During baseline collection, do not upload executable content, guess backup/source paths, enumerate directories, or fuzz filenames and delimiters.
4. Build a short candidate list from observed evidence, then select one candidate with the clearest trust boundary and cheapest decisive proof.

High-signal evidence includes:

- a user-controlled value reaching a server-side query, filter, lookup, or report;
- a value reflected into rendered HTML or a browser DOM sink;
- an object identifier used to retrieve data owned by a user, department, or tenant;
- an exact product/runtime version plus deployment details that can be checked against current vulnerability intelligence.

Absence of a security header by itself is not a meaningful candidate.

## Phase 2: route by evidence

Load only the most relevant specialist Skill after the baseline supports it:

- visible routes, forms, API calls, parameters, or downloadable objects: `api-recon`;
- server-side query or filter behavior: `hunt-sqli`;
- HTML reflection or DOM execution path: `hunt-xss`;
- object ownership or cross-department/tenant boundary: `hunt-idor`;
- role-only or administrator function boundary: `hunt-bfla`;
- file name, download, archive, export, template, or path parameter: `hunt-path-traversal`;
- exact product/runtime version: `known-vulnerability-triage` and the CVE Intelligence MCP.

This routing step is a hard gate, not a suggestion:

- Before sending the first changed-value proof request for a recognized class, invoke its specialist Skill through the `Skill` tool.
- Do not call `report_finding` unless the matching specialist appears in the current Task's Skill usage ledger. If an issue was noticed during baseline mapping, load the specialist and independently repeat the minimum baseline-versus-proof comparison before reporting it.
- In comprehensive mode, invoke `api-recon` once after the normal workflow map is established, then use the specialist for every evidence-supported row. Do not load a specialist for a row with no observed surface merely to increase a usage count.
- A Worker must not substitute remembered methodology for the Skill invocation, even when the vulnerability already appears obvious.

If several signals exist, prefer the route that needs the fewest requests and gives a direct baseline-versus-proof comparison. Do not run every specialist checklist and do not enumerate the whole application.

When the exact-version check returns a Critical/High candidate whose prerequisites match the observed deployment, prioritize that route over speculative filename, hidden-path, backup-file, or generic injection probes. If no applicable candidate is found, return to the business-request candidates.

For a version-based candidate, a banner is only a lead. Establish affected range and deployment prerequisites. Load `authorized-exploit-validation` only when all of the following are true:

- the Task explicitly permits active validation on the isolated training asset;
- an applicable CVE and relevant deployment prerequisites are established;
- minimal target-side validation is necessary to distinguish applicability from actual impact.

Follow any conditional reference named by that Skill. Prefer a target-provided harmless validation mechanism when one is visible and independently verifiable. Otherwise stop at `applicable-unconfirmed`; never improvise or combine public PoCs.

Exception for an explicitly declared training emulator: when the scoped response contains a safety header or body statement that unambiguously says the vulnerable effect is emulated without arbitrary execution, load `authorized-exploit-validation`, follow its matching conditional reference, and use only the documented emulator handshake. Record the outcome as simulated validation, never as actual code execution. This exception does not apply to ordinary staging, development, or production systems.

## Comprehensive coverage matrix

In comprehensive mode, keep this matrix in the working notes. A row can be closed only with observed evidence or a clear reason it is not applicable.

| Area | Minimum comparison |
|---|---|
| Query/input handling | inert baseline vs one low-impact changed value |
| Stored or rendered content | baseline render vs unique harmless browser canary |
| Object authorization | owner/tenant baseline vs one foreign object reference |
| Function authorization | ordinary role vs one privileged function request |
| File/path handling | legitimate file baseline vs one bounded sibling/parent-path attempt |
| Known component vulnerabilities | exact observed version → MCP affected-range and prerequisite check |

After confirming a finding, record it and continue with the next unclosed row while budget remains. Deduplicate findings that share the same endpoint, root cause, and proof.

## Phase 3: controlled differential

- Change one input, identifier, or condition at a time.
- Compare status, response shape, record ownership/count, rendered DOM, and security-relevant side effects against the baseline.
- A server error, timeout, crash, OOM, reflected string, version banner, or HTTP 200 alone is not proof.
- Use the smallest read-only or disposable proof that demonstrates the boundary failure.
- In focused mode, stop after the first confirmed issue. In comprehensive mode, stop probing that route after the first decisive proof and move to the next unclosed coverage row. Do not enumerate schemas, bulk records, many neighboring identifiers, additional accounts, or unrelated files.

## Phase 4: evidence gate and report

A confirmed Finding requires all of:

1. the affected request or component is inside the attached company asset scope;
2. baseline and changed behavior are both captured;
3. the security impact is directly observed rather than inferred;
4. the reproduction works with the minimum request sequence;
5. the Finding states evidence, impact, confidence, and a concrete remediation direction.

Bind the baseline and proof Traffic to one Finding. Use ARTEX traffic-aware HTTP/browser tooling or the configured capture proxy so the requests exist in the Traffic tab; pasted terminal output alone is not sufficient course evidence. If the evidence gate is not met within the Task budget, report the candidate as unconfirmed with the failed step; do not inflate certainty or severity.

## Time-box

- Focused mode: spend no more than one quarter establishing the baseline, the middle half validating one candidate, and the final quarter confirming and reporting.
- Comprehensive mode: spend no more than one fifth mapping the surface, divide the middle three fifths across unclosed coverage rows, and reserve the final fifth for independent confirmation, deduplication, Traffic binding, and reporting.
- If a route fails its decisive comparison twice, close it as unverified and move to the next evidence-supported route.
