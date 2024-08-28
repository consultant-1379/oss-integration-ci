#!/bin/bash
# Owner: App Staging Team PDLAPPSTAG@ericsson.com
while getopts ":c:s:" opt; do
  case ${opt} in
    c)
    CMD=$OPTARG
    ;;
    s)
    SCOPE=$OPTARG
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done
echo "command is: ${CMD}"
echo "scope is: ${SCOPE}"
case $CMD in
    "create")
    # shellcheck disable=SC2046
    docker run -u $(id -u):$(id -g) --rm -it -v "$WORKSPACE":/workdir "$DM_REPO":"$DM_VERSION" backup "$CMD" --scope "$SCOPE" -h "$HOST_URL" --name "$BACKUP_NAME" -n "$NAMESPACE" -v 4
    ;;
    "restore")
        # shellcheck disable=SC2046
        docker run -u $(id -u):$(id -g) --rm -it -v "$WORKSPACE":/workdir "$DM_REPO":"$DM_VERSION" "$CMD" --scope "$SCOPE" -h "$HOST_URL" --name "$BACKUP_NAME" -n "$NAMESPACE" -v 4
    ;;
    "import")
        # shellcheck disable=SC2046
        docker run -u $(id -u):$(id -g) --rm -it -v "$WORKSPACE":/workdir "$DM_REPO":"$DM_VERSION" backup "$CMD" --scope "$SCOPE" -h "$HOST_URL" --name "$BACKUP_NAME" -d "$SFTP_SERVER_PATH" -n "$NAMESPACE" -v 4
    ;;
    "export")
        # shellcheck disable=SC2046
        docker run -u $(id -u):$(id -g) --rm -it -v "$WORKSPACE":/workdir "$DM_REPO":"$DM_VERSION" backup "$CMD" --scope "$SCOPE" -h "$HOST_URL" --name "$BACKUP_NAME" -d "$SFTP_SERVER_PATH" -n "$NAMESPACE" -v 4
    ;;
    *)
        echo "unknown command"
        exit 1
    ;;
esac
