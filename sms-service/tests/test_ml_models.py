import pytest
from app.ml_models import IntelligentPostCareSystem
import os
import numpy as np

@pytest.fixture
def postcare_system():
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    return IntelligentPostCareSystem(model_dir)

def test_symptom_classifier(postcare_system):
    features = np.array([[1, 1, 1, 1]])
    prediction = postcare_system.symptom_classifier.predict_proba(features)
    assert prediction.shape == (1, 2)
