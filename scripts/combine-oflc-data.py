#!/usr/bin/env python
import pandas as pd
import namestand
import us
import glob
import sys, os
import itertools
import re
import six
flatten = lambda x: list(itertools.chain.from_iterable(x))

t = namestand.translator
standardizer = namestand.combine([
    namestand.downscore,
    t(re.compile(r"address(\d)"), r"address_\1"),
    t(re.compile(r"(number|nbr)"), r"no"),
    t(re.compile(r"(visa_type|visa_class|case_type)"), "visa_type"),
    t("recent_decision_date", "last_event_date"),
    t("decision_date", "last_event_date"),
    t("last_sig_event", "case_status"),
    t("case_num", "case_no"),
    t("emp_", "employer_"),
    t("num_aliens", "n_requested"),
    t("no_workers_requsted", "n_requested"),
    t("no_workers_requested", "n_requested"),
    t("no_workers_requested", "n_requested"),
    t("no_workers_certified", "n_certified"),
    t("workers_requested", "n_requested"),
    t("workers_certified", "n_certified"),
    t("npc_submitted_date", "case_received_date"),
    t("att_agent", "agent_attorney"),
    t("att_", "agent_attorney_"),
    t("occ_title", "job_title"),
    t("alien_work", "worksite"),
    t("worksite_location", "worksite"),
    t(re.compile("^(agent_attorney_firm|lawfirm_name)$"), "agent_attorney_firm_name"),
])

year_pat = re.compile(r"FY(\d+)")
def get_fy_from_path(path):
    last = path.split("/")[-1]
    found = int(re.search(year_pat, last).group(1))
    fy = found if found > 99 else 2000 + found
    return fy

visa_type_pat = re.compile(r"H-?2(A|B)")
def get_visa_type_from_path(path):
    last = path.upper().split("/")[-1]
    v_type = "H-2" + re.search(visa_type_pat, last).group(1)
    return v_type

def parse_date(x):
    dt = pd.to_datetime(x, errors="coerce")
    if pd.isnull(dt): return dt
    return dt.strftime("%Y-%m-%d")

def read_file(path):
    if path[-3:] == "csv":
        raw = pd.read_csv(path, low_memory = False)
    else:
        raw = pd.read_excel(path)

    renamed = raw.rename(columns=dict(zip(raw.columns, standardizer(raw.columns))))

    renamed = renamed[renamed["case_no"].notnull()].copy()
    renamed["fy"] = get_fy_from_path(path)
    renamed["visa_type"] = get_visa_type_from_path(path)
    return renamed

def read_all(src_dir):
    paths = glob.glob(os.path.join(src_dir, "*"))
    dfs = map(read_file, paths)
    return dfs

def get_state_abbr(x):
    if isinstance(x, six.string_types) and len(x) > 2:
        found = us.states.lookup(x)
        if found != None: return found.abbr
        else: return x
    else:
        return x

def combine(src_dir):
    # Read in all spreadsheets
    dfs = read_all(src_dir)
    decisions = pd.concat(dfs).reset_index(drop=True)

    # Normalize worksite_state and employer_state to postal abbreviations
    decisions["employer_state"] = decisions["employer_state"].apply(get_state_abbr)
    decisions["worksite_state"] = decisions["worksite_state"].apply(get_state_abbr)

    decisions["certification_begin_date"] = decisions["certification_begin_date"].apply(parse_date)
    decisions["certification_end_date"] = decisions["certification_end_date"].apply(parse_date)
    # Note: FY2006 H-2A data has no decision date / last event date.
    decisions["last_event_date"] = decisions["last_event_date"].apply(parse_date)
 
    double_colon = r":{2,}"
    end_colon = r"(^:)|(:$)"
    # Glob all agent/attorney names into one string

    agent_name_smushed = decisions[[
        "agent_attorney_first",
        "agent_attorney_last",
    ]].fillna("").apply(lambda x: " ".join(field.strip() for field in x), axis=1)

    decisions["agent_attorney_name"] = decisions["agent_attorney_name"].fillna(agent_name_smushed)

    decisions["agent_name"] = decisions[[
        "agent_attorney_firm_name",
        "agent_attorney_name",
    ]].fillna("")\
        .astype(str)\
        .applymap(lambda x: x.strip())\
        .apply(":".join, axis=1)\
        .apply(lambda x: re.sub(double_colon, ":", x))\
        .apply(lambda x: re.sub(end_colon, "", x))

    # Uppercase addresses and cities
    for_upping = [ "employer_name", "employer_address_1", "employer_address_2",
        "employer_city", "agent_name", "job_title" ]
    decisions[for_upping] = decisions[for_upping].fillna("")\
        .applymap(lambda x: six.text_type(x).upper().strip())

    # Classify certifications and expired certifications
    def is_certified(x):
        return "CERTIF" in x

    decisions["case_status"] = decisions["case_status"].fillna("").str.upper()
    decisions["is_certified"] = decisions["case_status"]\
        .apply(is_certified).astype(bool)

    # Fill in n_certified data, if missing, based on other columns
    decisions["n_certified"] = (decisions["n_certified"]\
        .fillna(decisions["n_requested"]) * decisions["is_certified"])\
        .fillna(0)\
        .astype(int)

    # Don't count as certified in the (relatively rare) scenario
    # that the number of workers certified is null or 0
    decisions["is_certified"] = decisions["n_certified"] > 0

    # If an entry includes one these organization flags,
    # it's a duplicate/umbrella application 
    decisions.loc[(
        (decisions["visa_type"] == "H-2A") &
        (decisions["fy"] >= 2008)
    ), "is_duplicate"] = (
        (decisions["organization_flag"].fillna("") == "") &
        (decisions["visa_type"] == "H-2A")
    )

    core_cols = [
        "case_no",
        "visa_type",
        "fy",
        "last_event_date",
        "case_status",
        "n_requested",
        "n_certified",
        "is_certified",
        "certification_begin_date",
        "certification_end_date",
        "job_title",
        "employer_name",
        "employer_state",
        "employer_city",
        "employer_address_1",
        "employer_address_2",
        "employer_postal_code",
        "worksite_state",
        "worksite_city",
        "agent_name",
        "organization_flag",
        "is_duplicate",
    ]
    return decisions[core_cols].sort_values([
        "fy",
        "visa_type",
        "last_event_date"
    ])

if __name__ == "__main__":
    combined = combine(sys.argv[1])
    combined.to_csv(sys.stdout, index=False, encoding="utf-8")
