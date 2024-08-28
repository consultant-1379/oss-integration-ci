#!/bin/bash
# shellcheck disable=SC2016
set -ex
# This script was created by edoytre for the purpose of installing
# eric-pm-server, kube-state-metrics and node exporter onto clusters monitored by
# application staging. Script is split into two sections 1) Teardown to completely remove
# and 2) Installation for a complete Install. Flow is controlled by 'TEARDOWN' parameter, false by default.

# Variables passed in through Jenkins
NAMESPACE=$1
INGRESS_IP=$2 #eric-pm-server ingress IP
TEARDOWN=$3 #default 'false', will perform uninstall when set to true
FUNCTIONAL_USER_USERNAME=$4
FUNCTIONAL_USER_PASSWORD=$5
GRAFANA_HOSTNAME=$6
KUBECONFIG=$7
GRAFANA_DATASOURCE_NAME=$8
GRAFANA_API_KEY=$9
# Expression below will remove all non-digit characters. If someone will pass value like "8Gi", it will be asigned to variable as "8"
PMSERVER_PVC_SIZE=${10//[!0-9]/}
PMSERVER_MEMORY_LIMITS=${11//[!0-9]/}

# Hardcoded Vars
# For prometheus config to get around escape chars. Do not modify. Add new if needed for new troublesome scrape vals.
# ** DO NOT MODIFY! **
REPLACEMENT_VALS='$1:$2'
NODE_REPLACEMENT_VALS='/api/v1/nodes/${1}/proxy/metrics'
CADVISOR_REPLACEMENT_VALS='/api/v1/nodes/${1}/proxy/metrics/cadvisor'
CADVISOR_REPLACEMENT_VALS_TWO='${2}-${1}'
CADVISOR_REPLACEMENT_VALS_THREE='${1}'
# ** DO NOT MODIFY! **

# Retention size need to be less than overall PVC size, so let it get reduced by 15%
PMSERVER_RETENTION_SIZE=$(( PMSERVER_PVC_SIZE*85/100 ))

### TEARDOWN SECTION ###

# Complete Uninstall section with error handling, if teardown parameter is set to true
if [ "$TEARDOWN" = 'true' ]; then
  echo "TEARDOWN parameter was set to true, uninstalling..."
  # If eric-pm-server present, uninstall, else echo and continue
  if helm status -n "${NAMESPACE}" monitoring-eric-pm --kubeconfig "$KUBECONFIG"; then
    helm uninstall -n "$NAMESPACE" monitoring-eric-pm --kubeconfig "$KUBECONFIG"
    echo "Uninstalled monitoring-eric-pm"
  else
    echo "monitoring-eric-pm not found"
  fi
  # If eric-pm-server clusterrolebinding exists, delete, else echo and continue
  if kubectl get clusterrolebinding eric-pm-server-"$NAMESPACE" --kubeconfig "$KUBECONFIG"; then
    kubectl delete clusterrolebinding eric-pm-server-"$NAMESPACE" --kubeconfig "$KUBECONFIG"
    echo "Deleted clusterrolebinding eric-pm-server-$NAMESPACE"
  else
    echo "clusterrolebinding eric-pm-server-$NAMESPACE not found"
  fi
  # If eric-pm-server clusterrole exists, delete, else echo and continue
  if kubectl get clusterrole eric-pm-server-"$NAMESPACE" --kubeconfig "$KUBECONFIG"; then
    kubectl delete clusterrole eric-pm-server-"$NAMESPACE" --kubeconfig "$KUBECONFIG"
    echo "Deleted clusterrole eric-pm-server-$NAMESPACE"
  else
    echo "clusterrole eric-pm-server-$NAMESPACE not found"
  fi
  # If eric-pm-kube-state-metrics present, uninstall, else echo and continue
  if helm status -n "${NAMESPACE}" monitoring-eric-pm-kube-state-metrics --kubeconfig "$KUBECONFIG"; then
    helm uninstall -n "$NAMESPACE" monitoring-eric-pm-kube-state-metrics --kubeconfig "$KUBECONFIG"
    echo "Uninstalled monitoring-eric-pm-kube-state-metrics"
  else
    echo "monitoring-eric-pm-kube-state-metrics not found"
  fi
  # If eric-pm-kube-state-metrics clusterrolebinding present, delete, else echo and continue
  if kubectl get clusterrolebinding eric-pm-kube-state-metrics-"$NAMESPACE" --kubeconfig "$KUBECONFIG"; then
    kubectl delete clusterrolebinding eric-pm-kube-state-metrics-"$NAMESPACE" --kubeconfig "$KUBECONFIG"
    echo "Deleted clusterrolebinding eric-pm-kube-state-metrics-$NAMESPACE"
  else
    echo "clusterrolebinding eric-pm-kube-state-metrics-$NAMESPACE not found"
  fi
  # If eric-pm-kube-state-metrics clusterrole present, delete, else echo and continue
  if kubectl get clusterrole eric-pm-kube-state-metrics-"$NAMESPACE" --kubeconfig "$KUBECONFIG"; then
    kubectl delete clusterrole eric-pm-kube-state-metrics-"$NAMESPACE" --kubeconfig "$KUBECONFIG"
    echo "Deleted clusterrole eric-pm-kube-state-metrics-$NAMESPACE"
  else
    echo "clusterrole eric-pm-kube-state-metrics-$NAMESPACE not found"
  fi
  # If defined namespace is present, delete, else echo and continue
  if kubectl get ns "$NAMESPACE" --kubeconfig "$KUBECONFIG"; then
    kubectl delete ns "$NAMESPACE" --kubeconfig "$KUBECONFIG"
    echo "Deleted $NAMESPACE namespace"
  else
    echo "$NAMESPACE namespace not found"
  fi
  # Echo all resources have been deleted and exit script
  echo "Teardown complete, $NAMESPACE and all associated resources have been removed"
  exit 0
# Teardown was set to 'false', start Installation...
else
  echo "TEARDOWN parameter was set to false, starting Installation..."
fi

### INSTALL SECTION ###
# Create appstaging-monitoring namespace
echo "Checking if $NAMESPACE namespace already exists...."
if kubectl get ns "${NAMESPACE}" --kubeconfig "$KUBECONFIG"; then
  echo "Namespace already exists, please check resources inside"
  exit 1 #Automatic Fail to investigate if namespace already present on machine
else
  echo "Namespace doesn't exist, Creating $NAMESPACE namespace ..."
  kubectl create ns "$NAMESPACE" --kubeconfig "$KUBECONFIG"
fi

# Create Image Pull Secret
echo "Creating Image Pull Secret"
kubectl create secret generic k8s-registry-secret \
  --from-file=.dockerconfigjson="$PWD"/armdockerconfig.json \
  --type=kubernetes.io/dockerconfigjson \
  --namespace "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Add image pull secrets to default sa
kubectl patch serviceaccount -n "$NAMESPACE" default -p '{"imagePullSecrets": [{"name": "k8s-registry-secret"}]}' --kubeconfig "$KUBECONFIG"

# Create Service Account
echo "Creating Service Account for eric-pm-server"
kubectl create sa eric-pm-server-"$NAMESPACE" -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Add image pull secrets to pm server sa
kubectl patch sa eric-pm-server-"$NAMESPACE" -n "$NAMESPACE" -p '{"imagePullSecrets": [{"name": "k8s-registry-secret"}]}' --kubeconfig "$KUBECONFIG"

# Create Cluster Role
echo "Creating clusterrole for eric-pm-server"
cat > eric-pm-server-clusterrole.yaml << EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: eric-pm-server-$NAMESPACE
rules:
  - apiGroups:
      - ""
    resources:
      - nodes
      - nodes/proxy
      - services
      - endpoints
      - pods
      - ingresses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ""
    resources:
      - configmaps
    verbs:
      - get
  - apiGroups:
      - "extensions"
    resources:
      - ingresses/status
      - ingresses
    verbs:
      - get
      - list
      - watch
  - nonResourceURLs:
      - "/metrics"
    verbs:
      - get
EOF

kubectl apply -f eric-pm-server-clusterrole.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Create ClusterRoleBinding
echo "Creating Clusterrolebinding for eric-pm-server"
cat > eric-pm-crb.yaml << EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: eric-pm-server-$NAMESPACE
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: eric-pm-server-$NAMESPACE
subjects:
- kind: ServiceAccount
  name: eric-pm-server-$NAMESPACE
  namespace: $NAMESPACE
EOF

kubectl apply -f eric-pm-crb.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Create Configmap (pm-server configuration)
echo "Creating Configmap for pm-server configuration"
cat > eric-pm-cm.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: eric-pm-server
  labels:
    name: eric-pm-server
  namespace: $NAMESPACE
data:
  prometheus.yml: |
    global:
      scrape_interval: 60s
      scrape_timeout: 10s
      evaluation_interval: 1m
    rule_files:
    scrape_configs:
      - job_name: prometheus-appstaging
        static_configs:
          - targets:
            - localhost:9090
            - localhost:9087
      - job_name: kube-state-metrics-appstaging
        static_configs:
          - targets:
            - eric-pm-kube-state-metrics.$NAMESPACE.svc.cluster.local:8080
      - job_name: 'node-exporter-appstaging'
        kubernetes_sd_configs:
          - role: endpoints
        relabel_configs:
        - source_labels: [__meta_kubernetes_endpoints_name]
          regex: 'node-exporter-appstaging'
          action: keep


      - job_name: 'kubernetes-nodes-appstaging'

        # Default to scraping over https
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
          # If your node certificates are self-signed or use a different CA to the
          # master CA, then disable certificate verification below. Note that
          # certificate verification is an integral part of a secure infrastructure
          # so this should only be disabled in a controlled environment. You can
          # disable certificate verification by uncommenting the line below.
          #
          #insecure_skip_verify: true
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

        kubernetes_sd_configs:
          - role: node
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)
          - target_label: __address__
            replacement: kubernetes.default.svc:443
          - source_labels: [__meta_kubernetes_node_name]
            regex: (.+)
            target_label: __metrics_path__
            replacement: $NODE_REPLACEMENT_VALS

      - job_name: 'kubernetes-nodes-cadvisor-appstaging'

        # Default to scraping over https
        scheme: https
        # Require to get more accurate rate metrics for CPU/RAM usage
        scrape_interval: 15s
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
          # If your node certificates are self-signed or use a different CA to the
          # master CA, then disable certificate verification below. Note that
          # certificate verification is an integral part of a secure infrastructure
          # so this should only be disabled in a controlled environment. You can
          # disable certificate verification by uncommenting the line below.
          #
          #insecure_skip_verify: true
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

        kubernetes_sd_configs:
          - role: node
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)
          - target_label: __address__
            replacement: kubernetes.default.svc:443
          - source_labels: [__meta_kubernetes_node_name]
            regex: (.+)
            target_label: __metrics_path__
            replacement: $CADVISOR_REPLACEMENT_VALS
         # replacement: /api/v1/nodes/${1}:4194/proxy/metrics
        metric_relabel_configs:
          - action: replace
            source_labels: [id]
            regex: '^/machine\.slice/machine-rkt\\x2d([^\\]+)\\.+/([^/]+)\.service$'
            target_label: rkt_container_name
            replacement: $CADVISOR_REPLACEMENT_VALS_TWO
          - action: replace
            source_labels: [id]
            regex: '^/system\.slice/(.+)\.service$'
            target_label: systemd_service_name
            replacement: $CADVISOR_REPLACEMENT_VALS_THREE

      # Scrape config for service endpoints.
      - job_name: 'kubernetes-service-endpoints-appstaging'

        kubernetes_sd_configs:
          - role: endpoints

        relabel_configs:
          - source_labels: [__meta_kubernetes_service_name]
            action: replace
            target_label: job
          - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scheme]
            action: replace
            target_label: __scheme__
            regex: (https?)
          - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
            action: replace
            target_label: __address__
            regex: ((?:\[.+\])|(?:.+))(?::\d+);(\d+)
            replacement: $REPLACEMENT_VALS
          - action: labelmap
            regex: __meta_kubernetes_service_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_service_name]
            action: replace
            target_label: kubernetes_name

      # Example scrape config for probing services via the Blackbox Exporter.
      - job_name: 'kubernetes-services-appstaging'

        metrics_path: /probe
        params:
          module: [http_2xx]

        kubernetes_sd_configs:
          - role: service

        relabel_configs:
          - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_probe]
            action: keep
            regex: true
          - source_labels: [__address__]
            target_label: __param_target
          - target_label: __address__
            replacement: blackbox
          - source_labels: [__param_target]
            target_label: instance
          - action: labelmap
            regex: __meta_kubernetes_service_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_service_name]
            target_label: kubernetes_name

      # Example scrape config for pods
      - job_name: 'kubernetes-pods-appstaging'

        kubernetes_sd_configs:
          - role: pod

        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scheme]
            action: replace
            target_label: __scheme__
            regex: (https?)
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ((?:\[.+\])|(?:.+))(?::\d+);(\d+)
            replacement: $REPLACEMENT_VALS
            target_label: __address__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name
