from django.apps import AppConfig
from .ml_model import MLModel
import os

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        base_dir = os.path.join(os.path.dirname(__file__), "model_files")

        model_path = os.path.join(base_dir, "rec_model")
        region_encoder_path = os.path.join(base_dir, "region_encoder.json")
        supplier_encoder_path = os.path.join(base_dir, "supplier_encoder.json")
        description_model_path = os.path.join(base_dir, "description_model.sav")

        self.ml_model = MLModel(model_path, region_encoder_path, supplier_encoder_path, description_model_path)
