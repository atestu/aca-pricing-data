PYTHON = /usr/bin/env python3

setup:
	${PYTHON} -m pip install -r requirements.txt

run:
	${PYTHON} main.py