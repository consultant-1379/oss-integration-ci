def bob = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"
def RETRY_ATTEMPT = 1

pipeline {
    options {
        timeout(time: params.TIMEOUT ?: '3600', unit: 'SECONDS')
    }
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'IMAGE_REGISTRY', description: 'Registry for the image to be used', defaultValue: 'armdocker.rnd.ericsson.se')
        string(name: 'IMAGE_REPO_PATH', description: 'Repository Path for the image to be used', defaultValue:'proj-orchestration-so')
        string(name: 'IMAGE_NAME', description: 'Name of the image to be used', defaultValue:'keycloak-client')
        string(name: 'IMAGE_TAG', description: 'Tag/Version of the image to be used', defaultValue:'1.0.0-65')
        string(
                name: 'ARMDOCKER_USER_SECRET',
                defaultValue: 'ciloopman-docker-auth-config',
                description: 'ARM Docker secret'
        )
        string(
            name: 'GERRIT_REFSPEC',
            defaultValue: 'refs/heads/master',
            description: 'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )
        string(
            name: 'TIMEOUT',
            defaultValue: '3600',
            description: 'Time to wait in seconds before the job should timeout')
        string(
            name: 'SUBMODULE_SYNC_TIMEOUT',
            defaultValue: '60',
            description: 'Number of seconds before the submodule sync command times out')
        string(
            name: 'SUBMODULE_UPDATE_TIMEOUT',
            defaultValue: '300',
            description: 'Number of seconds before the submodule update command times out')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'evo_docker_engine',
                description: 'Specify the slave label that you want the job to run on')
    }
    environment {
        IMAGE_URL = get_image_string("${params.IMAGE_REGISTRY}", "${params.IMAGE_REPO_PATH}", "${params.IMAGE_NAME}", "${params.IMAGE_TAG}")
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
        JENKINS_USER_AGENT_HOME = store_jenkins_user_agent_home()
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('Clean Workspace') {
            environment {
                HOME = "${env.JENKINS_USER_AGENT_HOME}"
            }
            steps {
                command_timeout("${params.SUBMODULE_SYNC_TIMEOUT}", 'git submodule sync')
                command_timeout("${params.SUBMODULE_UPDATE_TIMEOUT}", 'git submodule update --init --recursive --remote --depth=1 --jobs=5 bob')
                sh "${bob} git-clean"
            }
        }
        stage('Install Docker Config') {
            steps {
                script {
                    withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                        sh 'install -m 600 -D ${DOCKERCONFIG} ${DOCKER_CONFIG}/config.json'
                    }
                }
            }
        }
        stage('Retrieve image from Docker Pull command') {
            steps {
                retry(count: 5){
                    script{
                        if (RETRY_ATTEMPT > 1) {
                            echo "Rerunning the \"Retrieve image from Docker Pull command\" stage. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                            sleep(60)
                        }
                        else {
                            echo "Running the \"Retrieve image from Docker Pull command\" stage. Try ${RETRY_ATTEMPT} of 5"
                        }
                        RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                        sh "docker pull ${IMAGE_URL}"

                        RETRY_ATTEMPT = 1
                    }
                }
            }
        }
    }
     post {
        success {
            sh "docker image rm ${IMAGE_URL}"
        }
    }
}

def get_image_string(String image_Registry, String image_Repo_Path, String image_Name, String image_Version){
    if (image_Registry != "None" && image_Repo_Path != "None" && image_Name != "None" && image_Version != "None"){
        return image_Registry + "/" + image_Repo_Path + "/" + image_Name + ':' + image_Version
    }
    return "";
}

def store_jenkins_user_agent_home() {
    String value_storage = env.HOME
    return value_storage
}

def command_timeout(time_and_unit, command) {
    /**
    Method to add a timeout to a command

    Input:
    time_and_unit: A string in the format <amount_of_time><unit_of_time> e.g. 5m for five minutes
    command: The shell command to run e.g. git submodule sync
    */

    def timeout_command = "timeout " + time_and_unit + " " + command
    def exit_status_of_command = sh(script: timeout_command, returnStatus: true)

    if (exit_status_of_command == 124) {
        echo 'The following command timed-out: ' + command
        // Fail the build
        sh(script: 'exit 124')
    }
}
