pipeline {
    agent {
        label params.SLAVE_LABEL
    }
    parameters {
        string(name: 'CHART_VERSION', description: 'Number of current sprint')
        string(name: 'SLAVE_LABEL', defaultValue: 'evo_docker_engine_gic', description: 'Slave label to use')
    }
    stages {
        stage('Handle site_values') {
            steps {
                sh """
                    cp site-values/idun/ci/template/site-values-latest.yaml site-values/idun/ci/versioned/site-values-${params.CHART_VERSION}.yaml
                    git status
                """
            }
        }
        stage('Push to master') {
            steps {
                sh """
                    git add site-values/idun/ci/versioned/site-values-${params.CHART_VERSION}.yaml
                    git commit -m "Automatic copy of site_values for previous Sprint"
                    git push origin HEAD:refs/heads/master
                """
            }
        }
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
    }
}
