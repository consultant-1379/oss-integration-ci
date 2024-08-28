"""This module contains the Helm Template Class which models the Helm Templates generated using the site values."""

import subprocess
from functools import reduce
from memoization import cached
import yaml
from utils import find_key_in_dictionary, flatten_list

class Singleton(type):
    """Ensures a single instance of the helm template object is created."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Use to verify the class creation."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class HelmTemplate(metaclass=Singleton):
    """This class contains methods for retrieving information from the rendered chart."""

    def __init__(self, chart_path, values_file_path):
        """Use as a constructor."""
        self.chart_path = chart_path
        self.values_file_path = values_file_path

    @cached
    def get_helm_templates_from_chart(self):
        """Get all helm templates from the helm chart."""
        helm_template_process = subprocess.run(['helm', 'template', "-f", self.values_file_path, self.chart_path],
                                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)

        if helm_template_process.returncode != 0:
            raise Exception(helm_template_process.stdout.decode('utf-8'))

        return list(yaml.load_all(helm_template_process.stdout.decode('utf-8'), Loader=yaml.CSafeLoader))

    @cached
    def get_all_references_with_given_key(self, the_key):
        """Get a flattened list of templates for a given key."""
        references = []
        for template in self.get_helm_templates_from_chart():
            # flake8: noqa: E701
            value = list((template["metadata"]["name"], template["kind"], i)
                         for i in find_key_in_dictionary(input_key=the_key, dictionary=template))
            if value:
                references.append(value)
        return flatten_list(references)

    @cached
    def get_values_with_a_specific_path(self, key_path):
        """Get a flattened list of templates for a given specific template path."""
        references = []
        for template in self.get_helm_templates_from_chart():
            # flake8: noqa: E701
            value = reduce(lambda d, key: d.get(key) if d else None, key_path.split('.'), template)
            if value:
                references.append((template["metadata"]["name"], template["kind"], value))
        return flatten_list(references)

    # flake8: noqa: C901
    # pylint: disable=too-many-branches,bare-except
    @cached
    def get_pods_and_containers(self):
        """Return a list of all pod / container combinations that can be itereated through in tests that need both."""
        pods_and_containers = []
        for template in self.get_helm_templates_from_chart():
            if template is None:
                continue

            for key, value in template.items():
                if key == 'spec':
                    containers = {}
                    try:
                        containers = value['template']['spec']['containers']
                        if containers is None:
                            containers = {}
                    except:
                        pass
                    initcontainers = {}
                    try:
                        initcontainers = value['template']['spec']['initContainers']
                        if initcontainers is None:
                            initcontainers = {}
                    except:
                        pass
                    cronjobcontainers = {}
                    try:
                        cronjobcontainers = value['jobTemplate']['spec']['template']['spec']['containers']
                        if cronjobcontainers is None:
                            cronjobcontainers = {}
                    except:
                        pass
                    ephemeralcontainers = {}
                    try:
                        ephemeralcontainers = value['template']['spec']['ephemeralContainers']
                        if ephemeralcontainers is None:
                            ephemeralcontainers = {}
                    except:
                        pass
                    for container in containers:
                        pods_and_containers.append([template["metadata"]["name"],
                                                    template["kind"], value['template']['spec'], container])
                    for container in initcontainers:
                        pods_and_containers.append([template["metadata"]["name"],
                                                    template["kind"], value['template']['spec'], container])
                    for container in cronjobcontainers:
                        pods_and_containers.append([template["metadata"]["name"],
                                                    template["kind"], value['jobTemplate']['spec'], container])
                    for container in ephemeralcontainers:
                        pods_and_containers.append([template["metadata"]["name"],
                                                    template["kind"], value['template']['spec'], container])

        return pods_and_containers

    @cached
    def get_resulting_container_security_context(self, pod_spec, container_spec):
        """Return a resulting container security context, merging the pods securityContext where found."""
        pod_security_context = {}
        if 'securityContext' in pod_spec:
            if pod_spec['securityContext']:
                pod_security_context = pod_spec['securityContext']

        container_security_context = {}
        if 'securityContext' in container_spec:
            if container_spec['securityContext']:
                container_security_context = container_spec['securityContext']

        overlapping_security_context_keys = ['runAsGroup', 'runAsNonRoot', 'runAsUser']
        for security_context_key in overlapping_security_context_keys:
            if security_context_key not in container_security_context and security_context_key in pod_security_context:
                container_security_context[security_context_key] = pod_security_context[security_context_key]

        return container_security_context

    # flake8: noqa: C901
    # pylint: disable=too-many-branches,bare-except
    @cached
    def get_pod_specs(self):
        """Return a list of all pod specs found in the chart that have containers."""
        pod_specs = []
        for template in self.get_helm_templates_from_chart():
            if template is None:
                continue

            for key, value in template.items():
                if key == 'spec':
                    containers = {}
                    try:
                        containers = value['template']['spec']['containers']
                        if containers is None:
                            containers = {}
                        spec = value['template']['spec']
                    except:
                        pass
                    initcontainers = {}
                    try:
                        initcontainers = value['template']['spec']['initContainers']
                        if initcontainers is None:
                            initcontainers = {}
                        spec = value['template']['spec']
                    except:
                        pass
                    cronjobcontainers = {}
                    try:
                        cronjobcontainers = value['jobTemplate']['spec']['template']['spec']['containers']
                        if cronjobcontainers is None:
                            cronjobcontainers = {}
                        spec = value['jobTemplate']['spec']['template']['spec']
                    except:
                        pass

                    if (len(containers) + len(initcontainers) + len(cronjobcontainers)) > 0:
                        pod_specs.append([template["metadata"]["name"], template["kind"], spec])
        return pod_specs

    @cached
    def get_objects_of_kind(self, kind):
        """Return a list of objects of the given kind."""
        objects = []
        for template in self.get_helm_templates_from_chart():
            if template is None:
                continue
            if template['kind'] == kind:
                objects.append(template)
        return objects

    @cached
    def get_names_of_objects_of_kind(self, kind):
        """Get the names of objects of a certain kind."""
        return [object['metadata']['name'] for object in self.get_objects_of_kind(kind)]

    @cached
    def get_names_of_objects_of_kind_with_test_params(self, kind):
        """Get the names of objects of a certain kind as well as inputs for tests."""
        return [[object['metadata']['name'], 'ServiceAccount', object['metadata']['name']]
                for object in self.get_objects_of_kind(kind)]

    @cached
    def get_names_of_objects_of_kind_network_policy_with_test_params(self, kind):
        """Get the names of objects of a certain kind as well as inputs for tests."""
        return [[object['metadata']['name'], 'NetworkPolicy', object['spec']]
                for object in self.get_objects_of_kind(kind)]

    @cached
    def does_network_policy_have_an_egress_open_connection(self, network_policy):
        """Check whether a given Network Policy have an egress connection."""
        if "egress" in network_policy:
            egress_check_result = self.does_policy_types_contain_egress_and_is_egress_port_specified(network_policy)
            if egress_check_result:
                return True
        elif 'ingress' in network_policy or "Ingress" in network_policy['policyTypes']:
            return True
        return False

    @cached
    def does_policy_types_contain_egress_and_is_egress_port_specified(self, network_policy):
        """Check whether a given Network Policy contains an Egress Port which is specified."""
        if 'egress' in network_policy:
            egress_ports = network_policy['egress'][0]
            if 'to' in egress_ports:
                return False
        return True

    @cached
    def does_service_mesh_object_have_export_to(self, spec):
        """Check if a service mesh object has exportTo parameter with specific value."""
        if 'exportTo' in spec and spec['exportTo'] and len(spec['exportTo']) == 1 and spec['exportTo'][0] == '.':
            return True
        return False

    @cached
    def does_service_mesh_object_have_hosts_with_specific_namespace(self, spec):
        """Check if a service mesh object has hosts parameter with specific value."""
        if 'servers' in spec and spec['servers']:
            for item_server in spec['servers']:
                if 'hosts' in item_server and item_server['hosts']:
                    for item_host in item_server['hosts']:
                        if not item_host.startswith("./"):
                            return False
                else:
                    return False
        else:
            return False
        return True

    @cached
    def get_names_of_service_mesh_resources_of_given_kind(self, kind):
        """Get the names of objects of a certain kind as well as inputs for tests."""
        return [[object['metadata']['name'], object['kind'], object['spec']] for object in
                self.get_objects_of_kind(kind)]

    # pylint: disable=redefined-builtin
    @cached
    def get_names_of_service_mesh_gateway_resources_as_ingress(self):
        """Get the names of objects of a kind "Gateway" that are configured as ingress."""
        result = []
        for object in self.get_names_of_service_mesh_resources_of_given_kind('Gateway'):
            if 'app' in object[2]['selector'] and object[2]['selector']['app'] == "service-mesh-ingress-gateway":
                result.append(object)
        return result
