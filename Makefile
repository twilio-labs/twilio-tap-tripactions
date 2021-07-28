
.PHONY: test setup-environment


test:
	coverage run --source=./ --omit=env/*,test*,setup.py -m unittest discover && coverage report -m

setup-environment:
	rm -rf env || true
	python3 -m venv env
	. ./env/bin/activate && pip3 install -r requirements.txt