EOF

kubectl apply -f eric-pm-cm.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Helm Installation of eric-pm-server
echo "Helm Installation of eric-pm-server"
helm repo add chart-repo https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm/ --username "$FUNCTIONAL_USER_USERNAME" --password "$FUNCTIONAL_USER_PASSWORD" --kubeconfig "$KUBECONFIG"
helm install monitoring-eric-pm chart-repo/eric-pm-server --namespace "$NAMESPACE" --kubeconfig "$KUBECONFIG"\
  --set global.security.tls.enabled=false \
  --set server.configMapOverrideName=eric-pm-server \
  --set server.serviceAccountName=eric-pm-server-"${NAMESPACE}" \
  --set server.persistentVolume.enabled=true \
  --set server.persistentVolume.size="${PMSERVER_PVC_SIZE}"Gi \
  --set resources.eric-pm-server.limits.cpu=4 \
  --set resources.eric-pm-server.limits.memory="${PMSERVER_MEMORY_LIMITS}"Gi \
  --set server.tsdb.retention.size="${PMSERVER_RETENTION_SIZE}"GB \
  --set imageCredentials.pullSecret=k8s-registry-secret

# Create Ingress for eric-pm-server
echo "Creating Ingress for eric-pm-server"
echo "Ingress hostname is ${INGRESS_IP}"
cat > eric-pm-ingress.yaml << EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: eric-pm-server-$NAMESPACE-ingress
  namespace: $NAMESPACE
