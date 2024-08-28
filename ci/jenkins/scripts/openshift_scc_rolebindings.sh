#!/bin/bash

#https://calstore.internal.ericsson.com/elex?LI=EN/LZN7030279*&FN=1531-AOT1015396Uen.*.html&HT=sxm1682108121124&DT=EO+Cloud+Native+Installation+Instructions
#Defining SCC According to CPI, chapter 4.11.1
KUBECONFIG=$1
NAMESPACE=$2

function createSCCVnflcmService() {
  echo "Checking if scc for VNFLCM service exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get scc | grep 'custom-eric-vnflcm-service-scc'
  if [[ $? == 1 ]]; then
    echo "Creating scc for VNFLCM service"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
allowHostDirVolumePlugin: true
allowHostIPC: true
allowHostNetwork: true
allowHostPID: true
allowHostPorts: true
allowPrivilegeEscalation: true
allowPrivilegedContainer: true
allowedCapabilities:
- '*'
allowedUnsafeSysctls:
- '*'
apiVersion: security.openshift.io/v1
defaultAddCapabilities: null
fsGroup:
  type: RunAsAny
groups:
- system:cluster-admins
- system:nodes
- system:masters
kind: SecurityContextConstraints
metadata:
  name: custom-eric-vnflcm-service-scc
priority: null
readOnlyRootFilesystem: false
requiredDropCapabilities: null
runAsUser:
  type: RunAsAny
seLinuxContext:
  type: MustRunAs
seccompProfiles:
- '*'
supplementalGroups:
  type: RunAsAny
users:
- system:admin
- system:serviceaccount:openshift-infra:build-controller
volumes:
- '*'
EOF
  else
    echo "scc for VNFLCM service already created"
  fi
}

function createRoleVnflcmService() {
  echo "Checking if Role VNFLCM service exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get role | grep "$NAMESPACE-eric-vnflcm-service-custom-role"
  if [[ $? == 1 ]]; then
    echo "Creating Role VNFLCM service"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: $NAMESPACE-eric-vnflcm-service-custom-role
  namespace: $NAMESPACE
rules:
  - apiGroups:
      - security.openshift.io
    resources:
      - securitycontextconstraints
    resourceNames:
      - custom-eric-vnflcm-service-scc
    verbs:
      - use
EOF
  else
    echo "Role VNFLCM service already created"
  fi
}


function createRoleBindingVnflcmService() {
  echo "Checking if RoleBinding VNFLCM service exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get rolebinding | grep "$NAMESPACE-eric-vnflcm-service-scc-binding"
  if [[ $? == 1 ]]; then
    echo "Creating RoleBinding VNFLCM service"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: $NAMESPACE-eric-vnflcm-service-scc-binding
  namespace: $NAMESPACE
subjects:
  - kind: ServiceAccount
    name: eric-vnflcm-service-sa
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: $NAMESPACE-eric-vnflcm-service-custom-role
EOF
  else
    echo "RoleBinding VNFLCM service already created"
  fi
}

function createAllVnflcmService() {
  createSCCVnflcmService
  createRoleVnflcmService
  createRoleBindingVnflcmService
}







function createRestrictedRole() {
  echo "Checking if restricted scc role exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get role | grep "$NAMESPACE-evnfm-clusterrole-restricted"
  if [[ $? == 1 ]]; then
    echo "Creating restricted scc role"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: $NAMESPACE-evnfm-clusterrole-restricted
  annotations:
    meta.helm.sh/release-namespace: $NAMESPACE
rules:
- apiGroups:
  - security.openshift.io
  resourceNames:
  - restricted
  resources:
  - securitycontextconstraints
  verbs:
  - use
EOF
  else
    echo "Restricted scc role already exists"
  fi
}

