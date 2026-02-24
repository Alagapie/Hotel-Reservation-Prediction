pipeline {
    agent any

    environment {
        IMAGE_NAME = "hotelreservationapp"                 // Docker image name
        ACR_LOGIN_SERVER = "hotelreservation.azurecr.io"  // Your ACR login server
        ACR_CREDENTIALS_ID = "acr-admin-credentials"     // Jenkins credential ID for ACR admin
        RESOURCE_GROUP = "project-1"
        WEBAPP_NAME = "hotelreservationapp"              // Your Web App name
    }

    stages {

        stage('Clone Repo') {
            steps {
                echo 'Cloning GitHub repo'
                checkout scmGit(branches: [[name: '*/main']], 
                    extensions: [], 
                    userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Alagapie/Hotel-Reservation-Prediction.git']]
                )
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image'
                sh """
                docker build -t ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Login to ACR') {
            steps {
                echo 'Logging into Azure Container Registry'
                withCredentials([usernamePassword(credentialsId: "${ACR_CREDENTIALS_ID}", 
                                                 usernameVariable: 'ACR_USERNAME', 
                                                 passwordVariable: 'ACR_PASSWORD')]) {
                    sh """
                    echo $ACR_PASSWORD | docker login ${ACR_LOGIN_SERVER} -u $ACR_USERNAME --password-stdin
                    """
                }
            }
        }

        stage('Push Image to ACR') {
            steps {
                echo 'Pushing Docker image to Azure Container Registry'
                sh """
                docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Deploy to Azure Web App') {
            steps {
                echo 'Deploying Docker image to Azure Web App'
                withCredentials([usernamePassword(credentialsId: "${ACR_CREDENTIALS_ID}", 
                                                 usernameVariable: 'ACR_USERNAME', 
                                                 passwordVariable: 'ACR_PASSWORD')]) {
                    sh """
                    az webapp config container set \
                        --name ${WEBAPP_NAME} \
                        --resource-group ${RESOURCE_GROUP} \
                        --docker-custom-image-name ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest \
                        --docker-registry-server-url https://${ACR_LOGIN_SERVER} \
                        --docker-registry-server-user $ACR_USERNAME \
                        --docker-registry-server-password $ACR_PASSWORD
                    """
                }
            }
        }
    }
}