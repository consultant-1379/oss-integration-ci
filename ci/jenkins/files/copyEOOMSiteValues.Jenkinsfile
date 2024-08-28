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
                    cp site-values/eoom/ci/template/site-values-latest.yaml site-values/eoom/ci/template/versioned/site_values_helmfile-${params.CHART_VERSION}.yaml
                    cp site-values/eoom/ci/override/override-site-values-appstaging-tls-disabled.yaml site-values/eoom/ci/override/versioned/override-site-values-appstaging-tls-disabled-${params.CHART_VERSION}.yaml
                    cp site-values/eoom/ci/override/gr/FLEXI13046/site-values-override.yaml site-values/eoom/ci/override/gr/FLEXI13046/versioned/site-values-override-${params.CHART_VERSION}.yaml
                    cp site-values/eoom/ci/override/gr/FLEXI13048/site-values-override.yaml site-values/eoom/ci/override/gr/FLEXI13048/versioned/site-values-override-${params.CHART_VERSION}.yaml
                    git status
                """
            }
       }
       stage('Push to master') {
            steps {
                sh """
                    git add site-values/eoom/ci/template/versioned/site_values_helmfile-${params.CHART_VERSION}.yaml site-values/eoom/ci/override/versioned/override-site-values-appstaging-tls-disabled-${params.CHART_VERSION}.yaml site-values/eoom/ci/override/gr/FLEXI13046/versioned/site-values-override-${params.CHART_VERSION}.yaml site-values/eoom/ci/override/gr/FLEXI13048/versioned/site-values-override-${params.CHART_VERSION}.yaml
                    git commit -m "Automatic copy of site_values and overrides for previous Sprint"
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