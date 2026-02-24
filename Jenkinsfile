// pipeline {
//     agent any

//     environment {
//         IMAGE_NAME = "hotelreservationapp"                 // Docker image name
//         ACR_LOGIN_SERVER = "hotelreservation.azurecr.io"  // Your ACR login server
//         ACR_CREDENTIALS_ID = "acr-admin-credentials"     // Jenkins credential ID for ACR admin
//         RESOURCE_GROUP = "project-1"
//         WEBAPP_NAME = "hotelreservationapp"              // Your Web App name
//     }

//     stages {

//         stage('Clone Repo') {
//             steps {
//                 echo 'Cloning GitHub repo'
//                 checkout scmGit(branches: [[name: '*/main']], 
//                     extensions: [], 
//                     userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Alagapie/Hotel-Reservation-Prediction.git']]
//                 )
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 echo 'Building Docker image'
//                 sh """
//                 docker build -t ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest .
//                 """
//             }
//         }

//         stage('Login to ACR') {
//             steps {
//                 echo 'Logging into Azure Container Registry'
//                 withCredentials([usernamePassword(credentialsId: "${ACR_CREDENTIALS_ID}", 
//                                                  usernameVariable: 'ACR_USERNAME', 
//                                                  passwordVariable: 'ACR_PASSWORD')]) {
//                     sh """
//                     echo $ACR_PASSWORD | docker login ${ACR_LOGIN_SERVER} -u $ACR_USERNAME --password-stdin
//                     """
//                 }
//             }
//         }

//         stage('Push Image to ACR') {
//             steps {
//                 echo 'Pushing Docker image to Azure Container Registry'
//                 sh """
//                 docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest
//                 """
//             }
//         }

//         stage('Deploy to Azure Web App') {
//             steps {
//                 echo 'Deploying Docker image to Azure Web App'
//                 withCredentials([usernamePassword(credentialsId: "${ACR_CREDENTIALS_ID}", 
//                                                  usernameVariable: 'ACR_USERNAME', 
//                                                  passwordVariable: 'ACR_PASSWORD')]) {
//                     sh """
//                     az webapp config container set \
//                         --name ${WEBAPP_NAME} \
//                         --resource-group ${RESOURCE_GROUP} \
//                         --docker-custom-image-name ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest \
//                         --docker-registry-server-url https://${ACR_LOGIN_SERVER} \
//                         --docker-registry-server-user $ACR_USERNAME \
//                         --docker-registry-server-password $ACR_PASSWORD
//                     """
//                 }
//             }
//         }
//     }
// }


pipeline {
    agent any

    environment {
        // --- CONFIGURATION ---
        IMAGE_NAME         = "hotelreservationapp" 
        ACR_LOGIN_SERVER   = "hotelreservation.azurecr.io"
        ACR_CREDENTIALS_ID = "acr-admin-credentials" // Ensure this ID matches your Jenkins Credentials store
        RESOURCE_GROUP     = "project-1"
        WEBAPP_NAME        = "hotelreservationapp"
        
        // --- APP SETTINGS ---
        // Change APP_PORT to 5000 if your Python app is NOT using 80
        APP_PORT           = "80" 
    }

    stages {
        stage('Clone Repo') {
            steps {
                script {
                    echo 'Cleaning workspace and cloning GitHub repo...'
                    checkout scmGit(
                        branches: [[name: '*/main']], 
                        extensions: [], 
                        userRemoteConfigs: [[
                            credentialsId: 'github-token', 
                            url: 'https://github.com/Alagapie/Hotel-Reservation-Prediction.git'
                        ]]
                    )
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${IMAGE_NAME}"
                    // Builds the image with the ACR tag directly
                    sh "docker build -t ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest ."
                }
            }
        }

        stage('Login & Push to ACR') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${ACR_CREDENTIALS_ID}", 
                    usernameVariable: 'ACR_USERNAME', 
                    passwordVariable: 'ACR_PASSWORD'
                )]) {
                    script {
                        echo 'Logging into Azure Container Registry...'
                        sh "echo ${ACR_PASSWORD} | docker login ${ACR_LOGIN_SERVER} -u ${ACR_USERNAME} --password-stdin"
                        
                        echo 'Pushing image to ACR...'
                        sh "docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Deploy to Azure Web App') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${ACR_CREDENTIALS_ID}", 
                    usernameVariable: 'ACR_USERNAME', 
                    passwordVariable: 'ACR_PASSWORD'
                )]) {
                    script {
                        echo 'Syncing Web App with ACR and setting Environment Variables...'
                        
                        // 1. Point Web App to the new image and provide credentials
                        sh """
                        az webapp config container set \
                            --name ${WEBAPP_NAME} \
                            --resource-group ${RESOURCE_GROUP} \
                            --docker-custom-image-name ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest \
                            --docker-registry-server-url https://${ACR_LOGIN_SERVER} \
                            --docker-registry-server-user ${ACR_USERNAME} \
                            --docker-registry-server-password ${ACR_PASSWORD}
                        """

                        // 2. Set Critical App Settings
                        // WEBSITES_PORT: Tells Azure which port the container is listening on
                        // WEBSITES_CONTAINER_START_TIME_LIMIT: Gives your AI model up to 30 mins to load before timing out
                        sh """
                        az webapp config appsettings set \
                            --resource-group ${RESOURCE_GROUP} \
                            --name ${WEBAPP_NAME} \
                            --settings WEBSITES_PORT=${APP_PORT} \
                                       WEBSITES_CONTAINER_START_TIME_LIMIT=1800
                        """

                        echo 'Restarting Web App to apply changes...'
                        sh "az webapp restart --name ${WEBAPP_NAME} --resource-group ${RESOURCE_GROUP}"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Deployment successful! App URL: https://${WEBAPP_NAME}.azurewebsites.net"
        }
        failure {
            echo "Deployment failed. Check the Jenkins console and Azure Log Stream."
        }
    }
}
