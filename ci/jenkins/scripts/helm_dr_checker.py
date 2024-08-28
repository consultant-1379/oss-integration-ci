"""This module contains functionality to generate the DR Compliance Report."""
import os
import os.path
from os.path import exists
import re
import sys
from datetime import date, datetime
import requests

# Variables
# Jenkins
JENKINS_JOB_URL = os.environ["JOB_URL"]
JENKINS_BUILD_NUMBER = os.environ["BUILD_NUMBER"]

# ADP helm dr enforcements
USERNAME = os.environ.get("SELI_ARTIFACTORY_REPO_USER")
PASSWORD = os.environ.get("SELI_ARTIFACTORY_REPO_PASS")
URL_PATH = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local"
URL_NAME = "/monitoring/DR_Enforcements/ADP_DR_Enforcement_Data.csv"
FULL_URL = URL_PATH + URL_NAME
HELM_DR_ENFORCEMENT_DATA = []

# Helm dr check report data
HELM_DR_CHECK_REPORT = ".bob/design-rule-check-report.xml"
HELM_DR_CHECK_REPORT_DATA = []
HELM_DR_CHECK_REPORT_DATA_PASSED = []
HELM_DR_CHECK_REPORT_DATA_FAILED = []
HELM_DR_CHECK_REPORT_DATA_WARNING = []
HELM_DR_CHECK_REPORT_DATA_DISABLED = []
HELM_DR_CHECK_REPORT_DATA_SKIP_FAIL = []
HELM_DR_CHECK_REPORT_DATA_SKIP_PASS = []
HELM_DR_CHECK_REPORT_DATA_DRAFT = []
HELM_DR_CHECK_REPORT_DATA_EXEMPT = []

# Helm dr check report link
HELM_DR_CHECK_REPORT_HTML = "design-rule-check-report.html"
HELM_DR_CHECK_REPORT_LINK_TEMPLATE = "<a href='{job_url}/{build_number}/artifact/.bob/{report_name}'>{report_name}</a>"
helm_dr_check_report_link = HELM_DR_CHECK_REPORT_LINK_TEMPLATE.format(
    job_url=JENKINS_JOB_URL,
    build_number=JENKINS_BUILD_NUMBER,
    report_name=HELM_DR_CHECK_REPORT_HTML,
)

# Helm dr compliance
HELM_DR_COMPLIANCE_REPORT = ".bob/design-rule-compliance-report.html"
HELM_DR_COMPLIANCE_DATA = []
BUILD_NOTIFICATION = (
    "<table>"
    + "<tr>"
    + "<td>section_1</td>"
    + "</tr>"
    + "</table>"
    + "<p></p>"
    + "<table>"
    + "<tr>"
    + "<td>section_2</td>"
    + "</tr>"
    + "</table>"
    + "<p></p>"
    + "<table>"
    + "<tr>"
    + "<td>section_3</td>"
    + "</tr>"
    + "</table>"
)


# Functions
def validate_helm_dr_compliance():
    """Validate that the design-rule-report.xml exists within the workspace."""
    if exists(HELM_DR_CHECK_REPORT):
        execute_helm_dr_compliance_check()
    else:
        error_message_template = "{report} is not available in the workspace! Skipping the Helm DR compliance check!"
        error_message = error_message_template.format(report=HELM_DR_CHECK_REPORT)
        print(error_message)
        sys.exit("Error")


def execute_helm_dr_compliance_check():
    """Create the design-rule-compliance-report.html file."""
    fetch_helm_dr_enforcements()
    fetch_helm_dr_check_report_data()
    fetch_helm_dr_verdicts()
    fetch_helm_dr_compliance_data()
    fetch_helm_dr_statistics()
    fetch_helm_dr_summary()
    save_helm_dr_compliance_results()


# Fetch helm dr enforcement data from the artifactory
def fetch_helm_dr_enforcements():
    """Format Helm Design Rule Enforcements within design-rule-compliance-report.html file."""
    results = ""
    response = requests.get(FULL_URL, auth=(USERNAME, PASSWORD), timeout=60)

    if response.status_code == 200:
        results = response.text.replace("\r", "")
    else:
        error_message_template = "Error fetching {report} from the Artifactory! Skipping the Helm DR compliance check!"
        error_message = error_message_template.format(report=FULL_URL)
        print(error_message)
        sys.exit("Error")

    if results:
        for line in results.split("\n"):
            if line:
                HELM_DR_ENFORCEMENT_DATA.append(line.split(","))

        if HELM_DR_ENFORCEMENT_DATA:
            HELM_DR_ENFORCEMENT_DATA.pop(0)  # Exclude CSV header


