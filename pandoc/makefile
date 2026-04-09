VERSION=3.9.0.2

single_file: MANUAL.txt
	mkdir -p ../build
	cp $< ../build/pandoc.md
MANUAL.txt: clean
	wget https://raw.githubusercontent.com/jgm/pandoc/$(VERSION)/MANUAL.txt
all: single_file
clean:
	rm -f MANUAL.txt
Clean: clean
update:
	url="$$(curl -sIL -o /dev/null -w "%{url_effective}\n" https://github.com/jgm/pandoc/releases/latest)"; \
	version="$${url##*/}"; \
	sed -i "s/^VERSION=.*/VERSION=$$version/" $(MAKEFILE_LIST)
