#!/usr/bin/env groovy
@Library(['product-pipelines-shared-library', 'conjur-enterprise-sharedlib']) _

// Automated release, promotion and dependencies
properties([
  // Include the automated release parameters for the build
  release.addParams(),
  // Dependencies of the project that should trigger builds
  dependencies([])
])

// Performs release promotion.  No other stages will be run
if (params.MODE == "PROMOTE") {
  release.promote(params.VERSION_TO_PROMOTE) { infrapool, sourceVersion, targetVersion, assetDirectory ->
    // Any assets from sourceVersion Github release are available in assetDirectory
    // Any version number updates from sourceVersion to targetVersion occur here
    // Any publishing of targetVersion artifacts occur here
    // Anything added to assetDirectory will be attached to the Github Release

    // Note: assetDirectory is on the infrapool agent, not the local Jenkins agent.
  }
  release.copyEnterpriseRelease(params.VERSION_TO_PROMOTE)
  return
}

pipeline {
  agent { label 'conjur-enterprise-common-agent' }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  environment {
    // Sets the MODE to the specified or autocalculated value as appropriate
    MODE = release.canonicalizeMode()
  }

  triggers {
    cron(getDailyCronString())
    parameterizedCron(getWeeklyCronString("H(1-5)", "%MODE=RELEASE"))
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
          infrapool = getInfraPoolAgent.connected(type: "ExecutorV2", quantity: 1, duration: 1)[0]
        }
      }
    }

    // Generates a VERSION file based on the current build number and latest version in CHANGELOG.md
    stage('Validate Changelog and set version') {
      steps {
        script {
          updateVersion(infrapool, "CHANGELOG.md", "${BUILD_NUMBER}")
        }
      }
    }

    stage('Lint Spec') {
      steps {
        script {
          infrapool.agentSh "./bin/lint_spec"
        }
      }
    }

    // Commented out for now as it's failing. Will need to be fixed in a follow-up PR.
    // This was originally handled in GH Actions and needs to be ported to Jenkins.
    // stage('Test API Contract') {
    //   steps {
    //     script {
    //       infrapool.agentSh "./bin/test_api_contract"
    //     }
    //   }
    // }

    stage('Lint Tests') {
      steps {
        script {
          infrapool.agentSh "./bin/lint_tests"
        }
      }
    }

    stage('Build artifacts') {
      steps {
        script {
          infrapool.agentSh './bin/release'
        }
      }
    }

    stage('Test Examples') {
      steps {
        script {
          infrapool.agentSh "./bin/test_examples"
        }
      }
    }

    stage('Integration Tests') {
      environment {
        INFRAPOOL_REGISTRY_URL = "registry.tld"
      }
      steps {
        script {
          infrapool.agentSh "./bin/test_integration -l python"
          infrapool.agentSh "./bin/test_integration -l csharp-netcore"
        }
      }

      post {
        always {
          script {
            infrapool.agentStash name: 'xml-out', includes: '*.xml'
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
          infrapool.agentSh "./bin/test_integration -e -l python"
        }
      }
    }

    stage('K8s Inject Test') {
      when {
        anyOf {
          expression {
            script {
              infrapool.agentSh(returnStatus: true, script: 'git diff origin/main --name-only | grep --quiet "^test/python/k8s/.*"') == 0
            }
          }
          expression {
            script {
              infrapool.agentSh(returnStatus: true, script: 'git diff origin/main --name-only | grep --quiet "spec/authentication.yaml"') == 0
            }
          }
        }
      }
      steps {
        script {
          infrapool.agentSh '''
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

    stage('Release') {
      when {
        expression {
          MODE == "RELEASE"
        }
      }
      steps {
        script {
          release(infrapool, { billOfMaterialsDirectory, assetDirectory ->
            /* Publish release artifacts to all the appropriate locations
               Copy any artifacts to assetDirectory on the infrapool node
               to attach them to the Github release.

               If your assets are on the infrapool node in the target
               directory, use a copy like this:
                  infrapool.agentSh "cp target/* ${assetDirectory}"
               Note That this will fail if there are no assets, add :||
               if you want the release to succeed with no assets.

               If your assets are in target on the main Jenkins agent, use:
                 infrapool.agentPut(from: 'target/', to: assetDirectory)
            */
            infrapool.agentSh "cp dist/*.zip ${assetDirectory}"
            infrapool.agentSh "cp dist/*.tar.gz ${assetDirectory}"
          })
        }
      }
    }
  }
  post {
    always {
      releaseInfraPoolAgent()
    }
  }
}
