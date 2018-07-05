// declarative pipeline
// https://jenkins.io/doc/book/pipeline/syntax/
pipeline {

  agent any
  environment {
    WAKAT_VERSION = 'git describe --abbrev=0 --tags'
  }

  stages {
    stage('Build, tag and push docker image') {
      steps {
        sh '''
          docker build -t NLCR/wa-kat:${GIT_COMMIT} .
          docker tag NLCR/wa-kat:${GIT_COMMIT} NLCR/wa-kat:latest
          docker tag NLCR/wa-kat:${GIT_COMMIT} NLCR/wa-kat:${WAKAT_VERSION}
          docker push NLCR/wa-kat:${GIT_COMMIT}
          docker push NLCR/wa-kat:${WAKAT_VERSION}
          docker push NLCR/wa-kat:latest
          '''
        }
    }
    stage('Inspect image') {
      steps {sh 'docker push NLCR/wa-kat:${GIT_COMMIT}'}
    }
  }
}