function createRestrictedRoleBinding() {
  echo "Checking if restricted scc rolebinding exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get role | grep "$$NAMESPACE-evnfm-scc-clusterrolebinding"
  if [[ $? == 1 ]]; then
    echo "Creating restricted scc role"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: $NAMESPACE-evnfm-scc-clusterrolebinding
  annotations:
    meta.helm.sh/release-namespace: $NAMESPACE
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: $NAMESPACE-evnfm-clusterrole-restricted

subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: system:serviceaccounts:$NAMESPACE
EOF
  else
    echo "Restricted scc rolebinding already exists"
  fi
}

function createAllSCCRestrictedRole() {
  createRestrictedRole
  createRestrictedRoleBinding
}



function createSCCSearchEngine() {
  echo "Checking if scc Search Enging exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get scc | grep 'custom-search-engine-scc'
  if [[ $? == 1 ]]; then
    echo "Creating scc Search Enging"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
allowHostDirVolumePlugin: false
allowHostIPC: false
allowHostNetwork: false
allowHostPID: false
allowHostPorts: false
allowPrivilegeEscalation: true
allowPrivilegedContainer: true
allowedUnsafeSysctls:
- vm.max_map_count
apiVersion: security.openshift.io/v1
fsGroup:
  type: MustRunAs
groups: []
kind: SecurityContextConstraints
metadata:
  name:  custom-search-engine-scc
priority: 1
readOnlyRootFilesystem: false
requiredDropCapabilities:
- ALL
runAsUser:
  type: RunAsAny
seLinuxContext:
  type: RunAsAny
seccompProfiles:
- '*'
supplementalGroups:
  type: RunAsAny
users: []
volumes:
- configMap
- downwardAPI
- emptyDir
- persistentVolumeClaim
- projected
- secret
EOF
  else
    echo "scc Search Enging already created"
  fi
}

function createRoleSearchEngine() {
  echo "Checking if Role Search Enging exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get role | grep "$NAMESPACE-search-engine-custom-role"
  if [[ $? == 1 ]]; then
    echo "Creating Role Search Engine"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: $NAMESPACE-search-engine-custom-role
  namespace: $NAMESPACE
rules:
  - apiGroups:
      - security.openshift.io
    resources:
      - securitycontextconstraints
    resourceNames:
      - custom-search-engine-scc
    verbs:
      - use
EOF
  else
    echo "Role Search Enging already created"
  fi
}


function createRoleBindingSearchEngine() {
  echo "Checking if RoleBinding Search Enging exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get rolebinding | grep "$NAMESPACE-search-engine-scc-binding"
  if [[ $? == 1 ]]; then
    echo "Creating RoleBinding Search Enging"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: $NAMESPACE-search-engine-scc-binding
  namespace: $NAMESPACE
subjects:
  - kind: ServiceAccount
    name: eric-data-search-engine-sa
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: $NAMESPACE-search-engine-custom-role
EOF
  else
    echo "RoleBinding Search Enging already created"
  fi
}

function createAllSearchEngine() {
  createSCCSearchEngine
  createRoleSearchEngine
  createRoleBindingSearchEngine
}


function createSCCLogShipper() {
  echo "Checking if SCC LogShipper exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get scc | grep 'custom-log-shipper-scc'
  if [[ $? == 1 ]]; then
    echo "Creating SCC LogShipper"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
allowHostDirVolumePlugin: true
allowHostIPC: false
allowHostNetwork: false
allowHostPID: false
allowHostPorts: false
allowPrivilegeEscalation: true
allowPrivilegedContainer: true
apiVersion: security.openshift.io/v1
fsGroup:
  type: MustRunAs
groups: []
kind: SecurityContextConstraints
metadata:
  name: custom-log-shipper-scc
priority: 1
readOnlyRootFilesystem: false
requiredDropCapabilities:
- ALL
runAsUser:
  type: RunAsAny
seLinuxContext:
  type: RunAsAny
seccompProfiles:
- '*'
supplementalGroups:
  type: RunAsAny
users: []
volumes:
- configMap
- downwardAPI
- emptyDir
- hostPath
- persistentVolumeClaim
- projected
- secret
EOF
  else
    echo "SCC LogShipper already created"
  fi
}

