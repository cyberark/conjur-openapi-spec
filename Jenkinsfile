#!/usr/bin/env groovy
@Library("product-pipelines-shared-library") _

pipeline {
    agent { label 'conjur-enterprise-common-agent' }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    triggers {
        cron(getDailyCronString())
    }

    environment {
        MODE = release.canonicalizeMode()

        // Ensures CI uses the internal registry for conjur edge images
        REGISTRY_URL = "registry.tld"
    }

    stages {
        stage('Scan for internal URLs') {
            steps {
                script {
                    detectInternalUrls()
                }
            }
        }
        stage('Get InfraPool Agent') {
            steps {
                script {
                    INFRAPOOL_EXECUTORV2_AGENT_0 = getInfraPoolAgent.connected(type: "ExecutorV2", quantity: 1, duration: 1)[0]
                }
            }
        }
        stage('Enterprise Integration Tests') {
            steps {
                script {
                    INFRAPOOL_EXECUTORV2_AGENT_0.agentSh "./bin/test_integration -e -l python"
                }
            }
        }

        stage('Integration Tests') {
            steps {
                script {
                    INFRAPOOL_EXECUTORV2_AGENT_0.agentSh "./bin/test_integration -l python"
                }
            }

            post {
                always {
                    script {
                        INFRAPOOL_EXECUTORV2_AGENT_0.agentStash name: 'xml-out', includes: '*.xml'
                        unstash 'xml-out'
                        junit 'nose2-junit.xml'
                        cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'coverage.xml', conditionalCoverageTargets: '75, 0, 75', failUnhealthy: true, failUnstable: false, lineCoverageTargets: '75, 0, 75', maxNumberOfBuilds: 0, methodCoverageTargets: '75, 0, 75', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
                        codacy action: 'reportCoverage', filePath: "coverage.xml"
                    }
                }
            }
        }

        stage('K8s Inject Test') {
            when {
                anyOf {
                    expression {
                        script {
                            INFRAPOOL_EXECUTORV2_AGENT_0.agentSh(returnStatus: true, script: 'git diff origin/main --name-only | grep --quiet "^test/python/k8s/.*"') == 0
                        }
                    }
                    expression {
                        script {
                            INFRAPOOL_EXECUTORV2_AGENT_0.agentSh(returnStatus: true, script: 'git diff origin/main --name-only | grep --quiet "spec/authentication.yaml"') == 0
                        }
                    }
                }
            }
            steps {
                script {
                    INFRAPOOL_EXECUTORV2_AGENT_0.agentSh '''
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
    }

    post {
        always {
            releaseInfraPoolAgent(".infrapool/release_agents")
        }
    }
}
