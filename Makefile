LOCAL_GAE_LIB := /usr/local/google_appengine
BUILD_GAE_LIB := google_appengine

test: setup clean integrations

setup-local:
	sh bootstrap-gae.sh $(LOCAL_GAE_LIB)

setup-build:
	sh bootstrap-gae.sh $(BUILD_GAE_LIB)

clean:
	find . -name "*.py[co]" -delete

deps:
	pip install -Ur requirements.txt

unit:
	nosetests --logging-leve=ERROR

integrations:
	nosetests --logging-leve=ERROR -a slow --with-coverage --cover-package=trajectory

build:
	nosetests --with-coverage --cover-package=trajectory
