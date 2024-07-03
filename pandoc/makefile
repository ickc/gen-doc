VERSION=3.2.1

single_file: MANUAL.txt
MANUAL.txt:
	wget https://raw.githubusercontent.com/jgm/pandoc/$(VERSION)/MANUAL.txt
	@echo "single file is ready at $$(realpath $<)"
all: single_file
clean:
	rm -f MANUAL.txt
