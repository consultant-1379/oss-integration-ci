# Overview
The ci/jenkins/scripts/common/kubernetes_range_checkers/ directory contains a number of scripts that can be reused to ensure that the kubernetes manifests that are generated from a helm chart or helmfile, support a required range of kubernetes versions.

# Kubernetes Compatibility Checker Stages
Below are the stages which must be run to execute the kubernetes compatibility checkers

## 1) Generate the list of intended supported kubernetes versions
The following script is responsible for this stage.

```print_supported_k8s_versions.sh```

It takes one argument, which is the path to a file containing the minimum and maximum desired kubernetes version to support. This file must be in the following format.

```kubeVersion: <min_version> - <max_version>```

For example.

```kubeVersion: 1.18.0 - 1.22.0```

This is an example of running the script.

```./print_supported_k8s_versions.sh <path_to_kube_version_file> > <output_file_path>```

For example.

```./print_supported_k8s_versions.sh ./path/to/kubeVersion.yaml > ./bob/var.supported-k8s-versions```

The script will obtain the list of all versions in between this minimum and maximum version from the kubernetes GitHub tags and print the full list of versions inclusive of the minimum and maximum to standard out.

## 2) Generate a list of rendered helm templates for the given kubernetes range
The following script is responsible for this stage.

```generate_helm_templates_for_supported_k8s.sh```

Because the yaml templates contained with the microservices helm charts may be written in order to change their rendered output depending on the kubernetes version, or on the capabilities provided by that kubernetes version, we must render the templates for each kubernetes version and run the various kubernetes compatibility checks against each of those rendered charts.

Below is an example of a team checking if the target kubernetes cluster has a specific api version and deciding on the apiVersion to use based on that.

```
{{- $isApiNetworkingV1 := .Capabilities.APIVersions.Has "networking.k8s.io/v1/Ingress" }}
{{- if $isApiNetworkingV1 }}
apiVersion: networking.k8s.io/v1
{{- else }}
apiVersion: networking.k8s.io/v1beta1
{{- end }}
```

helm provides a way to simulate this when running the 'helm template' command by passing in both the --kube-version, as well as multiple --api-versions flags for each api-version.

The supported api-versions of any given kubernetes are available in the schema file for that kubernetes file, available in various GitHub repos. The script will use this repo to generate the required information to pass to helm.

The script also supports helmfile, which allows the passing down of helm arguments such as --kube-version and --api-version. However due to a bug in helmfile, the passing of multiple --api-versions does not currently work. The script achieves this by setting the api versions in a comma separated list in an optional environment variable, which can then be interpreted with some logic in the helmfile such as below. This results in the desired behavior of helm receiving the --api-versions required to render the target charts accurately for each kubernetes version.

```
{{ if env "KUBE_API_VERSIONS" }}
apiVersions:
    {{- range $apiVersion := ( env "KUBE_API_VERSIONS" | split "," ) }}
    - {{ $apiVersion }}
    {{- end }}
{{ end }}
```

This is an example of running the script.

```./generate_helm_templates_for_supported_k8s.sh <path_to_helm_chart_or_helmfile.yaml> <path_to_site_values_file> <path_to_file_containing_supported_kubernetes_versions> <path_to_directory_to_output_templates_to>```

For example.

```./generate_helm_templates_for_supported_k8s.sh ./path/to/helmfile.yaml ./path/to/site_values.yaml ./bob/var.supported-k8s-versions ./bob/helm-templates/```

## 3) Run the deprek8ion checks
The following script is responsible for this stage.

```deprek8ion.sh```

The deprek8ion checker can find deprecated keys in the various objects in the helm chart. Its GitHub page is located [here](https://github.com/swade1987/deprek8ion). It is delivered as a docker image which can be found [here](https://console.cloud.google.com/gcr/images/swade1987/EU/deprek8ion).

The script must be run within the deprek8ion image.

This is an example of running the script.

```./deprek8ion.sh <path_to_file_containing_supported_kubernetes_versions> <path_to_directory_to_output_templates_to>```

For example.

```./deprek8ion.sh ./bob/var.supported-k8s-versions ./bob/helm-templates/```

## 4) Run the kubeval checks
The following script is responsible for this stage.

```kubeval.sh```

The kubeval checker can check kubernetes yaml files against a set of kubernetes schemas. Its GitHub page is located [here](https://github.com/instrumenta/kubeval).

This is an example of running the script.

```./kubeval.sh <path_to_file_containing_supported_kubernetes_versions> <path_to_directory_to_output_templates_to> <optional_comma_separated_list_of_kinds_to_skip>```

For example.

```./kubeval.sh ./bob/var.supported-k8s-versions ./bob/helm-templates/ "HTTPProxy,SomeOtherKind"```

# Reusable bob ruleset file
The ci/jenkins/rulesets/common/ruleset_kubernetes_range_checks.yaml file is a reusable bob ruleset file that other repos can refer to, to call a reusable bob rule called 'run-kubernetes-compatibility-tests'

This bob rule requires several environment variables to be set, in order to pass the required details to each of the scripts outlined earlier in this document. These are as follows.

1. KUBE_VERSION_FILE_PATH: This is the path to the file containing the kubernetes minimum and maximum version to check against.

2. SITE_VALUES_FILE_PATH_FOR_KUBERNETES_COMPATIBILITY_CHECKS: This is the path to the site values file to use during helm/helmfile template commands. This file should enable as many services as possible to maximize how many services get checked.

3. HELMFILE_OR_HELM_CHART_FILE_PATH: This is the path to the helm chart or helmfile to be tested.

4. KUBEVAL_KINDS_TO_SKIP: This is an optional list of comma separated kubernetes kinds to ignore during kubeval checks. These are usually kinds such as 'HTTPProxy' which are provided by Custom Resource Definitions (CRDs) and which kubeval can't validate so must be skipped.

5. GERRIT_USERNAME: This is the username used by helmfile commands to pull down the children helm charts. It is not required if a helmfile is not being tested.

6. GERRIT_PASSWORD: This is the password used by helmfile commands to pull down the children helm charts. It is not required if a helmfile is not being tested.
