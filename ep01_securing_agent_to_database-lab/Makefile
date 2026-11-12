PYTHON ?= .venv/bin/python
PYTEST ?= .venv/bin/pytest

.PHONY: help test-unit test-snippet-sync deploy-track-a deploy-track-b test-attacks destroy

help:
	@echo "Targets:"
	@echo "  test-unit          Run Phase 1 unit tests (no cloud resources)"
	@echo "  test-snippet-sync  Verify episode HTML snippets match tested code"
	@echo "  deploy-track-a     Deploy Track A (Cloud Run + Envoy + tokenx)"
	@echo "  deploy-track-b     Deploy Track B (Agent Runtime + Agent Gateway)"
	@echo "  test-attacks       Run T1-T8 attack suite against TARGET=track-a|track-b"
	@echo "  destroy            Tear down Terraform resources"

test-unit:
	$(PYTEST) tests/unit

test-snippet-sync:
	$(PYTEST) tests/test_snippet_sync.py

deploy-track-a:
	@echo "See docs/ and infra/terraform/02_track_a_cloudrun_envoy (Phase 3)"

deploy-track-b:
	@echo "See docs/ and infra/terraform/03_track_b_enterprise (Phase 4)"

test-attacks:
	@echo "See attacks/walkthrough.py and tests/attacks (Phase 3/4)"

destroy:
	@echo "Run terraform destroy in infra/terraform/*"
