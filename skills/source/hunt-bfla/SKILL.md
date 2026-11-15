---
name: hunt-bfla
description: Safely validate broken function-level authorization by comparing an ordinary user's allowed actions with one privileged or administrator function on the same scoped application.
---

# Broken Function-Level Authorization

Use when normal navigation or observed API calls expose role-specific operations.

1. Establish an ordinary-role baseline and record the action that the UI permits.
2. Identify one privileged function from visible metadata, disabled UI, or an observed API route. Do not brute-force hidden administrator paths.
3. Replay only that function with the ordinary session, preserving method and content type.
4. Confirm impact from an application-visible state or response object. A `200`, different error, or route existence alone is not proof.
5. Stop after one decisive comparison. Do not delete records, change security settings, create privileged users, or perform bulk actions.
6. Bind the ordinary baseline and privileged proof Traffic to the Finding and distinguish function authorization from object-level IDOR.
