#!/usr/bin/env bash

while [ $# -gt 0 ]; do
  case "$1" in
  --sprint_number*)
    if [[ "$1" != *=* ]]; then shift; fi # Value is next arg if no `=`
    SPRINT_NUMBER="${1#*=}"
    ;;
  --jiras*)
    if [[ "$1" != *=* ]]; then shift; fi # Value is next arg if no `=`
    JIRALIST="${1#*=}"
    ;;
  --release_type*)
    if [[ "$1" != *=* ]]; then shift; fi
    RELEASE_TYPE="${1#*=}"
    ;;
  --helmfile_csars*)
    if [[ "$1" != *=* ]]; then shift; fi # Value is next arg if no `=`
    HELMFILE_CSARS="${1#*=}"
    ;;
  --dm_version*)
    if [[ "$1" != *=* ]]; then shift; fi
    DM_VERSION="${1#*=}"
    ;;
  --product_name*)
    if [[ "$1" != *=* ]]; then shift; fi
    PRODUCT_NAME="${1#*=}"
    ;;
  --custwf_version*)
    if [[ "$1" != *=* ]]; then shift; fi
    CUSTWF_VERSION="${1#*=}"
    ;;
  --custwf_link*)
    if [[ "$1" != *=* ]]; then shift; fi
    CUSTWF_LINK="${1#*=}"
  esac
  shift
done

if [[ ${RELEASE_TYPE} == "DROP_BACK" ]]; then
  releaseTypeString="Drop Back"
elif [[ ${RELEASE_TYPE} == "NIGHTLY_RELEASE" ]]; then
  releaseTypeString="Nightly Build"
else
  releaseTypeString="Sprint"
fi


p_style='style="margin-top:0;margin-bottom:0;line-height: 1.45;"'

echo "<head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">
<style type=\"text/css\" style=\"display:none;\">
p {margin-top:0;margin-bottom:0;line-height: 1.45;font-family: Calibri, sans-serif;}
a {font-family: Consolas, monospace;}
td, th {border-width: 1px; border-style: solid; border-color: rgb(0, 0, 0); padding-left: 5pt; padding-right: 5pt;}
</style></head>" > emailBody.txt

{ echo "<p>Hi All,<br><br>";
echo "${PRODUCT_NAME} Helmfile and Deployment manager for ${releaseTypeString} ${SPRINT_NUMBER} packages available below:<br></p>"; } >> emailBody.txt

{ echo "<table style=\"border-collapse: collapse; border-spacing: 0px;\">";
echo "<tr>";
echo "<th><p>Package</p></th>";
echo "<th><p>Package Version</p></th>";
echo "</tr>";
echo "<tr>";
echo "<td><p>Deployment Manager</p></td>";
echo "<td><p><a href=\"https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars/dm\"/>""${DM_VERSION}""</a></p></td>";
echo "</tr>";
echo "</table><br><br>"; } >> emailBody.txt

if [[ ${PRODUCT_NAME} == "EO" ]]; then
    { echo "<p>Note all CSARs available <a href=\"https://eteamspace.internal.ericsson.com/display/DGBase/CSAR+Releases\">here</a></p>"; } >> emailBody.txt
else
    { echo "<p>Note all CSARs available <a href=\"https://eteamspace.internal.ericsson.com/display/DGBase/EOOM+CSAR+Releases\">here</a></p>"; } >> emailBody.txt
fi

{ echo "<p>Included Application Versions:<br>";
echo "<table style=\"border-collapse: collapse; border-spacing: 0px;\">";
echo "<tr>";
echo "<th><p>Application</p></th>";
echo "<th><p>Application Version</p></th>";
echo "</tr>";
echo "<tr>";
echo "</tr>"; } >> emailBody.txt

# shellcheck disable=SC2001
for csar in $(echo "${HELMFILE_CSARS}" | sed "s/,/ /g");
do
  APP_NAME=$(echo "$csar"|awk -F'/' '{print $(NF-1)}')
  APP_VERSION=$(echo "$csar"|awk -F'/' '{print $NF}')
    if [[ ${APP_NAME} != "None" ]]; then
    echo "$APP_NAME"
    { echo "<tr>";
    echo "<td><p>$APP_NAME</p></td>";
    echo "<td><p><a href=\"$csar\">$APP_VERSION</a></p></td>";
    echo "</tr>"; } >> emailBody.txt
    fi
done
{ echo "</table><br><br>"; } >> emailBody.txt

echo "<p ${p_style}>EO CM Custom Workflow SDK Version included: <a href=\"${CUSTWF_LINK}\">$CUSTWF_VERSION</a></p><br>" >>emailBody.txt

if [[ ${releaseTypeString} == "Sprint" && ${PRODUCT_NAME} == "EO" ]]; then
    { echo "<p>Release notes will need to be updated for all areas for EO ${SPRINT_NUMBER}</p>";
    echo "<p>See the appropriate link under the following area</p>";
    echo "<p><a href=\"https://eteamspace.internal.ericsson.com/display/PAO/EO+Release+Notes+Sprints\">
    https://eteamspace.internal.ericsson.com/display/PAO/EO+Release+Notes+Sprints</a></p><br>"; } >> emailBody.txt
fi

if [[ ${JIRALIST} != "None" ]]; then
    { echo "<p>JIRAs included in this build:</p>"; } >> emailBody.txt
    # shellcheck disable=SC2001
    for jira in $(echo "${JIRALIST}" | sed "s/,/ /g");
    do
        { echo "<p><a href=\"https://eteamproject.internal.ericsson.com/browse/${jira}\">
        https://eteamproject.internal.ericsson.com/browse/${jira}</a></p>"; } >> emailBody.txt
    done
    echo "<br>" >> emailBody.txt
fi

{ echo "<p>Thanks,<br>";
echo "Application Staging</p>"; } >> emailBody.txt
