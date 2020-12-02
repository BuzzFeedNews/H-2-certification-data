# H-2 Visa Certification Data

This repository contains [data](data/) tracking the U.S. Department of Labor's H-2 visa certification decisions.

## Data Sources

The [raw data](data/raw) come from the Department of Labor's Office of Foreign Labor Certification (OFLC). The OFLC posts [recent data here](http://www.foreignlaborcert.doleta.gov/performancedata.cfm). Historical data can be found at [flcdatacenter.com](http://www.flcdatacenter.com/). 

## Time-frame

H-2 visas come in two types: H-2A for agricultural workers and H-2B for non-agricultural unskilled workers. The OFLC data source covers __H-2A decisions since FY2006__ and __H-2B decisions since FY2000__. The most recent data, for both visa types, includes data  __through FY2020 Q4__, which concluded on September 30, 2020.

## Standardized Data

Over the years, the OFLC has slightly changed the H-2 visa decision data it publishes, and the names of various fields. The code in this repository standardizes the field names and other bits of nomenclature. It also standardizes state abbreviations and consolidates information about visa agents. For simplicity's sake, it also ignores some fields. A full list of fields can be found in the raw data, or in the data dictionaries available at the sources above.

The fields in the standardized data are as follows:

- `case_no`: The OFLC-assigned case number.
- `visa_type`: "H-2A" or "H-2B".
- `fy`: The fiscal year of the most recent OFLC decision/progress on the case.
- `last_event_date`: The date of the most recent OFLC decision/progress on the case.
- `case_status`: The status of the case; typically a variation on "CERTIFIED", "DENIED", "WITHDRAWN", et cetera.
- `n_requested`: The number of workers/visas certified.
- `n_certified`: The number of workers/visas certified.
- `is_certified`: `True`/`False`; a standardization of the `case_status` field.
- `certification_begin_date` / `certification_begin_date`: "Actual date granted to an employer indicating when the need for the foreign workers to perform agricultural services or labor is expected to [begin / end]." Unavailable for H-2B data prior to FY2007.
- `job_title`: The job title listed by the employer.
- `employer_name`: The name of the employer applying for certification; converted to all-caps.
- `employer_state`: The state the employer listed.
- `employer_city`: The city the employer listed.
- `employer_address_1`: The first line of the address the employer listed.
- `employer_address_2`: The second line of the address the employer listed.
- `employer_postal_code`: The postal code the employer listed.
- `agent_name`: The name of the agent or attorney filing the application for the employer. Some years of data include multiple columns related to visa agents; the standardized field combines these fields, separating them by a `:`.
- `organization_flag`: Various types of organizations — including sole employers and joint employers — can apply for visa certifications. This field tracks OFLC's categorizations. Only available for H-2A decisions.
- `is_duplicate`: `True`/`False`/`null`: This derived value will be `True` — indicating that this row corresponds a sub-application of a [joint employer's "master application"](http://www.foreignlaborcert.doleta.gov/h_2a_details.cfm) — if (a) `visa_type` is "H-2A", (b) the `organization_flag` is blank, and (c) comes from fiscal year 2008 or later. H-2A data from FY 2006 and FY 2007 do not contain a `organization_flag` field. For these records, and H-2B records, `is_duplicate` will be `null`.

To download the standardized data, [click here](data/processed/h2-visa-decisions.csv?raw=true).

## Reproducing the Data

You can run the data-fetchers and data-standardizer yourself. To do so, you'll need the following requirements:

- Python 3
- The Python libraries listed in `requirements.txt`. This can be installed by running `pip install -r requirements.txt`
- [mdbtools](https://www.codeenigma.com/community/blog/using-mdbtools-nix-convert-microsoft-access-mysql), for extracting the older files. On OSX, you can install `mdbtools` with Homebrew by running `brew install mdbtools`. On Ubuntu, you can run `sudo apt-get install -y mdbtools-dev`.

To re-run the full workflow, execute the following command from this repository's root directory: `make data`

## Questions?

Email Jeremy Singer-Vine at jeremy.singer-vine@buzzfeed.com.
