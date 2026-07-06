.PHONY: build test preview clean all

all: build test preview

build:
	python3 tools/build.py

test:
	python3 -m pytest tests/ -q

preview:
	python3 tools/preview.py

clean:
	rm -rf fonts/*.ttf docs/preview-*.png