spec:
  ingressClassName: nginx
  rules:
  - host: $INGRESS_IP
    http:
      paths:
      - backend:
          service:
            name: eric-pm-server
            port:
              number: 9090
        path: /
        pathType: ImplementationSpecific
EOF

kubectl apply -f eric-pm-ingress.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"
kubectl get ingress --all-namespaces --kubeconfig "$KUBECONFIG"

# Create Network Policy
echo "Creating eric-pm-server Network Policy"
cat > eric-pm-network-policy.yaml << EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: eric-pm-server-$NAMESPACE-allow-external-traffic
  namespace: $NAMESPACE
spec:
  ingress:
  - {}
  podSelector:
    matchLabels:
      app: eric-pm-server
  policyTypes:
  - Ingress
EOF

kubectl apply -f eric-pm-network-policy.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Install Node Exporter
echo "Installing Node Exporter"
cat > node-exporter.yaml << EOF
apiVersion: apps/v1
kind: DaemonSet
metadata:
  labels:
    app.kubernetes.io/component: exporter
    app.kubernetes.io/name: node-exporter-appstaging
  name: node-exporter-appstaging
  namespace: $NAMESPACE
spec:
  selector:
    matchLabels:
      app.kubernetes.io/component: exporter
      app.kubernetes.io/name: node-exporter-appstaging
  template:
    metadata:
      labels:
        app.kubernetes.io/component: exporter
        app.kubernetes.io/name: node-exporter-appstaging
    spec:
      containers:
      - args:
        - --path.sysfs=/host/sys
        - --path.rootfs=/host/root
        - --no-collector.wifi
        - --no-collector.hwmon
        - --collector.filesystem.ignored-mount-points=^/(dev|proc|sys|var/lib/docker/.+|var/lib/kubelet/pods/.+)($|/)
        - --collector.netclass.ignored-devices=^(veth.*)$
        name: node-exporter-appstaging
        image: armdocker.rnd.ericsson.se/dockerhub-ericsson-remote/prom/node-exporter
        ports:
          - containerPort: 9100
            protocol: TCP
        resources:
          limits:
            cpu: 250m
            memory: 180Mi
          requests:
            cpu: 102m
            memory: 180Mi
        volumeMounts:
        - mountPath: /host/sys
          mountPropagation: HostToContainer
          name: sys
          readOnly: true
        - mountPath: /host/root
          mountPropagation: HostToContainer
          name: root
          readOnly: true
      serviceAccountName: eric-pm-server-$NAMESPACE
      volumes:
      - hostPath:
          path: /sys
        name: sys
      - hostPath:
          path: /
        name: root