# Fetch helm dr check report data from the jenkins workspace
def fetch_helm_dr_check_report_data():
    """Format Helm Design Rule Report file within the workspace (.bob/design-rule-report.xml)."""
    input_string = ""
    input_data = []

    with open(HELM_DR_CHECK_REPORT, encoding="utf-8") as input_file:  # .bob/design-rule-check-report.xml
        input_string = input_file.read().split("</tr>")
    input_file.close()

    if input_string:
        for line in input_string:
            line = line.replace("\n", "").replace(",", "").replace("</td>", ",")
            line = re.sub("<.*?>", "", line)  # Exclude HTML tags
            line = line[:-1]  # Exclude trailing comma
            if line:
                data = line.split(",")
                input_data.append(data)

    if input_data:
        for data in input_data:
            if data[0] and data[1] and data[2] and data[3]:
                HELM_DR_CHECK_REPORT_DATA.append(data)


# Compare helm dr enforcement and report data
# flake8: noqa: C901
# pylint: disable=too-many-branches,too-many-locals,too-many-nested-blocks,global-statement
def fetch_helm_dr_compliance_data():
    """Format Helm Design Rule Compliance Data within design-rule-compliance-report.html file."""
    global BUILD_NOTIFICATION
    data_position = "section_1"
    data_template = (
        "<tr style='text-align: left;'>"
        + "<td>{tag}&emsp;</td>"
        + "<td>{key}&emsp;</td>"
        + "<td>{status}&emsp;</td>"
        + "<td>{checker_tool}&emsp;</td>"
        + "<td>{enforcement_date}&emsp;</td>"
        + "<td>{remaining_days}&emsp;</td>"
        + "<td style='background-color: {verdict_color};'>{verdict}&emsp;</td>"
        + "</tr>"
    )

    if HELM_DR_ENFORCEMENT_DATA:
        for data in HELM_DR_ENFORCEMENT_DATA:
            adp_dr_jira_link = "<a href='https://eteamproject.internal.ericsson.com/browse/{key}'>{key}</a>"
            adp_dr_jira_key = adp_dr_jira_link.format(key=data[0])
            adp_dr_tag = data[1]
            adp_dr_status = data[2]
            adp_dr_checker_tool = data[3]
            adp_dr_planned_enforcement_date = data[4]
            stripped_planned_enforcement_date = datetime.strptime(adp_dr_planned_enforcement_date, "%Y-%m-%d").date()
            remaining_days = (((stripped_planned_enforcement_date) - date.today()).days)
            adp_dr_remaining_days = (str(remaining_days) + " days")

            output_verdict = "-"
            output_verdict_color = "#ffffff" # White

            if HELM_DR_CHECK_REPORT_DATA:
                for report_data in HELM_DR_CHECK_REPORT_DATA:
                    report_dr_verdict = report_data[0]
                    report_dr_tag = report_data[1]

                    if adp_dr_tag == report_dr_tag:
                        output_verdict = report_dr_verdict

                        if output_verdict == "PASS":
                            output_verdict_color = "#008001"  # Green
                        elif output_verdict == "FAILED":
                            output_verdict_color = "#fe0000"  # Red
                        elif output_verdict == "DISABLE":
                            output_verdict_color = "#dfded9"  # Grey
                        elif output_verdict == "WARNING":
                            output_verdict_color = "#ffff01"  # Yellow
                        elif output_verdict == "SKIP_FAIL":
                            output_verdict_color = "#ff5001"  # Orange
                        elif output_verdict == "SKIP_PASS":
                            output_verdict_color = "#7f817b"  # Deep grey
                        elif output_verdict == "DRAFT":
                            output_verdict_color = "#ff00fe"  # Pink
                        elif output_verdict == "EXEMPT":
                            output_verdict_color = "#00ff01"  # Lime green

            data_string = data_template.format(
                tag=adp_dr_tag,
                key=adp_dr_jira_key,
                status=adp_dr_status,
                checker_tool=adp_dr_checker_tool,
                enforcement_date=adp_dr_planned_enforcement_date,
                remaining_days=adp_dr_remaining_days,
                verdict=output_verdict,
                verdict_color=output_verdict_color,
            )
            HELM_DR_COMPLIANCE_DATA.append(data_string)

        if HELM_DR_COMPLIANCE_DATA:
            output_string = (
                "<p><b>ADP Design Rules Notification of Enforcement:</b><br>"
                + "ADP will enforce the following design rules within the next 90 days.<br></p>"
                + "<table>"
                + "<thead>"
                + "<tr style='text-align: left'>"
                + "<th style='color: white; background-color: black;'>DR Tag</th>"
                + "<th style='color: white; background-color: black;'>ADP JIRA&emsp;</th>"
                + "<th style='color: white; background-color: black;'>Status&emsp;</th>"
                + "<th style='color: white; background-color: black;'>DR Checker Tool&emsp;</th>"
                + "<th style='color: white; background-color: black;'>Planned Enforcement Date&emsp;</th>"
                + "<th style='color: white; background-color: black;'>Grace Period Expiration&emsp;</th>"
                + "<th style='color: white; background-color: black;'>Current Helm DR Check Verdict&emsp;</th>"
                + "</tr>"
                + "</thead>"
                + "<tbody>"
            )

            for data in HELM_DR_COMPLIANCE_DATA:
                output_string = output_string + data

            BUILD_NOTIFICATION = BUILD_NOTIFICATION.replace(data_position, output_string)


