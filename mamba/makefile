PROJECT = mamba
GIT_DIR = git
DOC_DIR = $(GIT_DIR)/docs
SOURCE_DIR = $(DOC_DIR)/source
SPHINX_HTML = $(DOC_DIR)/build/singlehtml/index.html
DOXYGEN_XML = build/doxygen/xml/index.xml
PIXI_RUN = pixi run --manifest-path $(CURDIR)/pixi.toml

DOC_FILES = $(shell find $(SOURCE_DIR) -type f | sort)
API_FILES = $(shell find $(GIT_DIR)/libmamba/include -type f | sort)

.PHONY: single_file all html md txt clean Clean update print-%

single_file: ../build/$(PROJECT).md
../build/$(PROJECT).md: build/$(PROJECT).md
	@mkdir -p $(@D)
	cp -f $< $@

all: single_file html md txt
html: build/$(PROJECT).html
md: build/$(PROJECT).md
txt: build/$(PROJECT).txt

build/$(PROJECT).html: $(SPHINX_HTML)
	@mkdir -p build
	cp -f $< $@

build/$(PROJECT).md: $(SPHINX_HTML)
	@mkdir -p build
	$(PIXI_RUN) pandoc -s -t gfm-raw_html -o $@ $< --extract-media=media --resource-path=$(DOC_DIR)/build/singlehtml

build/$(PROJECT).txt: $(SPHINX_HTML)
	@mkdir -p build
	$(PIXI_RUN) pandoc -s -t plain -o $@ $<

$(SPHINX_HTML): $(DOXYGEN_XML) $(DOC_FILES) makefile pixi.toml
	cd $(DOC_DIR); MAMBA_DEV_DOXYGEN_XML_DIR=$(CURDIR)/build/doxygen/xml $(PIXI_RUN) $(MAKE) singlehtml

$(DOXYGEN_XML): $(DOC_DIR)/Doxyfile $(API_FILES) pixi.toml
	@mkdir -p $(@D)
	cd $(GIT_DIR); (cat docs/Doxyfile; printf '\nINPUT=libmamba/include\nOUTPUT_DIRECTORY=../build/doxygen\nXML_OUTPUT=xml\n') | $(PIXI_RUN) doxygen -

clean:
	rm -rf build media $(DOC_DIR)/build $(DOC_DIR)/xml

Clean: clean
	rm -rf .pixi

update:
	cd $(GIT_DIR); git checkout main; git pull origin main

print-%:
	$(info $* = $($*))