EOF

kubectl apply -f node-exporter.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Create Node Exporter Service
echo "Creating Node Exporter Service"
cat > node-exporter-service.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: node-exporter-appstaging
  namespace: $NAMESPACE
  annotations:
      prometheus.io/scrape: 'true'
      prometheus.io/port:   '9100'
spec:
  selector:
      app.kubernetes.io/component: exporter
      app.kubernetes.io/name: node-exporter-appstaging
  ports:
  - name: node-exporter-appstaging
    protocol: TCP
    port: 9100
    targetPort: 9100
EOF

kubectl apply -f node-exporter-service.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Create Service Account for Kube State Metrics
echo "Creating Service Account for Kube State Metrics"
kubectl create sa -n "$NAMESPACE" eric-pm-kube-state-metrics-"$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Ad pull secrets to sa
kubectl patch sa -n "$NAMESPACE" eric-pm-kube-state-metrics-"$NAMESPACE" -p '{"imagePullSecrets": [{"name": "k8s-registry-secret"}]}' --kubeconfig "$KUBECONFIG"

# Create Cluster Role for Kube State Metrics
echo "Creating Cluster Role for Kube State Metrics"
cat > kube-state-clusterrole.yaml << EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: eric-pm-kube-state-metrics-$NAMESPACE
rules:
- apiGroups:
  - ""
  resources:
  - configmaps
  - secrets
  - nodes
  - pods
  - services
  - serviceaccounts
  - resourcequotas
  - replicationcontrollers
  - limitranges
  - persistentvolumeclaims
  - persistentvolumes
  - namespaces
  - endpoints
  verbs:
  - list
  - watch
