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
          docker build -t nlcr/wa-kat:${GIT_COMMIT} .
          docker tag nlcr/wa-kat:${GIT_COMMIT} nlcr/wa-kat:latest
          docker tag nlcr/wa-kat:${GIT_COMMIT} nlcr/wa-kat:${WAKAT_VERSION}
          docker push nlcr/wa-kat:${GIT_COMMIT}
          docker push nlcr/wa-kat:${WAKAT_VERSION}
          docker push nlcr/wa-kat:latest
          '''
        }
    }
    stage('Inspect image') {
      steps {sh 'docker push nlcr/wa-kat:${GIT_COMMIT}'}
    }
  }
}
