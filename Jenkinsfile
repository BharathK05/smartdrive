// SmartDrive CI/CD: every push to main -> test -> terraform apply -> deploy -> health check.
pipeline {
    agent any

    triggers {
        pollSCM('* * * * *') // check GitHub every minute (Jenkins runs on a laptop, so GitHub can't call it)
    }

    parameters {
        booleanParam(name: 'DESTROY', defaultValue: false, description: 'Delete ALL SmartDrive resources in AWS (use after the demo)')
    }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        TF_IN_AUTOMATION      = 'true'
    }

    options {
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Test') {
            when { expression { !params.DESTROY } }
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -q -r app/requirements.txt pytest
                    pytest -q app
                '''
            }
        }

        stage('Terraform') {
            steps {
                dir('terraform') {
                    sh '''
                        MY_IP=$(curl -fsS https://checkip.amazonaws.com)
                        terraform init -input=false
                        if [ "$DESTROY" = "true" ]; then
                            terraform destroy -auto-approve -input=false -var "my_ip=$MY_IP/32"
                        else
                            terraform apply -auto-approve -input=false -var "my_ip=$MY_IP/32"
                        fi
                    '''
                }
            }
        }

        stage('Deploy') {
            when { expression { !params.DESTROY } }
            steps {
                sh '''
                    APP_IP=$(terraform -chdir=terraform output -raw app_ip)
                    terraform -chdir=terraform output -raw ssh_private_key > deploy_key
                    chmod 600 deploy_key
                    SSH="ssh -i deploy_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 ec2-user@$APP_IP"

                    # A brand-new server needs a minute or two to boot and run its setup script.
                    for i in $(seq 1 30); do $SSH true && break; echo "Waiting for SSH..."; sleep 10; done
                    $SSH 'cloud-init status --wait > /dev/null' || true

                    # Copy the app code to the server, install dependencies and restart the service.
                    tar czf - -C app --exclude=__pycache__ --exclude=test_app.py . | $SSH 'tar xzf - -C /opt/smartdrive'
                    $SSH 'cd /opt/smartdrive \
                        && ([ -d venv ] || python3.11 -m venv venv) \
                        && venv/bin/pip install -q -r requirements.txt \
                        && sudo systemctl enable smartdrive \
                        && sudo systemctl restart smartdrive'
                '''
            }
        }

        stage('Health check') {
            when { expression { !params.DESTROY } }
            steps {
                sh '''
                    APP_URL=$(terraform -chdir=terraform output -raw app_url)
                    curl -fsS --retry 10 --retry-delay 5 --retry-all-errors "$APP_URL/health"
                    echo ""
                    echo "SmartDrive is live at $APP_URL"
                '''
            }
        }
    }

    post {
        always {
            sh 'rm -f deploy_key' // never leave the SSH key lying around
        }
    }
}
