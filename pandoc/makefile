VERSION=3.2.1

single_file: MANUAL.txt
	@echo "single file is ready at $$(realpath $<)"
MANUAL.txt:
	wget https://raw.githubusercontent.com/jgm/pandoc/$(VERSION)/MANUAL.txt
all: single_file
clean:
	rm -f MANUAL.txt
Clean: clean
update:
	url="$$(curl -sIL -o /dev/null -w "%{url_effective}\n" https://github.com/jgm/pandoc/releases/latest)"; \
	version="$${url##*/}"; \
	sed -i "s/^VERSION=.*/VERSION=$$version/" $(MAKEFILE_LIST)
