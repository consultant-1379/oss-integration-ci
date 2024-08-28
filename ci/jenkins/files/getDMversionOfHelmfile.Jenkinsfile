#!/usr/bin/env groovy
pipeline{
    agent {
        label 'evo_docker_engine_gic'
    }
    parameters {
            string(name: 'FUNCTIONAL_USER_SECRET',
                defaultValue: 'ciloopman-user-creds')
            string(name: 'EOVERSION',
                defaultValue: '0.0.0')
            string(name: 'HELMFILE',
                defaultValue: 'eric-eo-helmfile',
                description: 'Helmfile name to get DM out of')
            }
    stages{
        stage('Get version'){
            steps{
                cleanWs()
            script{
                withCredentials([usernamePassword(credentialsId: params.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                   sh 'curl -O -u $FUNCTIONAL_USER_USERNAME:$FUNCTIONAL_USER_PASSWORD --ipv4 https://arm.seli.gic.ericsson.se/artifactory/proj-eo-drop-helm-local/${HELMFILE}/${HELMFILE}-${EOVERSION}.tgz'
                   sh 'ls -la'
                   sh 'tar -xf ${HELMFILE}-${EOVERSION}.tgz'
                   dmversion = sh(script: 'grep tag ${HELMFILE}/dm_version.yaml | awk \'{print $2}\' | sed \'s/\"//g\'', returnStdout: true)
                   def data = "DM_VERSION=" + dmversion
                   writeFile(file: 'artifact.properties', text: data)
                   archiveArtifacts 'artifact.properties'
                }
}
}
}
}
}