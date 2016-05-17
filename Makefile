default:
	@echo No default target

.PHONY: recent-data archived-data data/raw data/processed clean

data: clean data/raw data/processed

recent-data:
	mkdir -p data/raw
	./scripts/fetch-oflc-recent-data.py data/raw

archived-data:
	mkdir -p data/raw
	./scripts/fetch-oflc-archived-data.py data/raw

data/raw: recent-data archived-data

data/processed: scripts/combine-oflc-data.py
	mkdir -p $@
	./scripts/combine-oflc-data.py data/raw > $@/H-2-certification-decisions.csv

clean:
	find data/raw -type f -exec rm {} \;
