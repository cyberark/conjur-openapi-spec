#!/usr/bin/env groovy

pipeline {
    agent { label 'executor-v2' }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    stages {
        stage('Integration Test') {
            steps {
                sh './bin/integration_tests'
            }
        }
        stage('Linting') {
            steps {
                sh './bin/lint_tests'
            }
        }
    }

    post {
        always {
            cleanupAndNotify(currentBuild.currentResult)
        }
    }
}
