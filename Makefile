.PHONY: all obo owl json kgx release

# Directories
CURDUR := $(shell realpath $(PWD))/src/ncbi_gene_pyobo
DATA_DIR := $(CURDUR)/data
RAW_DIR := $(DATA_DIR)/raw
# Release directory
RELEASE_DIR := $(DATA_DIR)/release

# File targets
OBO_FILE := $(RAW_DIR)/ncbigene-full-obo.obo
EDITED_OBO_FILE := $(RAW_DIR)/ncbigene-full-obo-edit.obo
OWL_FILE := $(RAW_DIR)/ncbigene-full-obo.owl
JSON_FILE := $(RAW_DIR)/ncbigene-full-obo.json
KGX_FILES := $(wildcard $(DATA_DIR)/transformed/*.tsv)

# Default target
all: kgx

# Rule for fetching OBO file
obo: $(OBO_FILE)

# Rule for editing OBO file
edit: $(EDITED_OBO_FILE)

# Rule for converting OBO to OWL
owl: $(OWL_FILE)

# Rule for converting OWL to JSON
json: $(JSON_FILE)

# Rule for KGX transformation
kgx: $(JSON_FILE)
	ncbi-gene transform

# Pattern rule for creating files
$(RAW_DIR)/%:
	@mkdir -p $(@D)
	touch $@

# Rule for getting OBO file
$(OBO_FILE):
	if [ ! -f $(OBO_FILE) ]; then \
		poetry run ncbi-gene get-obo; \
	fi

# Remove unwanted \ characters [https://github.com/fastobo/fastobo-py/issues/342]
$(EDITED_OBO_FILE): $(OBO_FILE)
	sed 's/def: "\\\\\(.*\)\\\\\\\\\\\\" \[\]/def: "\1" []/' $(OBO_FILE) > $(EDITED_OBO_FILE)

# Rule for converting OBO to OWL using fastobo
$(OWL_FILE): $(EDITED_OBO_FILE)
	if [ ! -f $(OWL_FILE) ]; then \
		poetry run ncbi-gene convert $< -o $@; \
	fi

# Rule for converting OBO to JSON using fastobo
$(JSON_FILE): $(EDITED_OBO_FILE)
	if [ ! -f $(JSON_FILE) ]; then \
		poetry run ncbi-gene convert $< -o $@; \
	fi

# Release target
release: all
	@mkdir -p $(RELEASE_DIR)
	# Make tar file for .obo
	tar -czf $(RELEASE_DIR)/ncbigene-full-obo-$(shell date +%Y-%m-%d).tar.gz -C $(dir $(OBO_FILE)) $(notdir $(OBO_FILE))
	# Make tar file for all .tsv files
	tar -czf $(RELEASE_DIR)/kgx-$(shell date +%Y-%m-%d).tar.gz -C $(DATA_DIR)/transformed/ *.tsv


test:
	echo $(DATA_DIR)