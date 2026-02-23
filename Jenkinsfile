pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        AZURE_REGISTRY = "myregistry.azurecr.io"
        IMAGE_NAME = "ml-project:latest"
        RESOURCE_GROUP = "myResourceGroup"
        APP_NAME = "mlprojectapp"
    }

    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Alagapie/Hotel-Reservation-Prediction.git']])
                }
            }
        }

        stage('Setting up Virtual Environment and Installing dependencies') {
            steps {
                script {
                    echo 'Setting up Virtual Environment............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Building and Pushing Docker Image to ACR') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'azure-creds',
                                                 usernameVariable: 'AZURE_CLIENT_ID',
                                                 passwordVariable: 'AZURE_CLIENT_SECRET')]) {
                    script {
                        echo 'Building and Pushing Docker Image to ACR.............'
                        sh '''
                        az login --service-principal \
                          -u $AZURE_CLIENT_ID \
                          -p $AZURE_CLIENT_SECRET \
                          --tenant <tenant-id>

                        az acr login --name myregistry

                        docker build -t ${AZURE_REGISTRY}/${IMAGE_NAME} .
                        docker push ${AZURE_REGISTRY}/${IMAGE_NAME}
                        '''
                    }
                }
            }
        }

        stage('Deploy to Azure Web App for Containers') {
            steps {
                script {
                    echo 'Deploying to Azure Web App.............'
                    sh '''
                    az webapp create \
                      --resource-group ${RESOURCE_GROUP} \
                      --plan myAppServicePlan \
                      --name ${APP_NAME} \
                      --deployment-container-image-name ${AZURE_REGISTRY}/${IMAGE_NAME}
                    '''
                }
            }
        }
    }
}
