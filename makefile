.DEFAULT_GOAL = help

CASES = $(patsubst ./%,%,$(shell find . -mindepth 1 -maxdepth 1 \! -path './.*' -type d))

.PHONY: single_file clean update help
single_file:  ## Generate single file for each projects
	@for case in $(CASES); do \
		cd $$case; \
		$(MAKE) single_file; \
		cd ..; \
	done
all:  ## Generate all files for each projects
	@for case in $(CASES); do \
		cd $$case; \
		$(MAKE) all; \
		cd ..; \
	done
clean:  ## Clean all projects
	@for case in $(CASES); do \
		cd $$case; \
		$(MAKE) clean; \
		cd ..; \
	done
# TODO: refactor to handle different default branch for different projects
update:  ## Update all submodules
	git submodule update --init --recursive
	git submodule foreach git checkout main
	git submodule foreach git pull origin main

# modified from https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:  ## print this help message
	@awk 'BEGIN{w=0;n=0}{while(match($$0,/\\$$/)){sub(/\\$$/,"");getline nextLine;$$0=$$0 nextLine}if(/^[[:alnum:]_-]+:.*##.*$$/){n++;split($$0,cols[n],":.*##");l=length(cols[n][1]);if(w<l)w=l}}END{for(i=1;i<=n;i++)printf"\033[1m\033[93m%-*s\033[0m%s\n",w+1,cols[i][1]":",cols[i][2]}' $(MAKEFILE_LIST)

print-%:
	$(info $* = $($*))
