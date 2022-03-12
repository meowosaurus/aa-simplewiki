appname = example
package = example

help:
	@echo "Makefile for $(appname)"

translationfiles:
	cd $(package) && \
	django-admin makemessages -l en --ignore 'build/*' && \
	django-admin makemessages -l de --ignore 'build/*' && \
	django-admin makemessages -l es --ignore 'build/*' && \
	django-admin makemessages -l ko --ignore 'build/*' && \
	django-admin makemessages -l ru --ignore 'build/*' && \
	django-admin makemessages -l zh_Hans --ignore 'build/*'

compiletranslationfiles:
	cd $(package) && \
	django-admin compilemessages -l en  && \
	django-admin compilemessages -l de  && \
	django-admin compilemessages -l es  && \
	django-admin compilemessages -l ko  && \
	django-admin compilemessages -l ru  && \
	django-admin compilemessages -l zh_Hans

coverage:
	rm -rfv htmlcov && \
	coverage run ../myauth/manage.py test $(package) --keepdb --failfast && coverage html && coverage report

build_test:
	rm -rfv dist && \
	python3 -m build

tox_tests:
	tox && \
	rm -rf .tox/
