pipeline {
    agent any

    stages{
        stage('cloining Github repo to jenkins'){
            steps{
                script{
                    echo 'Cloning Githb repo to jenkins'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Alagapie/Hotel-Reservation-Prediction.git']])
                }
            }
        }
    }
}