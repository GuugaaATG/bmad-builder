---
name: bmad-get-manifest-bmb
description: Returns the BMad Builder (bmb) module manifest for bmad-init configuration setup. Only use when bmad-get-manifest-bmb is specifically invoked by name.
---

## Overview

This skill provides the module manifest for this module. It is not called directly by users — it exists so that `bmad-init` can discover and read the manifest at `resources/manifest.json`.

The manifest defines critical config questions that are needed for this to function properly so the JSon must be returned exactly as it is.

## Steps:

Step 1: Read and return the full `resources/manifest.json` contents
