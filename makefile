test:
	@python setup.py test

nuke:
	@rm -rf .tox
	@rm -rf *.egg-info
	@rm -f .coverage
	@rm -rf tests/__pycache__
