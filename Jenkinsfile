pipeline {
  agent any
    stages {
      stage('Build images and push them to Dockerhub') {
        when {
          anyOf { branch 'master'; branch 'production'; branch 'feature/*' }
        }
        steps {
          sh '''#!/usr/bin/env bash
            # Make Bash Great Again
            set -o errexit # exit when a command fails.
            set -o nounset # exit when using undeclared variables
            set -o pipefail # catch non-zero exit code in pipes
            # set -o xtrace # uncomment for bug hunting

            # Code below blocked by https://github.com/WebarchivCZ/WA-KAT/issues/107
            # docker build -t webarchiv/kat:develop -t webarchiv/kat:latest -t webarchiv/kat:$(git rev-parse --short HEAD) .
            # docker push webarchiv/kat:develop
            # docker push webarchiv/kat:$(git rev-parse --short HEAD)
          '''
        }
      }
      stage('Deploy to test') {
        when {
          anyOf { branch 'master'; branch 'production'; branch 'feature/*' }
        }
        environment {
                SSH_CREDS = credentials('ansible')
        }
        steps {
          sh '''#!/usr/bin/env bash
            # Make Bash Great Again
            set -o errexit # exit when a command fails.
            set -o nounset # exit when using undeclared variables
            set -o pipefail # catch non-zero exit code in pipes
            # set -o xtrace # uncomment for bug hunting

            cd ci
            ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i test --private-key ${SSH_CREDS} -u ${SSH_CREDS_USR} prepare-configuration.yml
            ssh -o "StrictHostKeyChecking=no" -i ${SSH_CREDS} ${SSH_CREDS_USR}@10.3.0.110 sudo /home/ansible/wakat/run.sh

          '''
        }
      }
      stage('Deploy to production') {
        when {
          anyOf { branch 'production'}
        }
        environment {
                SSH_CREDS = credentials('ansible')
        }
        steps {
          sh '''#!/usr/bin/env bash
            # Make Bash Great Again
            set -o errexit # exit when a command fails.
            set -o nounset # exit when using undeclared variables
            set -o pipefail # catch non-zero exit code in pipes
            # set -o xtrace # uncomment for bug hunting

            # Code below blocked by https://github.com/WebarchivCZ/WA-KAT/issues/107
            # docker push webarchiv/kat:latest
            
            cd ci
            ansible-playbook -i prod --private-key ${SSH_CREDS} -u ${SSH_CREDS_USR} prepare-configuration.yml
            # I had issues witch docker_compose module in ansible. Thus implmentation in ssh as workaround.
            ssh -o "StrictHostKeyChecking=no" -i ${SSH_CREDS} ${SSH_CREDS_USR}@10.3.0.50 sudo /home/ansible/wakat/run.sh
          '''
        }
      }
    }
}