- apiGroups:
  - apps
  resources:
  - statefulsets
  - daemonsets
  - deployments
  - replicasets
  verbs:
  - list
  - watch
- apiGroups:
  - batch
  resources:
  - cronjobs
  - jobs
  verbs:
  - list
  - watch
- apiGroups:
  - autoscaling
  resources:
  - horizontalpodautoscalers
  verbs:
  - list
  - watch
- apiGroups:
  - authentication.k8s.io
  resources:
  - tokenreviews
  verbs:
  - create
- apiGroups:
  - authorization.k8s.io
  resources:
  - subjectaccessreviews
  verbs:
  - create
- apiGroups:
  - policy
  resources:
  - poddisruptionbudgets
  verbs:
  - list
  - watch
- apiGroups:
  - certificates.k8s.io
  resources:
  - certificatesigningrequests
  verbs:
  - list
  - watch
- apiGroups:
  - storage.k8s.io
  resources:
  - storageclasses
  - volumeattachments
  verbs:
  - list
  - watch
- apiGroups:
  - admissionregistration.k8s.io
  resources:
  - mutatingwebhookconfigurations
  - validatingwebhookconfigurations
  verbs:
  - list
  - watch
- apiGroups:
  - networking.k8s.io
  resources:
  - networkpolicies
  - ingresses
  verbs:
  - list
  - watch
