default:
	@echo No default target

.PHONY: data/raw data/processed clean

data: data/raw data/processed

data/raw: scripts/fetch-oflc-recent-data.py scripts/fetch-oflc-archived-data.py
	mkdir -p $@
	./scripts/fetch-oflc-recent-data.py $@
	./scripts/fetch-oflc-archived-data.py $@

data/processed: data/raw scripts/combine-oflc-data.py
	mkdir -p $@
	./scripts/combine-oflc-data.py data/raw > $@/h2-visa-decisions.csv

clean:
	find $@ -type f -exec rm {} \;
