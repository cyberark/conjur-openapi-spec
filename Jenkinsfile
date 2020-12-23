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
                script {
                    ccCoverage.dockerPrep()
                    sh './bin/integration_tests'
                }
            }

            post {
                always {
                    junit 'nose2-junit.xml'
                    cobertura autoUpdateHealth: false, autoUpdateStability: true, coberturaReportFile: 'coverage.xml', conditionalCoverageTargets: '75, 0, 75', failUnhealthy: true, failUnstable: true, lineCoverageTargets: '75, 0, 75', maxNumberOfBuilds: 0, methodCoverageTargets: '75, 0, 75', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
                    sh """
                    if [[ -x cc-test-reporter ]]; then
                      echo "cc-test-reporter binary found, reporting coverage data to code climate"
                      export GIT_COMMIT="\$(<GIT_COMMIT)"
                      export GIT_BRANCH="\$(<GIT_BRANCH)"
                      ./cc-test-reporter after-build \
                        --coverage-input-type "coverage.py"\
                        --id \$(<TRID) \
                        && echo "Successfully Reported Coverage Data"
                    else
                      echo "cc-test-reporter binary not found, not reporting coverage data to code climate"
                    fi
                    """
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
