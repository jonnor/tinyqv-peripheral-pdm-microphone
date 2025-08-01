.POSIX:

ENVIRONMENT = PATH=$$(realpath venv/bin):$$PATH PDK=sky130A

all:

distclean:
	rm -rf tt venv

harden:
	$(ENVIRONMENT) venv/bin/python tt/tt_tool.py --harden

png:
	$(ENVIRONMENT) venv/bin/python tt/tt_tool.py --create-png

tt:
	git clone -b ttsky25a https://github.com/TinyTapeout/tt-support-tools tt
	python3 -m venv venv
	venv/bin/pip install -r tt/requirements.txt
	venv/bin/pip install https://github.com/TinyTapeout/libparse-python/releases/download/0.3.1-dev1/libparse-0.3.1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
	$(ENVIRONMENT) venv/bin/pip install openlane==2.2.9
	$(ENVIRONMENT) venv/bin/python tt/tt_tool.py --create-user-config

.PHONY: all distclean harden png tt
