#!/usr/bin/env groovy

pipeline {
    agent { label 'executor-v2' }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    triggers {
        cron(getDailyCronString())
    }

    stages {
        stage('Enterprise Integration Tests') {
            steps {
                script {
                    sh "./bin/test_integration -e -l python"
                }
            }
        }

        stage('Integration Tests') {
            steps {
                script {
                    ccCoverage.dockerPrep()
                    sh './bin/test_integration -l python'
                }
            }

            post {
                always {
                    junit 'nose2-junit.xml'
                    cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'coverage.xml', conditionalCoverageTargets: '75, 0, 75', failUnhealthy: true, failUnstable: false, lineCoverageTargets: '75, 0, 75', maxNumberOfBuilds: 0, methodCoverageTargets: '75, 0, 75', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
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

        stage('K8s Inject Test') {
            when {
                anyOf {
                    expression {
                        sh(returnStatus: true, script: 'git diff origin/main --name-only | grep --quiet "^test/python/k8s/.*"') == 0
                    }
                    expression {
                        sh(returnStatus: true, script: 'git diff origin/main --name-only | grep --quiet "spec/authentication.yaml"') == 0
                    }
                }
            }
            steps {
                sh '''
                curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
                chmod 700 get_helm.sh
                ./get_helm.sh

                curl -fsSL -o kind https://kind.sigs.k8s.io/dl/v0.10.0/kind-linux-amd64
                chmod 700 kind
                sudo mv ./kind /usr/local/bin/kind

                curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

                ./test/python/k8s/start --no-regen-client
                '''
            }
        }
    }

    post {
        always {
            cleanupAndNotify(currentBuild.currentResult)
        }
    }
}