- apiGroups:
  - coordination.k8s.io
  resources:
  - leases
  verbs:
  - list
  - watch
- apiGroups:
  - rbac.authorization.k8s.io
  resources:
  - clusterrolebindings
  - clusterroles
  - rolebindings
  - roles
  verbs:
  - list
  - watch
EOF

kubectl apply -f kube-state-clusterrole.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Create Clusterrolebinding for Kube State Metrics
echo "Creating Clusterrolebinding for Kube State Metrics"
cat > eric-ksm-crb.yaml << EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: eric-pm-kube-state-metrics-$NAMESPACE
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: eric-pm-kube-state-metrics-$NAMESPACE
subjects:
- kind: ServiceAccount
  name: eric-pm-kube-state-metrics-$NAMESPACE
  namespace: $NAMESPACE
EOF

kubectl apply -f eric-ksm-crb.yaml -n "$NAMESPACE" --kubeconfig "$KUBECONFIG"

# Helm Install of Kube State Metrics
echo "Installing Kube State Metrics"
helm repo add state-chart-repo https://arm.seli.gic.ericsson.se/artifactory/proj-adp-pm-kube-state-metrics-released-helm-local/ \
  --username "$FUNCTIONAL_USER_USERNAME" \
  --password "$FUNCTIONAL_USER_PASSWORD" \
  --kubeconfig "$KUBECONFIG"
helm install monitoring-eric-pm-kube-state-metrics state-chart-repo/eric-pm-kube-state-metrics \
  --version 2.3.0+17 \
  --namespace "$NAMESPACE" \
  --kubeconfig "$KUBECONFIG" \
  --set security.tls.enabled=false \
  --set rbac.appMonitoring.enabled=false \
  --set kubeStateMetrics.serviceAccountName=eric-pm-kube-state-metrics-"$NAMESPACE"

# Add newly created prometheus as a datasource to Grafana via api
echo  "Adding prometheus $INGRESS_IP as a datasource to Grafana ${GRAFANA_HOSTNAME}"
generate_post_data() #Helper function to process data of post request to Grafana
{
  cat <<EOF
{
  "name": "$GRAFANA_DATASOURCE_NAME",
  "type": "prometheus",
  "url": "http://$INGRESS_IP",
  "access": "proxy",
  "basicAuth": false
}
EOF
}

# Post request to add installed prometheus as a datsource to Grafana
response=$(curl -fsSLw "%{http_code}" 'http://seliius29510.seli.gic.ericsson.se:3000/api/datasources' \
-X  POST -H 'Content-Type: application/json;charset=UTF-8' \
-H "Authorization: Bearer $GRAFANA_API_KEY"  \
--data "$(generate_post_data)") || \
  if [[ ${response: -3} == 409  ]] ; then
    echo "WARNING: Datasource with the same name already exist."
  else
    echo "ERROR: Couldn't create a new datasource. Response:"
    echo "$response"
    exit1
  fi

echo "Installation finished, view metrics on ${GRAFANA_HOSTNAME} by selecting $GRAFANA_DATASOURCE_NAME as a datasource on relevant dashboards"