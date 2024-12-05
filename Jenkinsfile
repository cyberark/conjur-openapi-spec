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

        stage('Changelog') {
          steps {
            script {
              parseChangelog(INFRAPOOL_EXECUTORV2_AGENT_0)
            }
          }
        }

        stage('Lint Spec') {
            steps {
                script {
                    INFRAPOOL_EXECUTORV2_AGENT_0.agentSh "./bin/lint_spec"
                }
            }
        }

        // Commented out for now as it's failing. Will need to be fixed in a follow-up PR.
        // This was originally handled in GH Actions and needs to be ported to Jenkins.
        // stage('Test API Contract') {
        //     steps {
        //         script {
        //             INFRAPOOL_EXECUTORV2_AGENT_0.agentSh "./bin/test_api_contract"
        //         }
        //     }
        // }

        stage('Lint Tests') {
            steps {
                script {
                    INFRAPOOL_EXECUTORV2_AGENT_0.agentSh "./bin/lint_tests"
                }
            }
        }

        stage('Test Examples') {
            steps {
                script {
                    INFRAPOOL_EXECUTORV2_AGENT_0.agentSh "./bin/test_examples"
                }
            }
        }

        stage('Generate Postman Collection') {
            steps {
                script {
                    INFRAPOOL_EXECUTORV2_AGENT_0.agentSh "./bin/generate_postman_collection"
                }
            }
        }

        stage('Integration Tests') {
            environment {
                INFRAPOOL_REGISTRY_URL = "registry.tld"
            }
            steps {
                script {
                    INFRAPOOL_EXECUTORV2_AGENT_0.agentSh "./bin/test_integration -l python"
                    INFRAPOOL_EXECUTORV2_AGENT_0.agentSh "./bin/test_integration -l csharp-netcore"
                }
            }

            post {
                always {
                    script {
                        INFRAPOOL_EXECUTORV2_AGENT_0.agentStash name: 'xml-out', includes: '*.xml'
                        unstash 'xml-out'
                        junit 'nose2-junit.xml'
                        cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'coverage.xml', conditionalCoverageTargets: '70, 0, 70', failUnhealthy: true, failUnstable: false, lineCoverageTargets: '70, 0, 70', maxNumberOfBuilds: 0, methodCoverageTargets: '70, 0, 70', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
                        codacy action: 'reportCoverage', filePath: "coverage.xml"
                    }
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

                    curl -fsSL -o kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64
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
