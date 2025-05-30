import pytest
import torch
from src.model import SponsorshipDetector, ModelTrainer

@pytest.fixture
def model():
    return SponsorshipDetector()

@pytest.fixture
def trainer():
    return ModelTrainer()

def test_model_architecture(model):
    # Test model structure
    assert hasattr(model, 'bert')
    assert hasattr(model, 'dropout')
    assert hasattr(model, 'classifier')
    assert hasattr(model, 'sigmoid')
    
    # Test forward pass with dummy input
    batch_size = 2
    seq_length = 10
    input_ids = torch.randint(0, 1000, (batch_size, seq_length))
    attention_mask = torch.ones((batch_size, seq_length))
    
    output = model(input_ids, attention_mask)
    assert output.shape == (batch_size, 1)
    assert torch.all(output >= 0) and torch.all(output <= 1)  # Check sigmoid output range

def test_model_trainer_initialization(trainer):
    assert trainer.model is not None
    assert trainer.criterion is not None
    assert trainer.optimizer is not None
    assert hasattr(trainer, 'device')

@pytest.mark.skip(reason="Requires actual training data")
def test_model_training(trainer):
    # This test should be implemented when we have actual training data
    pass
