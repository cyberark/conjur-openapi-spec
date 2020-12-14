#!/usr/bin/env groovy

pipeline {
    agent { label 'executor-v2' }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    stages {
        stage('Integration Tests') {
            steps {
                sh './bin/integration_tests'
            }

            post {
                always {
                    junit 'nose2-junit.xml'
                }
            }
        }

        stage('Lint Integration Tests') {
            steps {
                sh './bin/lint_tests'
            }
        }

        stage('Lint Spec File') {
            steps {
                sh './bin/lint_spec'
            }
        }
        
        stage('API Contract Test') {
            steps {
                sh './bin/api_test'
            }
        }
    }

    post {
        always {
            cleanupAndNotify(currentBuild.currentResult)
        }
    }
}
