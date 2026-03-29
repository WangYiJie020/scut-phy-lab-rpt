.DEFAULT_GOAL := all

LATEX := xelatex
LATEX_FLAGS := -interaction=nonstopmode -halt-on-error -recorder

REPORTS := $(sort $(patsubst %/,%,$(dir $(wildcard */main.tex))))
OUTPUTS := $(REPORTS:%=output/%.pdf)
DEPS := $(wildcard $(REPORTS:%=build/%/deps.mk))

.PHONY: all clean distclean $(REPORTS)

all: $(OUTPUTS)

$(REPORTS): %: output/%.pdf

-include $(DEPS)

output/%.pdf: %/main.tex Makefile | output
	@mkdir -p build/$*
	@cd $* && $(LATEX) $(LATEX_FLAGS) -output-directory=../build/$* main.tex
	@cd $* && $(LATEX) $(LATEX_FLAGS) -output-directory=../build/$* main.tex
	@$(MAKE) --no-print-directory build/$*/deps.mk
	@cp build/$*/main.pdf $@

build/%/deps.mk: build/%/main.fls Makefile
	@mkdir -p $(dir $@)
	@awk -v root='$(CURDIR)/' -v target='output/$*.pdf' '\
		function norm(path, parts, n, i, seg, out) { \
			delete stack; \
			n = split(path, parts, "/"); \
			depth = 0; \
			for (i = 1; i <= n; i++) { \
				seg = parts[i]; \
				if (seg == "" || seg == ".") continue; \
				if (seg == "..") { \
					if (depth > 0) depth--; \
					continue; \
				} \
				stack[++depth] = seg; \
			} \
			out = ""; \
			for (i = 1; i <= depth; i++) out = out (i == 1 ? "" : "/") stack[i]; \
			return out; \
		} \
		/^PWD / { pwd = substr($$0, 5); next } \
		BEGIN { printf "%s:", target } \
		/^INPUT / { \
			path = substr($$0, 7); \
			if (path !~ /^\//) path = pwd "/" path; \
			if (index(path, root) != 1) next; \
			sub("^" root, "", path); \
			path = norm(path); \
			if (path ~ /^(build|output)\//) next; \
			gsub(/\\/, "\\\\", path); \
			gsub(/ /, "\\ ", path); \
			gsub(/#/, "\\#", path); \
			if (!seen[path]++) printf " %s", path; \
		} \
		END { print "" }' $< > $@

output:
	@mkdir -p $@

clean:
	@rm -rf build

distclean:
	@rm -rf build output
