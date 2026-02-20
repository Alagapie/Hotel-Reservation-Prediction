import pandas as pd
import matplotlib.pyplot as plt
import os
import joblib
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml , load_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
logger = get_logger(__name__)

class DataProcessor:
    

    def __init__(self, train_path,  processed_dir,test_path, config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir
        self.config = read_yaml(config_path)


        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
    def preprocess_data(self,df):
        try:
            logger.info('starting our preprocessing step')

            logger.info('dropping unneccessary columns')
            df=df.drop(columns=['Unnamed: 0','Booking_ID'])
            df = df.drop_duplicates()


            cat_cols = self.config['data_processing']['categorical_columns']
            num_cols = self.config['data_processing']['numerical_columns']

            logger.info('label encoding the target colums')
            self.le= LabelEncoder()
            df['booking_status'] = self.le.fit_transform(df['booking_status'])
            class_mapping = dict(zip(self.le.classes_, self.le.transform(self.le.classes_)))
            logger.info(f'Label mapping are : {class_mapping}')

            X = df.drop(columns=['booking_status'])
            y = df['booking_status']

            

            logger.info('Scaling and encdoing our dataset')
            standardscaler= StandardScaler()
            onehot=OneHotEncoder(handle_unknown='ignore', sparse_output=False)
            self.processor = ColumnTransformer(transformers=[
                ('num',standardscaler,num_cols),
                ('cat',onehot,cat_cols)
            ])
           
            X_processed = self.processor.fit_transform(X)
          
            
            
            num_col_names = num_cols
            cat_col_names = self.processor.named_transformers_['cat'].get_feature_names_out(cat_cols)
            self.all_col_names = list(num_col_names) + list(cat_col_names)

            return X_processed, y
    


        except Exception as e:
            logger.error('error while preprocessing the data')
            raise CustomException('failed to preprocess the data', e)
    def preprocess_test_data(self,df):
        try:
            logger.info('starting our preprocessing step')

            logger.info('dropping unneccessary columns')
            df=df.drop(columns=['Unnamed: 0','Booking_ID'])
            


           

            logger.info('label encoding the target colums')
           
            df['booking_status'] = self.le.transform(df['booking_status'])
            

            X = df.drop(columns=['booking_status'])
            y = df['booking_status']

            

            logger.info('Scaling and encdoing our dataset')
            
           
           
            X_processed = self.processor.transform(X)
          
            
            
            

            return X_processed, y
    


        except Exception as e:
            logger.error('error while preprocessing the data')
            raise CustomException('failed to preprocess the data', e)
    
    def balanced(self,X,y):
        try:
          logger.info('Balancing data')
          sm=SMOTE(random_state=42)
          X= X
          y= y
          X_balanced,y_balanced = sm.fit_resample(X,y)
         
          return X_balanced, y_balanced
        except Exception as e:
            logger.error('errror')
            raise CustomException('failed during balancing', e)
    
    
    def save_processed_data(self,X, y,X_test, Y_test,train_filepath,test_filepath):
        try:
            logger.info('converting the processed data into Dataframe')
            train_data= pd.DataFrame(X, columns=self.all_col_names)
            train_data['booking_status'] = y
            test_data = pd.DataFrame(X_test, columns=self.all_col_names)
            test_data['booking_status'] = Y_test

            logger.info('saving the processed data to csv files')
            train_data.to_csv(train_filepath, index=False)
            test_data.to_csv(test_filepath, index=False)
            logger.info('processed data saved sucessfully')
        except Exception as e:
            logger.error('error while  saving the processed data')
            raise CustomException('failed to save the processed data', e)
        
    def process(self):
        try:
            logger.info('loading the raw data directory')
            train_df = load_data(self.train_path)
            X_train, y_train = self.preprocess_data(train_df)
            X_train, y_train = self.balanced(X_train, y_train)
            test_df = load_data(self.test_path)
            X_test, Y_test = self.preprocess_test_data(test_df)
            
            self.save_processed_data(X_train, y_train, X_test, Y_test, PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH)
            joblib.dump(self.processor, "artifacts/preprocessor.pkl")
            joblib.dump(self.le, "artifacts/label_encoder.pkl")
   
            logger.info('data processing completed successfully')
        except CustomException as e:
            logger.error(f"error during data processing ")
            raise CustomException('failed to process the data', e)
if __name__ == "__main__":
    processor = DataProcessor(train_path=TRAIN_FILE_PATH, test_path=TEST_FILE_PATH, processed_dir=PROCESSED_DIR, config_path=CONFIG_PATH)
    processor.process()
    
   