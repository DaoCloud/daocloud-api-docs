---
hide:
  - toc
---

# OpenAPI Documentation Generation Flow

This page uses Ghippo as an example to explain how OpenAPI documentation is produced.
The main idea is to generate a Swagger JSON file and then automatically submit a PR to the documentation repository.

1. Add the following target to `Makefile`:

    ```go title="Makefile"
    .PHONY += doc.openapi
    doc.openapi:
        $(eval swagger_path ?= swagger)
        @bash hack/gen-openapi-json.sh ghippo $(GHIPPO_VERSION) $(swagger_path)
    ```

1. Write the script that generates the Swagger JSON file.

1. Write the script that opens a PR against the documentation repository.

1. Update the GitLab CI configuration so that the OpenAPI documentation is published automatically for tagged releases.