function createRoleLogShipper() {
  echo "Checking if RoleLogShipper exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get role | grep "$NAMESPACE-log-shipper-custom-role"
  if [[ $? == 1 ]]; then
    echo "Creating Role LogShipper"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: $NAMESPACE-log-shipper-custom-role
  namespace: $NAMESPACE
rules:
  - apiGroups:
      - security.openshift.io
    resources:
      - securitycontextconstraints
    resourceNames:
      - custom-log-shipper-scc
    verbs:
      - use
EOF
  else
    echo "Role LogShipper already created"
  fi
}

function createRoleBindingLogShipper() {
  echo "Checking if RoleBinding LogShipper exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get RoleBinding | grep "$NAMESPACE-log-shipper-scc-binding"
  if [[ $? == 1 ]]; then
    echo "Creating RoleBinding LogShipper"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: $NAMESPACE-log-shipper-scc-binding
  namespace: $NAMESPACE
subjects:
  - kind: ServiceAccount
    name: eric-log-shipper
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: $NAMESPACE-log-shipper-custom-role
EOF
  else
    echo "RoleBinding LogShipper already created"
  fi
}

function createAllLogShipper() {
  createSCCLogShipper
  createRoleLogShipper
  createRoleBindingLogShipper
}


function createSCCObjectStorageMN() {
  echo "Checking if SCC ObjectStorageMN exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get scc | grep 'custom-object-storage-mn-scc'
  if [[ $? == 1 ]]; then
    echo "Creating SCC ObjectStorageMN"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
allowHostDirVolumePlugin: false
allowHostIPC: false
allowHostNetwork: false
allowHostPID: false
allowHostPorts: false
allowPrivilegeEscalation: true
allowPrivilegedContainer: false
allowedCapabilities: null
apiVersion: security.openshift.io/v1
defaultAddCapabilities: null
fsGroup:
  type: MustRunAs
groups: []
kind: SecurityContextConstraints
metadata:
  generation: 2
  name: custom-object-storage-mn-scc
priority: 1
readOnlyRootFilesystem: false
requiredDropCapabilities:
- KILL
- MKNOD
- SETUID
- SETGID
runAsUser:
  type: RunAsAny
seLinuxContext:
  type: MustRunAs
supplementalGroups:
  type: RunAsAny
users: []
volumes:
- configMap
- downwardAPI
- emptyDir
- persistentVolumeClaim
- projected
- secret
EOF
  else
    echo "SCC ObjectStorageMN already created"
  fi
}

function createRoleObjectStorageMN() {
  echo "Checking if Role ObjectStorageMN exists"
kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get role | grep "$NAMESPACE-object-storage-mn-custom-role"
  if [[ $? == 1 ]]; then
    echo "Creating Role ObjectStorageMN"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: $NAMESPACE-object-storage-mn-custom-role
  namespace: $NAMESPACE
rules:
  - apiGroups:
      - security.openshift.io
    resources:
      - securitycontextconstraints
    resourceNames:
      - custom-object-storage-mn-scc
    verbs:
      - use
EOF
  else
    echo "Role ObjectStorageMN already created"
  fi
}

function createRoleBindingObjectStorageMN() {
  echo "Checking if RoleBinding ObjectStorageMN exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get rolebinding | grep "$NAMESPACE-object-storage-mn-scc-binding"
  if [[ $? == 1 ]]; then
    echo "Creating RoleBinding ObjectStorageMN"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: $NAMESPACE-object-storage-mn-scc-binding
  namespace: $NAMESPACE
subjects:
  - kind: ServiceAccount
    name: eric-data-object-storage-mn
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: $NAMESPACE-object-storage-mn-custom-role
EOF
  else
    echo "RoleBinding ObjectStorageMN already created"
  fi
}

function createAllObjectStorageMN() {
  createSCCObjectStorageMN
  createRoleObjectStorageMN
  createRoleBindingObjectStorageMN
}



