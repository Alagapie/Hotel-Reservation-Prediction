pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }
        
    

    stages{
        stage('cloining Github repo to jenkins'){
            steps{
                script{
                    echo 'Cloning Githb repo to jenkins'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Alagapie/Hotel-Reservation-Prediction.git']])
                }
            }
        }

        stage('setting up our virtual env and installing dependecies'){
            steps{
                script{
                    echo 'setting up our virtual env and installing dependecies'
                    sh '''
                    python -m venv ${VENV_DIR}
                    .  ${VENV_DIR}/bin/activate
                    
                    pip install --upgrade pip

                    pip install -e .
                    '''

                    
                }
            }
        }
    }
}