# Categorize helm DRs by verdicts
# flake8: noqa: C901
# pylint: disable=too-many-branches,global-statement
def fetch_helm_dr_verdicts():
    """Format Helm Design Rule Verdicts within design-rule-compliance-report.html file."""
    if HELM_DR_CHECK_REPORT_DATA:
        for data in HELM_DR_CHECK_REPORT_DATA:
            dr_verdict = data[0]
            dr_tag = data[1]

            if dr_verdict == "PASS":
                HELM_DR_CHECK_REPORT_DATA_PASSED.append(dr_tag)
            elif dr_verdict == "FAILED":
                HELM_DR_CHECK_REPORT_DATA_FAILED.append(dr_tag)
            elif dr_verdict == "DISABLE":
                HELM_DR_CHECK_REPORT_DATA_DISABLED.append(dr_tag)
            elif dr_verdict == "WARNING":
                HELM_DR_CHECK_REPORT_DATA_WARNING.append(dr_tag)
            elif dr_verdict == "SKIP_FAIL":
                HELM_DR_CHECK_REPORT_DATA_SKIP_FAIL.append(dr_tag)
            elif dr_verdict == "SKIP_PASS":
                HELM_DR_CHECK_REPORT_DATA_SKIP_PASS.append(dr_tag)
            elif dr_verdict == "DRAFT":
                HELM_DR_CHECK_REPORT_DATA_DRAFT.append(dr_tag)
            elif dr_verdict == "EXEMPT":
                HELM_DR_CHECK_REPORT_DATA_EXEMPT.append(dr_tag)