function createSCCDatabasePG() {
  echo "Checking if scc Database PG exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get scc | grep 'custom-document-db-pg-scc'
  if [[ $? == 1 ]]; then
    echo "Creating scc Database PG"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -

allowHostPorts: false
priority: null
requiredDropCapabilities:
  - KILL
  - MKNOD
  - SETUID
  - SETGID
allowPrivilegedContainer: false
runAsUser:
  type: RunAsAny
users: []
allowHostDirVolumePlugin: false
allowHostIPC: false
seLinuxContext:
  type: MustRunAs
readOnlyRootFilesystem: false
fsGroup:
  type: MustRunAs
groups: []
priority: 1
kind: SecurityContextConstraints
metadata:
  name: custom-document-db-pg-scc
defaultAddCapabilities: null
supplementalGroups:
  type: RunAsAny
volumes:
  - configMap
  - downwardAPI
  - emptyDir
  - persistentVolumeClaim
  - projected
  - secret
allowHostPID: false
allowHostNetwork: false
allowPrivilegeEscalation: true
apiVersion: security.openshift.io/v1
allowedCapabilities: null
EOF
  else
    echo "scc Database PG already created"
  fi
}


function createRoleDatabasePG() {
  echo "Checking if Role Database PG exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get role | grep "$NAMESPACE-document-db-pg-custom-role"
  if [[ $? == 1 ]]; then
    echo "Creating Role Database PG"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -

apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: $NAMESPACE-document-db-pg-custom-role
  namespace: $NAMESPACE
rules:
  - apiGroups:
      - security.openshift.io
    resources:
      - securitycontextconstraints
    resourceNames:
      - custom-document-db-pg-scc
    verbs:
      - use
EOF
  else
    echo "Role for Database PG already created"
  fi
}

function createRoleBindingAllPGServiceAccounts() {
  echo "Checking if RoleBinding AllPGServiceAccounts exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get rolebinding | grep "$NAMESPACE-document-db-pg-scc-binding"
  if [[ $? == 1 ]]; then
    echo "Creating RoleBinding for All PGServiceAccounts"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -

kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: $NAMESPACE-document-db-pg-scc-binding
  namespace: $NAMESPACE
subjects:
  - kind: ServiceAccount
    name: eric-lm-combined-server-db-pg-sa
  - kind: ServiceAccount
    name: eric-cm-mediator-db-pg-sa
  - kind: ServiceAccount
    name: idam-database-pg-sa
  - kind: ServiceAccount
    name: eric-fh-alarm-handler-db-pg-sa
  - kind: ServiceAccount
    name: eric-oss-common-postgres-sa
  - kind: ServiceAccount
    name: application-manager-postgres-sa
  - kind: ServiceAccount
    name: eric-vnflcm-db-sa
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: $NAMESPACE-document-db-pg-custom-role
EOF
  else
    echo "RoleBinding AllPGServiceAccounts already created"
  fi
}

#ServiceMesh
function createSCCServiceMeshSideCar() {
  echo "Checking if scc Service Mesh SideCar exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get scc | grep "$NAMESPACE-custom-service-mesh-sidecar-scc"
  if [[ $? == 1 ]]; then
    echo "Creating scc Service Mesh SideCar"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -

allowHostDirVolumePlugin: true
allowHostIPC: false
allowHostNetwork: false
allowHostPID: false
allowHostPorts: false
allowPrivilegeEscalation: false
allowPrivilegedContainer: false
allowedCapabilities:
- NET_ADMIN
- NET_RAW
apiVersion: security.openshift.io/v1
fsGroup:
  type: RunAsAny
groups: []
kind: SecurityContextConstraints
metadata:
  name: $NAMESPACE-custom-service-mesh-sidecar-scc
  annotations:
    meta.helm.sh/release-namespace: $NAMESPACE
priority: null
readOnlyRootFilesystem: false
requiredDropCapabilities:
- AUDIT_CONTROL
- AUDIT_WRITE
- BLOCK_SUSPEND
- CHOWN
- DAC_OVERRIDE
- DAC_READ_SEARCH
- FOWNER
- FSETID
- IPC_LOCK
- IPC_OWNER
- KILL
- LEASE
- LINUX_IMMUTABLE
- MAC_ADMIN
- MAC_OVERRIDE
- MKNOD
- NET_BIND_SERVICE
- NET_BROADCAST
- SETFCAP
- SETGID
- SETPCAP
- SETUID
- SYSLOG
- SYS_ADMIN
- SYS_BOOT
- SYS_CHROOT
- SYS_MODULE
- SYS_NICE
- SYS_PACCT
- SYS_PTRACE
- SYS_RAWIO
- SYS_RESOURCE
- SYS_TIME
- SYS_TTY_CONFIG
- WAKE_ALARM
runAsUser:
  type: RunAsAny
seLinuxContext:
  type: RunAsAny
seccompProfiles:
- '*'
supplementalGroups:
  type: RunAsAny
users: []
volumes:
- configMap
- downwardAPI
- emptyDir
- persistentVolumeClaim
- projected
- secret
EOF
  else
    echo "scc Service Mesh SideCar already created"
  fi
}

