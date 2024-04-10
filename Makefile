.PHONY: all obo owl json kgx release

# Directories
CURDUR := $(shell realpath $(PWD))/src/ncbi_gene_pyobo
DATA_DIR := $(CURDUR)/data
RAW_DIR := $(DATA_DIR)/raw
# Release directory
RELEASE_DIR := $(DATA_DIR)/release

# File targets
OBO_FILE := $(RAW_DIR)/ncbigene-obo.obo
OWL_FILE := $(RAW_DIR)/ncbigene-obo.owl
JSON_FILE := $(RAW_DIR)/ncbigene-obo.json
KGX_FILES := $(wildcard $(DATA_DIR)/transformed/*.tsv)

# Default target
all: kgx

# Rule for fetching OBO file
obo: $(OBO_FILE)

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


# Rule for converting OBO to OWL
$(OWL_FILE): $(OBO_FILE)
	robot convert -i $< -o $@

# Rule for converting OWL to JSON
$(JSON_FILE): $(OWL_FILE)
	robot convert -i $< -o $@

# Release target
release: all
	@mkdir -p $(RELEASE_DIR)
	cp $(OBO_FILE) $(OWL_FILE) $(JSON_FILE) $(RELEASE_DIR)
	cp $(KGX_FILES) $(RELEASE_DIR)
	cd $(DATA_DIR) && tar -czf release-$(shell date +%Y-%m-%d).tar.gz release

test:
	echo $(DATA_DIR)