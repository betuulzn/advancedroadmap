pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
        // Two pushes to the same PR within seconds shouldn't race on the same workspace
        disableConcurrentBuilds()
    }

    environment {
        GITHUB_CHECK_CONTEXT = 'jenkins/ui-tests'
        VENV_DIR             = '.venv'
    }

    stages {

        stage('Notify: pending') {
            steps {
                githubNotify(
                    context: env.GITHUB_CHECK_CONTEXT,
                    description: 'UI test suite running...',
                    status: 'PENDING'
                )
            }
        }

        stage('Setup environment') {
            steps {
                sh '''
                    python3 -m venv "$VENV_DIR"
                    . "$VENV_DIR/bin/activate"
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run UI tests') {
            matrix {
                axes {
                    axis {
                        name 'BROWSER'
                        values 'chrome', 'firefox'
                    }
                }
                stages {
                    stage('pytest') {
                        steps {
                            sh '''
                                . "$VENV_DIR/bin/activate"
                                mkdir -p "reports/$BROWSER" "screenshots/$BROWSER" "logs/$BROWSER"
                                SCREENSHOT_DIR="screenshots/$BROWSER" LOG_DIR="logs/$BROWSER" \
                                pytest tests/ \
                                    --browser="$BROWSER" \
                                    --headless \
                                    --junitxml="reports/$BROWSER/junit.xml" \
                                    --html="reports/$BROWSER/report.html" \
                                    --self-contained-html \
                                    -v
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // Feeds Jenkins' native Test Result Trend graph + marks build UNSTABLE on failures
            junit testResults: 'reports/*/junit.xml', allowEmptyResults: true

            // Screenshots, HTML reports and logs for every browser axis, for any build outcome
            archiveArtifacts artifacts: 'reports/**, screenshots/**, logs/**',
                              allowEmptyArchive: true,
                              fingerprint: true

            publishHTML(target: [
                reportDir            : 'reports/chrome',
                reportFiles          : 'report.html',
                reportName           : 'Chrome Test Report',
                keepAll              : true,
                alwaysLinkToLastBuild: true,
                allowMissing         : true
            ])
            publishHTML(target: [
                reportDir            : 'reports/firefox',
                reportFiles          : 'report.html',
                reportName           : 'Firefox Test Report',
                keepAll              : true,
                alwaysLinkToLastBuild: true,
                allowMissing         : true
            ])
        }
        success {
            githubNotify(context: env.GITHUB_CHECK_CONTEXT, description: 'All UI tests passed', status: 'SUCCESS')
        }
        unstable {
            githubNotify(context: env.GITHUB_CHECK_CONTEXT, description: 'UI tests failed - see test report', status: 'FAILURE')
        }
        failure {
            githubNotify(context: env.GITHUB_CHECK_CONTEXT, description: 'Pipeline failed', status: 'FAILURE')
        }
        cleanup {
            cleanWs()
        }
    }
}
