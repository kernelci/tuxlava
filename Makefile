export PROJECT := tuxlava
check: spellcheck stylecheck test

include $(shell tuxpkg get-makefile)

stylecheck: style flake8

spellcheck:
	codespell \
		--check-filenames \
		--skip '.git,public,dist,*.sw*,*.pyc,tags,*.json,.coverage,htmlcov,*.jinja2,*.yaml'
