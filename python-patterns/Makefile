.PHONY: all single_file pdf epub html clean Clean
single_file: build/python-patterns.md
	cp -f $< ../build/python-patterns.md
all: single_file pdf epub html
build/python-patterns.md: build/python-patterns.html
	pandoc -s -t gfm-raw_html -o $@ $<
pdf: build/python-patterns.pdf
build/python-patterns.pdf:
	@mkdir -p build
	cd git; $(MAKE) latexpdf
	cp -f git/_build/latex/PythonPatterns.pdf build/python-patterns.pdf
epub: build/python-patterns.epub
build/python-patterns.epub:
	@mkdir -p build
	cd git; $(MAKE) epub
	cp -f git/_build/epub/PythonPatterns.epub build/python-patterns.epub
html: build/python-patterns.html
build/python-patterns.html:
	@mkdir -p build
	cd git; $(MAKE) singlehtml
	cp -f git/_build/singlehtml/index.html build/python-patterns.html
clean:
	rm -rf git/_build
Clean: clean
	rm -rf build
update:
	cd git; git pull
