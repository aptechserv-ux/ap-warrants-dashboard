#!/usr/bin/env python3
"""
exceltojsonconvertor.py
------------------------------------------------------------------
Converts "Out of State Warrants_CCTNS.xlsx" (the DGP Desk No. 85 CCTNS
export) into warrants_data.json, in the exact field schema used by
index.html's FIELDS array, so it can be loaded straight into the app
via the "Seed Database" button (or auto-seed-on-empty).

Usage:
    pip install openpyxl
    python3 exceltojsonconvertor.py "Out of State Warrants_CCTNS.xlsx" warrants_data.json

Re-run this whenever the source Excel is refreshed with new/updated
warrant records.
------------------------------------------------------------------
"""
import sys
import json
import re
import datetime

try:
    import openpyxl
except ImportError:
    openpyxl = None

# Column order exactly as exported from CCTNS (0-indexed). "Column 3" is an
# artifact of the source export's header row -- it actually holds the
# Police Unit / Commissionerate name, not a generic column.
SOURCE_COLUMNS = [
    "slNo", "range", "policeUnit", "policeStation", "crimeNoYear", "cctnsId",
    "court", "courtCaseNo", "warrantType", "warrantNo", "warrantDate",
    "sectionsOfLaw", "categoryOfCase", "nameOfPerson", "alias", "fatherSpouseName",
    "dobAge", "gender", "mobileNo", "photographAvailable", "idParticularsAvailable",
    "originalAddress", "addressStateUT", "addressDistrict", "addressPS",
    "latestKnownAddress", "addressVerificationStatus", "dateLastVerified",
    "cctnsSearchConducted", "cctnsSearchDate", "natgridVerificationRequired",
    "natgridVerificationStatus", "otherDatabaseChecks", "interStatePoliceVerification",
    "currentProbableStateUT", "currentProbableDistrict", "currentProbablePS",
    "locationConfidence", "previousExecutionAttempts", "lastAttemptDate",
    "resultOfLastAttempt", "reasonsForNonExecution", "warrantPendingSince",
    "ageingDays", "ageingBucket", "priority", "interStateTeamRequired",
    "proposedStateCluster", "proposedDistrictCluster", "localPoliceCoordination",
    "teamAssigned", "dateTeamDeployed", "executionStatus", "dateOfExecution",
    "productionTransitStatus", "courtIntimated", "dateCourtIntimated",
    "untraceableEffortsRecorded", "reportFiledBeforeCourt", "reportDate",
    "nextAction", "targetDate", "responsibleOfficer", "shoVerification",
    "unitNodalOfficerVerification", "remarks",
    # Present in the source export but not part of the 66-field proforma used
    # by the app's FIELDS/edit-modal UI. Folded into `remarks` below instead
    # of being dropped, so no information is lost.
    "warrIssuedTo", "warrantLocation",
]

DATE_FIELDS_DMY = {"warrantDate", "warrantPendingSince", "dateLastVerified",
                   "cctnsSearchDate", "lastAttemptDate", "dateTeamDeployed",
                   "dateCourtIntimated", "reportDate", "targetDate"}
DATE_FIELDS_DMY_HMS = {"dateOfExecution"}


def clean(v):
    """Strip whitespace and the stray leading/trailing single-quotes Excel
    adds to force text formatting on numeric-looking IDs (CCTNS ID, Warrant No.)."""
    if v is None:
        return ""
    s = str(v).strip()
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        s = s[1:-1]
    return s.strip()


def to_iso_date(s, with_time=False):
    s = clean(s)
    if not s:
        return ""
    try:
        if with_time:
            s = s.split(" ")[0]
            dt = datetime.datetime.strptime(s, "%d-%m-%Y")
        else:
            dt = datetime.datetime.strptime(s, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return s  # leave as-is if it doesn't match the expected pattern


def compute_ageing(warrant_date_iso):
    if not warrant_date_iso:
        return None, None
    try:
        start = datetime.date.fromisoformat(warrant_date_iso)
    except ValueError:
        return None, None
    days = max(0, (datetime.date.today() - start).days)
    years = days / 365
    if years >= 10:
        bucket = ">10 Years"
    elif years >= 5:
        bucket = "5-10 Years"
    elif years >= 1:
        bucket = "1-5 Years"
    else:
        bucket = "<1 Year"
    return days, bucket


def row_to_record(raw_row):
    rec = {}
    for key, val in zip(SOURCE_COLUMNS, raw_row):
        rec[key] = clean(val)

    for key in DATE_FIELDS_DMY:
        if key in rec:
            rec[key] = to_iso_date(rec[key])
    for key in DATE_FIELDS_DMY_HMS:
        if key in rec:
            rec[key] = to_iso_date(rec[key], with_time=True)

    # Execution status: trim stray tab/whitespace from the CCTNS export
    # (e.g. "NBWs Execution Pending\t") but keep the real department wording.
    rec["executionStatus"] = re.sub(r"\s+", " ", rec.get("executionStatus", "")).strip()

    # Fold the two extra source columns into remarks instead of dropping them.
    extra_bits = []
    if rec.get("warrIssuedTo"):
        extra_bits.append(f"Issued To: {rec['warrIssuedTo']}")
    if rec.get("warrantLocation"):
        extra_bits.append(f"Location: {rec['warrantLocation']}")
    if extra_bits:
        prefix = "[" + "; ".join(extra_bits) + "]"
        rec["remarks"] = (prefix + " " + rec["remarks"]).strip() if rec.get("remarks") else prefix
    rec.pop("warrIssuedTo", None)
    rec.pop("warrantLocation", None)

    # Recompute ageing from the real warrant date where possible -- the
    # source export's own Ageing (Days)/Ageing Bucket columns are mostly
    # blank, and index.html recomputes this at load time anyway.
    days, bucket = compute_ageing(rec.get("warrantDate", ""))
    if days is not None:
        rec["ageingDays"] = days
        rec["ageingBucket"] = bucket

    try:
        rec["slNo"] = int(float(rec["slNo"])) if rec.get("slNo") else None
    except (ValueError, TypeError):
        pass

    return rec


def load_rows_from_xlsx(path):
    if openpyxl is None:
        raise RuntimeError("openpyxl is required to read .xlsx directly: pip install openpyxl")
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb.active
    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue  # header
        if row is None or all(c is None for c in row):
            continue
        rows.append(list(row))
    return rows


def load_rows_from_csv(path):
    import csv
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # header
        return [row for row in reader]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 exceltojsonconvertor.py <source.xlsx|source.csv> [out.json]")
        sys.exit(1)

    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "warrants_data.json"

    if src.lower().endswith(".csv"):
        rows = load_rows_from_csv(src)
    else:
        rows = load_rows_from_xlsx(src)

    records = [row_to_record(r) for r in rows]
    records = [r for r in records if r.get("nameOfPerson") or r.get("cctnsId")]

    with open(out, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(records)} warrant records -> {out}")


if __name__ == "__main__":
    main()
