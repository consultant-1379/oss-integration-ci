"""Module for certificate mgt operations."""
import logging
import os
from datetime import datetime, timezone
import OpenSSL

LOG = logging.getLogger(__name__)


# pylint: disable=too-many-locals,too-many-branches,too-many-statements
def report_certificate_expiry(repo_path, warn_days, report_name, filters, excludes):  # noqa: C901
    """
    Check certificates in repo_path and writes out report (HTML) summary.

    Input:
        repo_path: File path to repo root for certificate scanning
        warn_days: Number of days from current day for expiry warning
        report_name: Title for summary report
        filters: CSV of path keywords to include in scan
        excludes: CSV of path keywords to exclude from scan

    Output:
        Summary report (HTML) with details about certificate expiry
    """
    LOG.info("Called report_certificate_expiry")
    filters = filters.split(",")
    excludes = excludes.split(",")
    LOG.info("Path includes: %s", filters)
    LOG.info("Path excludes: %s", excludes)
    error_cert_files = []
    expiring_cert_files = []
    expired_cert_files = []
    cert_files = []
    ext = tuple([".pem", ".crt"])
    # pylint: disable=too-many-nested-blocks
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(ext) and "intermediate-ca" not in file and \
               "root" not in file and "DigiCert" not in file:
                if "all" in filters:
                    cert_files.append(os.path.join(root, file))
                else:
                    for filter_keyword in filters:
                        if filter_keyword.lower() in os.path.join(root, file).lower():
                            cert_files.append(os.path.join(root, file))
                            continue
    updated_cert_files = []
    for cert_file in cert_files:
        found_entry = False
        for exclude_entry in excludes:
            if exclude_entry.strip() != "" and exclude_entry.lower() in cert_file.lower():
                found_entry = True
        if not found_entry:
            updated_cert_files.append(cert_file)

    # Process cert files
    for cert_file in updated_cert_files:
        LOG.info("Checking file: %s", cert_file)
        try:
            with open(cert_file, "r", encoding="utf-8") as cert_file_handle:
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_file_handle.read())
        # pylint: disable=broad-except
        except Exception:
            cert_file = "/".join(cert_file.strip("/").split('/')[1:])
            error_cert_files.append(cert_file)
            continue
        cert_ts = x509.get_notAfter()
        timestamp = cert_ts.decode('utf-8')
        now = datetime.now(timezone.utc)
        cert_expiry_date = datetime.strptime(timestamp, '%Y%m%d%H%M%S%z')
        time_delta = cert_expiry_date - now
        LOG.info("Expiry: %s", cert_expiry_date.date().isoformat())
        time_days_left = time_delta.days
        LOG.info("Days remaining: %s", time_days_left)
        cert_file = "/".join(cert_file.strip("/").split('/')[1:])
        if int(time_days_left) < 0:
            expired_cert_files.append(cert_file)
        elif int(time_days_left) <= int(warn_days):
            expiring_cert_files.append([cert_file, time_days_left])

    # Write out summary report
    with open(f"/pipeline-mgt-scripts/output-files/report_{report_name}.html", "w", encoding="utf-8") as output_report:
        output_report.write(f"<h1>Repo {report_name} certificate summary</h1>")
        output_report.write("<ul>")
        output_report.write(f"<li><b>Expiry check</b>: within {warn_days} days</li>")
        output_report.write(f"<li><b>Path include filters</b>: {filters}</li>")
        output_report.write(f"<li><b>Path exclude filters</b>: {excludes}</li>")
        output_report.write("</ul>")
        if len(expiring_cert_files) > 1:
            output_report.write(f"<h3>Expiring (within {warn_days} days):</h3>")
            output_report.write("<ul>")
            sorted_expiring_list = sorted(expiring_cert_files, key=lambda d: d[1])
            for expiring_cert_file in sorted_expiring_list:
                cert_file = expiring_cert_file[0]
                time_days_left = expiring_cert_file[1]
                LOG.info("*** Expiring cert ==> %s", cert_file)
                output_report.write(f"<li>{cert_file} (days left: {time_days_left})</li>")
            output_report.write("</ul>")
        if len(expired_cert_files) > 1:
            output_report.write("<h3>Expired:</h3>")
            output_report.write("<ul>")
            for expired_cert_file in expired_cert_files:
                LOG.info("*** EXPIRED cert ==> %s", expired_cert_file)
                output_report.write(f"<li>{expired_cert_file}</li>")
            output_report.write("</ul>")
        if len(error_cert_files) > 1:
            output_report.write("<h3>Errors (unable to process):</h3>")
            output_report.write("<ul>")
            for error_cert_file in error_cert_files:
                LOG.info("*** ERROR: Unable to process cert ==> %s", error_cert_file)
                output_report.write(f"<li>{error_cert_file}</li>")
            output_report.write("</ul>")
