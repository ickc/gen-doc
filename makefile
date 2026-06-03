.DEFAULT_GOAL = help

CASES = $(patsubst %/,%,$(sort $(dir $(wildcard */makefile */Makefile))))
PRIVATE_SUBMODULES = isambard-docs/git
PRIVATE_CASES = isambard-docs

.PHONY: single_file all clean Clean update update-private help
single_file:  ## Generate single file for each projects
	@for case in $(CASES); do \
		$(MAKE) -C $$case single_file; \
	done
all:  ## Generate all files for each projects
	@for case in $(CASES); do \
		$(MAKE) -C $$case all; \
	done
clean:  ## Clean all projects targets
	@for case in $(CASES); do \
		$(MAKE) -C $$case clean; \
	done
Clean:  ## Clean all projects including everything it generates
	@for case in $(CASES); do \
		$(MAKE) -C $$case Clean; \
	done
# TODO: refactor to handle different default branch for different projects
update:  ## Update all submodules
	git submodule update --init --recursive
	@for case in $(CASES); do \
		$(MAKE) -C $$case update; \
	done
update-private:  ## Initialize and update optional private submodules
	git submodule update --init --checkout --recursive -- $(PRIVATE_SUBMODULES)
	@for case in $(PRIVATE_CASES); do \
		$(MAKE) -C $$case update || exit $$?; \
	done

# modified from https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:  ## print this help message
	@awk 'BEGIN{w=0;n=0}{while(match($$0,/\\$$/)){sub(/\\$$/,"");getline nextLine;$$0=$$0 nextLine}if(/^[[:alnum:]_-]+:.*##.*$$/){n++;split($$0,cols[n],":.*##");l=length(cols[n][1]);if(w<l)w=l}}END{for(i=1;i<=n;i++)printf"\033[1m\033[93m%-*s\033[0m%s\n",w+1,cols[i][1]":",cols[i][2]}' $(MAKEFILE_LIST)

print-%:
	$(info $* = $($*))
