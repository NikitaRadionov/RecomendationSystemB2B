import pandas as pd
import numpy as np
from catboost import CatBoostClassifier
import pickle
from gensim.models.doc2vec import Doc2Vec,\
    TaggedDocument

from nltk.tokenize import word_tokenize
import json

class MLModel: 
    def __init__(self,model_path, region_encoder_path, supplier_encoder_path, description_model_path):
        self.model = CatBoostClassifier()
        self.model.load_model(model_path)
        self.region_encoder = json.load(open(region_encoder_path))
        self.supplier_encoder = json.load(open(supplier_encoder_path))
        self.description_model = pickle.load(open(description_model_path, 'rb'))
    def predict(self, data):
        converted_data = np.zeros(29,float)
        converted_data[0] = data["contract_amount"]
        if data['okpd2'] == "29.10":
            converted_data[1] = 1
        elif data['okpd2'] == "29.20":
            converted_data[2] = 1
        elif data['okpd2'] == "29.31":
            converted_data[3] = 1
            
            converted_data[4] = 1
        else:
            converted_data[3] = 1
            converted_data[5] = 1
        converted_data[6] = self.region_encoder[data["delivery_region"]]
        if data['law_type'] == "44_FZ":
            converted_data[7] = 1
        else:
            converted_data[7] = 0
            
        description_vectors = self.description_model.infer_vector(word_tokenize(data['description'].lower()))
        
        for i in range(len(description_vectors)):
            converted_data[i + 8] = description_vectors[i]
        
        predict_result_id = pd.Series(self.model.predict_proba(converted_data)).sort_values(ascending=False).head(5).index
        main_result = []
        for key, val in self.supplier_encoder.items():
            if val in predict_result_id:
                main_result.append(key)
        return main_result