# Statistics
# flake8: noqa: C901
def fetch_helm_dr_statistics():
    """Format Helm Design Rule Statistics within design-rule-compliance-report.html file."""
    global BUILD_NOTIFICATION
    data_length = 5
    default_value = "Please refer to {report_link}"
    data_passed = default_value
    data_failed = default_value
    data_disabled = default_value
    data_warning = default_value
    data_skip_failed = default_value
    data_skip_passed = default_value
    data_draft = default_value
    data_exempt = default_value

    data_position = "section_3"
    data_template = (
        "<p><b>Detailed Helm DR Check Results:</b></p>"
        + "<table>"
        + "<thead>"
        + "<tr style='text-align: left'>"
        + "<th style='color: white; background-color: black;'>Verdict</th>"
        + "<th style='color: white; background-color: black;'>Verdict Description</th>"
        + "<th style='color: white; background-color: black;'>Count&emsp;</th>"
        + "<th style='color: white; background-color: black;'>Design Rules</th>"
        + "</tr>"
        + "</thead>"
        + "<tbody>"
        + "<tr style='text-align: left;'>"
        + "<td style='background-color: #008001;'>PASS</td>"
        + "<td>Passed the Helm DR check.</td>"
        + "<td>{count_passed}</td>"
        + "<td>{passed}</td>"
        + "</tr>"
        + "<tr style='text-align: left;'>"
        + "<td style='background-color: #fe0000;'>FAILED</td>"
        + "<td>Failed the Helm DR check</td>"
        + "<td>{count_failed}</td>"
        + "<td>{failed}</td>"
        + "</tr>"
        + "<tr style='text-align: left;'>"
        + "<td style='background-color: #ffff01;'>WARNING</td>"
        + "<td>The DR check could not be fully determined.</td>"
        + "<td>{count_warning}</td>"
        + "<td>{warning}</td>"
        + "</tr>"
        + "<tr style='text-align: left;'>"
        + "<td style='background-color: #dfded9;'>DISABLE</td>"
        + "<td>The rule is disabled by configuration.</td>"
        + "<td>{count_disabled}</td>"
        + "<td>{disabled}</td>"
        + "</tr>"
        + "<tr style='text-align: left;'>"
        + "<td style='background-color: #ff5001;'>SKIP_FAIL</td>"
        + "<td>The rule is failing, and its configuration is set to SKIP.</td>"
        + "<td>{count_skip_failed}</td>"
        + "<td>{skip_failed}</td>"
        + "</tr>"
        + "<tr style='text-align: left;'>"
        + "<td style='background-color: #7f817b;'>SKIP_PASS&emsp;</td>"
        + "<td>The rule is passing, and its configuration is set to SKIP.</td>"
        + "<td>{count_skip_passed}</td>"
        + "<td>{skip_passed}</td>"
        + "</tr>"
        + "<tr style='text-align: left;'>"
        + "<td style='background-color: #ff00fe;'>DRAFT</td>"
        + "<td>The rule's configuration is set to SKIP because it has not been approved yet.</td>"
        + "<td>{count_draft}</td>"
        + "<td>{draft}</td>"
        + "</tr>"
        + "<tr style='text-align: left;'>"
        + "<td style='background-color: #00ff01;'>EXEMPT</td>"
        + "<td>An official exemption is granted. Therefore, the DR checker tool verdict is set to be true.</td>"
        + "<td>{count_exempt}</td>"
        + "<td>{exempt}</td>"
        + "</tr>"
        + "</tbody>"
        + "</table>"
    )

    if len(HELM_DR_CHECK_REPORT_DATA_PASSED) == 0:
        data_passed = "-"
    elif len(HELM_DR_CHECK_REPORT_DATA_PASSED) <= data_length:
        data_passed = (
            str(HELM_DR_CHECK_REPORT_DATA_PASSED)
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )

    if len(HELM_DR_CHECK_REPORT_DATA_FAILED) == 0:
        data_failed = "-"
    elif len(HELM_DR_CHECK_REPORT_DATA_FAILED) <= data_length:
        data_failed = (
            str(HELM_DR_CHECK_REPORT_DATA_FAILED)
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )

    if len(HELM_DR_CHECK_REPORT_DATA_DISABLED) == 0:
        data_disabled = "-"
    elif len(HELM_DR_CHECK_REPORT_DATA_DISABLED) <= data_length:
        data_disabled = (
            str(HELM_DR_CHECK_REPORT_DATA_DISABLED)
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )

    if len(HELM_DR_CHECK_REPORT_DATA_WARNING) == 0:
        data_warning = "-"
    elif len(HELM_DR_CHECK_REPORT_DATA_WARNING) <= data_length:
        data_warning = (
            str(HELM_DR_CHECK_REPORT_DATA_WARNING)
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )

    if len(HELM_DR_CHECK_REPORT_DATA_SKIP_FAIL) == 0:
        data_skip_failed = "-"
    elif len(HELM_DR_CHECK_REPORT_DATA_SKIP_FAIL) <= data_length:
        data_skip_failed = (
            str(HELM_DR_CHECK_REPORT_DATA_SKIP_FAIL)
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )

    if len(HELM_DR_CHECK_REPORT_DATA_SKIP_PASS) == 0:
        data_skip_passed = "-"
    elif len(HELM_DR_CHECK_REPORT_DATA_SKIP_PASS) <= data_length:
        data_skip_passed = (
            str(HELM_DR_CHECK_REPORT_DATA_SKIP_PASS)
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )

    if len(HELM_DR_CHECK_REPORT_DATA_DRAFT) == 0:
        data_draft = "-"
    elif len(HELM_DR_CHECK_REPORT_DATA_DRAFT) <= data_length:
        data_draft = (
            str(HELM_DR_CHECK_REPORT_DATA_DRAFT)
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )

    if len(HELM_DR_CHECK_REPORT_DATA_EXEMPT) == 0:
        data_exempt = "-"
    elif len(HELM_DR_CHECK_REPORT_DATA_EXEMPT) <= data_length:
        data_exempt = (
            str(HELM_DR_CHECK_REPORT_DATA_EXEMPT)
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )

    data_string = data_template.format(
        count_passed=len(HELM_DR_CHECK_REPORT_DATA_PASSED),
        count_skip_passed=len(HELM_DR_CHECK_REPORT_DATA_SKIP_PASS),
        count_exempt=len(HELM_DR_CHECK_REPORT_DATA_EXEMPT),
        count_disabled=len(HELM_DR_CHECK_REPORT_DATA_DISABLED),
        count_draft=len(HELM_DR_CHECK_REPORT_DATA_DRAFT),
        count_warning=len(HELM_DR_CHECK_REPORT_DATA_WARNING),
        count_skip_failed=len(HELM_DR_CHECK_REPORT_DATA_SKIP_FAIL),
        count_failed=len(HELM_DR_CHECK_REPORT_DATA_FAILED),
        passed=data_passed,
        skip_passed=data_skip_passed,
        exempt=data_exempt,
        disabled=data_disabled,
        draft=data_draft,
        warning=data_warning,
        skip_failed=data_skip_failed,
        failed=data_failed,
    )
    output_string = data_string.format(report_link=helm_dr_check_report_link)
    BUILD_NOTIFICATION = BUILD_NOTIFICATION.replace(data_position, output_string)


