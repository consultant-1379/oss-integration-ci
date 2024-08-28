#!/bin/bash
# shellcheck disable=SC2086
#set -xv

function print_variables() {
  echo "The following arguments were passed:"
  echo "- File: $file"
  echo "- Image: $image"
  echo "- Include image: $include_image"
  echo "- CSAR Sol Version: $sol_version"
}

function build_csar() {
  while IFS= read -r prop; do
    echo "Found property entry: $prop"
    IFS='=' read -ra property_entry <<< "$prop"
    if [ "${#property_entry[@]}" -le 1 ]; then
      echo "Invalid property found: $prop"
      exit 1
    fi
    csar_name_version="${property_entry[0]}"
    csar_chart_content_list="$(echo "${property_entry[1]}" | tr -d '[:space:]' | tr ',' ' ')"
    # Is it a helm Chart or a Helmfile
    if [[ "${csar_name_version}" == *"helmfile"* ]]; then
      csar_type="--helmfile"
    else
      csar_type="--helm"
    fi
    if [ "$include_image" == "true" ]; then
      no_image=""
    else
      no_image="--no-images"
    fi

    echo -e "\n---------- Building Mini CSAR ${csar_name_version} ----------\n"
    for count in {1..5}; do
      echo -e "\n---------- Attempt ${count} of 5 for ${csar_name_version} ----------\n"

      echo "Executing :: docker run --rm --volume $(pwd):$(pwd) -w $(pwd) ${image} generate ${csar_type} ${csar_chart_content_list} --name ${csar_name_version} --sol-version ${sol_version} ${no_image}"
      docker run --user "$(id -u)":"$(id -g)" --rm --volume "$(pwd)":"$(pwd)" -w "$(pwd)" "${image}" generate "${csar_type}" ${csar_chart_content_list} --name "${csar_name_version}" --sol-version "${sol_version}" "${no_image}"
      cmd_exit_code=$?
      if [ "${cmd_exit_code}" -eq 0 ]; then
        break
      fi
    done
  done < "$file"
}

while getopts ":f:d:i:s:" opt; do
  case $opt in
    f) file="$OPTARG"
    ;;
    d) image="$OPTARG"
    ;;
    i) include_image="$OPTARG"
    ;;
    s) sol_version="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done
shift $((OPTIND-1))

print_variables
build_csar
