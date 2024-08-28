pipeline {
    agent {
        label 'evo_docker_engine_gic'
    }
    parameters {
        string(name: 'CHART_VERSION', description: 'Number of current sprint')
    }
    stages {
        stage('Handle site_values') {
            steps {
                sh """
                    cp site-values/eo/ci/template/site-values-latest.yaml site-values/eo/ci/template/versioned/site_values_helmfile-${params.CHART_VERSION}.yaml
                    git status
                """
            }
       }
       stage('Push to master') {
            steps {
                sh """
                    git add site-values/eo/ci/template/versioned/site_values_helmfile-${params.CHART_VERSION}.yaml
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