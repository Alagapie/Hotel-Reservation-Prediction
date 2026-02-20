import os
import pandas as pd
import numpy as np
from azure.storage.blob import BlobServiceClient

from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)


class DataIngestion:

    def __init__(self,config):
        self.config = config['data_ingestion']
        self.bucket_name = self.config['container_name']
        self.file_name = self.config['file_name']
        self.train_test_ratio = self.config['train_ratio']


        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f'DataIngestion started with {self.bucket_name}')
    def download_csv_from_azure(self):
        try:
            client = BlobServiceClient.from_connection_string(self.config['connection_string'])
            bucket= client.get_container_client(self.bucket_name)
            blob = bucket.get_blob_client(self.file_name)

            download_stream = blob.download_blob()
            with open(RAW_FILE_PATH, "wb") as local_file:
             local_file.write(download_stream.readall())


            logger.info(f'Raw file is sucessfully downloaded to {RAW_FILE_PATH}')
        except Exception as e:
            logger.error(f"error while downloading the csv file: {str(e)}")

            raise CustomException('failed to download the csv file', e)
    def split_data(self):
        try:
            logger.info('starting the splitting process')
            data=pd.read_csv(RAW_FILE_PATH)
            train_data, test_data = train_test_split(data, test_size=1-self.train_test_ratio, random_state=42)
            train_data.to_csv(TRAIN_FILE_PATH)
            test_data.to_csv(TEST_FILE_PATH)

            logger.info(f'train data save to {TRAIN_FILE_PATH} and ')

        except Exception as e:
            logger.error('error while splitting the data')
            raise CustomException('failed to split the data',e )
        
    def run(self):
        try:
            logger.info('Starting data ingestion process')
            self.download_csv_from_azure()
            self.split_data()
            logger.info('Data ingestion process completed successfully')
        except CustomException as ce:
            logger.error(f'CustomException :{str(ce)}')
        finally:
            logger.info('Data ingestion process completed')
if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()