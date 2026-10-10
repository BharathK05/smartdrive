# Jenkins plus the tools the SmartDrive pipeline needs: Python (tests), SSH (deploy) and Terraform (AWS).
FROM jenkins/jenkins:lts-jdk21

ARG TERRAFORM_VERSION=1.16.5

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv openssh-client curl unzip \
 && rm -rf /var/lib/apt/lists/* \
 && ARCH="$(dpkg --print-architecture)" \
 && curl -fsSL -o /tmp/terraform.zip \
      "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_${ARCH}.zip" \
 && unzip -q /tmp/terraform.zip terraform -d /usr/local/bin \
 && rm /tmp/terraform.zip
USER jenkins
