.PHONY: setup doctor list audit quality security large-quality report

setup:
	git submodule update --init --recursive
	python3 scripts/init_large_task.py

doctor:
	python3 bench.py doctor

list:
	python3 bench.py list

audit: security quality large-quality

security:
	python3 bench.py security-audit

quality:
	python3 bench.py quality-audit

large-quality:
	python3 bench.py quality-audit-large

report:
	python3 bench.py report
