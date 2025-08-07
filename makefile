# Makefile

.PHONY: test test-reset

# Run backend tests in venv
test:
	source venv/bin/activate && pytest backend/

# Reset venv and run tests
test-reset:
	./reset_backend.sh && source venv/bin/activate && pytest backend/

