.PHONY: single_file

single_file: ../build/spack.txt
../build/spack.txt: build/spack.txt
		cp -f $< $@

.PHONY: all pdf html epub md txt
all: single_file pdf html epub md txt
pdf: build/spack.pdf
html: build/spack.html
epub: build/spack.epub
md: build/spack.md
txt: build/spack.txt

build/spack.pdf: git/lib/spack/docs/_build/latex/spack.pdf
	@mkdir -p build
	@cp -f $< $@
build/spack.html: git/lib/spack/docs/_build/singlehtml/index.html
	@mkdir -p build
	cp -f $< $@
build/spack.epub: git/lib/spack/docs/_build/epub/spack.epub
	@mkdir -p build
	cp -f $< $@
build/spack.md: git/lib/spack/docs/_build/singlehtml/index.html
	@mkdir -p build
	pandoc -s -t gfm-raw_html -o $@ $<
build/spack.txt: git/lib/spack/docs/_build/singlehtml/index.html
	@mkdir -p build
	pandoc -s -t plain -o $@ $<

git/lib/spack/docs/_build/latex/spack.pdf:
	cd git/lib/spack/docs; pixi run $(MAKE) latexpdf SPHINXOPTS='-D latex_engine=lualatex'
git/lib/spack/docs/_build/singlehtml/index.html:
	cd git/lib/spack/docs; pixi run $(MAKE) singlehtml
git/lib/spack/docs/_build/epub/spack.epub:
	cd git/lib/spack/docs; pixi run $(MAKE) epub

.PHONY: clean Clean update
clean:
	rm -rf git/lib/spack/docs/_build
Clean: clean
	rm -rf build
update:
	cd git; git checkout master; git pull origin master