function createClusterRoleServiceMeshSideCar() {
  echo "Checking if ClusterRole Service Mesh SideCar exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get clusterrole | grep "$NAMESPACE-custom-service-mesh-sidecar-clusterrole"
  if [[ $? == 1 ]]; then
    echo "Creating ClusterRole Service Mesh SideCar"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
 name: $NAMESPACE-custom-service-mesh-sidecar-clusterrole
 annotations:
    meta.helm.sh/release-namespace: $NAMESPACE
rules:
- apiGroups:
  - security.openshift.io
  resourceNames:
  - $NAMESPACE-custom-service-mesh-sidecar-scc
  resources:
  - securitycontextconstraints
  verbs:
  - use
EOF
  else
    echo "ClusterRole Service Mesh SideCar already created"
  fi
}

function createRoleBindingAllServiceMeshSideCarServiceAccounts() {
  echo "Checking if RoleBinding AllServiceMeshSideCarServiceAccounts exists"
  kubectl --kubeconfig "$KUBECONFIG" -n "$NAMESPACE" get rolebinding | grep "$NAMESPACE-custom-service-mesh-sidecar-rolebinding"
  if [[ $? == 1 ]]; then
    echo "Creating RoleBinding AllServiceMeshSideCarServiceAccounts"
    cat <<EOF | kubectl --kubeconfig "$KUBECONFIG" apply -n "$NAMESPACE" -f -

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: $NAMESPACE-custom-service-mesh-sidecar-rolebinding
  annotations:
    meta.helm.sh/release-namespace: $NAMESPACE
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: $NAMESPACE-custom-service-mesh-sidecar-clusterrole
subjects:
  - kind: ServiceAccount
    name: eric-am-common-wfs-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-am-common-wfs-ui-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-am-onboarding-service-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-eo-api-gateway-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-eo-evnfm-crypto-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-eo-evnfm-nbi
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-eo-lm-consumer-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-eo-usermgmt-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-eo-usermgmt-ui-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-vnfm-orchestrator-service-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: evnfm-toscao-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-eo-common-br-agent-sa
    namespace: $NAMESPACE
  - kind: ServiceAccount
    name: eric-eo-fh-event-to-alarm-adapter-sa
    namespace: $NAMESPACE

EOF
  else
    echo "RoleBinding for all Service mesh ServiceAccounts already created"
  fi
}
function createAllServiceMeshSCCSideCar() {
  createSCCServiceMeshSideCar
  createClusterRoleServiceMeshSideCar
  createRoleBindingAllServiceMeshSideCarServiceAccounts
}

function createAllSCCDatabasePG() {
  createSCCDatabasePG
  createRoleDatabasePG
  createRoleBindingAllPGServiceAccounts
}

createAllSCCRestrictedRole
createAllSearchEngine
createAllVnflcmService
createAllLogShipper
createAllObjectStorageMN
createAllSCCDatabasePG
createAllServiceMeshSCCSideCar