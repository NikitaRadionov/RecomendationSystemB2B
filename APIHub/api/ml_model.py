import pandas as pd
import numpy as np
import lightgbm as lgb
import pickle
from gensim.models.doc2vec import Doc2Vec,\
    TaggedDocument
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
import json
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
class MLModel:

    def __init__(self,model_path, region_encoder_path, supplier_encoder_path, description_model_path, supplier_data_path):
        self.model = lgb.Booster(model_file = model_path)
        self.region_encoder = json.load(open(region_encoder_path))
        self.supplier_encoder = json.load(open(supplier_encoder_path))
        self.description_model = pickle.load(open(description_model_path, 'rb'))
        self.supplier_df = pd.read_csv(supplier_data_path)
        self.supplier_df.drop(['level', 'Unnamed: 0'], axis = 1, inplace = True)
          
    def _supplier_similarity(self, df, supplier):
        price_diff = abs(df['cost'] - supplier['supplier_cost'])
        level = str(int(df['level_1_1'])) + str(int(df['level_1_2'])) + str(int(df['level_1_3'])) + str(int(df['level_2_1'])) + str(int(df['level_2_2']))
        okpd = int(supplier[f"level_{level}"] > 0)
    
        df_text = []
        supplier_text = []
        for i in range(20):
            df_text.append(df[f'title_vector_{i}'])
            supplier_text.append(supplier[f'supplier_title_vector_{i}'])
        desc_cosine_sim = cosine_similarity(np.array(df_text).reshape(1, -1), np.array(supplier_text).reshape(1, -1))[0][0]
        region = supplier[int(df['region'])]
        return [price_diff, okpd, desc_cosine_sim, region]
    
    def _get_convert_data(self, data):
        converted_data = np.zeros(27,float)
        
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
    
        description_vectors = self.description_model.infer_vector(word_tokenize(data['description'].lower()))
        
        for i in range(len(description_vectors)):
            converted_data[i + 7] = description_vectors[i]
        
        columns = ['cost','level_1_1','level_1_2','level_1_3','level_2_1','level_2_2','region', 'title_vector_0','title_vector_1','title_vector_2','title_vector_3','title_vector_4','title_vector_5', 'title_vector_6','title_vector_7','title_vector_8','title_vector_9','title_vector_10','title_vector_11','title_vector_12','title_vector_13','title_vector_14','title_vector_15','title_vector_16', 'title_vector_17', 'title_vector_18', 'title_vector_19']
        df_row = pd.DataFrame([converted_data], columns = columns)
        
        arr = []
        interact_value1 = []
        interact_value2 = []
        interact_value3 = []
        interact_value4 = []
        
        for supplier_id in self.supplier_df['supplier_id']:
            supplier_row = self.supplier_df[self.supplier_df['supplier_id']==supplier_id].rename({"supplier_id":"supplier"}, axis = 1)
            supplier_row.index = range(df_row.index[0],df_row.index[0]+1)
            inter = self._supplier_similarity(df_row.iloc[0], supplier_row.iloc[0])
            if inter[1] == 1 and inter[2]>=0.45 and inter[3] > 0:
                interact_value1.append(inter[0])
                interact_value2.append(inter[1])
                interact_value3.append(inter[2])
                interact_value4.append(inter[3])
                new_row = pd.concat([df_row, supplier_row], axis = 1)
                arr.append(list(new_row.values[0]))
        columns.extend(list(supplier_row.columns))
        val_df = pd.DataFrame(arr, columns = columns)
        val_df['price_sim'] = interact_value1
        val_df['code_sim'] = interact_value2
        val_df['title_sim'] = interact_value3
        val_df['region_sim'] = interact_value4
        
        return val_df
    
    def predict(self, data): 
        converted_data = self._get_convert_data(data)

        if converted_data.empty:
            return []
        converted_data['pred'] = self.model.predict(converted_data)
        predict_result_id = converted_data.sort_values('pred', ascending = False).head(5)['supplier']
        main_result = []
        for key, val in self.supplier_encoder.items():
            if val in predict_result_id:
                main_result.append(key)
        return main_result