# pylint: disable=too-many-branches,global-statement
def fetch_helm_dr_summary():
    """Format Helm Design Rule Summary within design-rule-compliance-report.html file."""
    global BUILD_NOTIFICATION
    data_position = "section_2"
    data_template = (
        "<p><b>DR Check Summary:</b></p>"
        + "<table>"
        + "<thead>"
        + "<tr style='text-align: left;'>"
        + "<th style='color: white; background-color: black;'>Rules</th>"
        + "<th style='color: white; background-color: black;'>Count&emsp;</th></tr>"
        + "</thead>"
        + "<tbody>"
        + "<tr style='text-align: left; background-color: #008001;'>"
        + "<td>Rules ran and passed</td>"
        + "<td>{ran_and_passed}</td>"
        + "</tr>"
        + "<tr style='text-align: left; background-color: #fe0000;'>"
        + "<td>Rules ran and failed</td>"
        + "<td>{ran_and_failed}</td>"
        + "</tr>"
        + "<tr style='text-align: left; background-color: #ffff01;'>"
        + "<td>Rules ran and warning</td>"
        + "<td>{ran_and_warning}</td>"
        + "</tr>"
        + "<tr style='text-align: left; background-color: #dfded9;'>"
        + "<td>Remaining rules (Exempt + Disable + Draft)&emsp;&emsp;</td>"
        + "<td>{remaining_rules}</td>"
        + "</tr>"
        + "<tr style='text-align: left;'>"
        + "<td><b>Total rules</b></td>"
        + "<td><b>{total}</b></td>"
        + "</tr>"
        + "</tbody>"
        + "</table>"
    )

    count_ran_and_passed = len(HELM_DR_CHECK_REPORT_DATA_PASSED) + len(
        HELM_DR_CHECK_REPORT_DATA_SKIP_PASS
    )
    count_ran_and_failed = len(HELM_DR_CHECK_REPORT_DATA_FAILED) + len(
        HELM_DR_CHECK_REPORT_DATA_SKIP_FAIL
    )
    count_ran_and_warning = len(HELM_DR_CHECK_REPORT_DATA_WARNING)
    count_remaining = (
        len(HELM_DR_CHECK_REPORT_DATA_DISABLED)
        + len(HELM_DR_CHECK_REPORT_DATA_EXEMPT)
        + len(HELM_DR_CHECK_REPORT_DATA_DRAFT)
    )
    count_total = (
        count_ran_and_passed
        + count_ran_and_failed
        + count_ran_and_warning
        + count_remaining
    )

    output_string = data_template.format(
        ran_and_passed=count_ran_and_passed,
        ran_and_failed=count_ran_and_failed,
        ran_and_warning=count_ran_and_warning,
        remaining_rules=count_remaining,
        total=count_total,
    )
    BUILD_NOTIFICATION = BUILD_NOTIFICATION.replace(data_position, output_string)


def save_helm_dr_compliance_results():
    """Save DR Compliance results to .bob/design-rule-compliance-report.html file within the workspace."""
    with open(HELM_DR_COMPLIANCE_REPORT, "a", encoding="utf-8") as output_file:
        output_file.write(BUILD_NOTIFICATION)
    output_file.close()

# pylint: disable=broad-except
def main():
    """Call main function that is called once the file is called."""
    if len(sys.argv) != 2:
        print("Error: Function name is not supplied!")
        sys.exit("Error")

    function_name = sys.argv[1]
    if function_name == "validate_helm_dr_compliance":
        try:
            validate_helm_dr_compliance()
        except Exception as error:
            print(error)
            sys.exit("Error")


if __name__ == "__main__":
    main()
