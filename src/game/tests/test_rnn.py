import pytest
import torch
import numpy as np
from game.ai.models import RPSLSTM
from game.ai.predictors import RNNPredictor

class TestRPSLSTM:
    def test_model_structure(self):
        model = RPSLSTM(input_size=3, hidden_size=10, output_size=3)
        assert isinstance(model, torch.nn.Module)
        
    def test_forward_pass(self):
        model = RPSLSTM(input_size=3, hidden_size=10, output_size=3)
        # Batch=1, Seq=5, Feat=3
        dummy_input = torch.randn(1, 5, 3)
        output = model(dummy_input)
        assert output.shape == (1, 3)
        # Probabilities should sum to 1
        assert torch.isclose(torch.sum(output), torch.tensor(1.0))

class TestRNNPredictor:
    def test_init(self):
        predictor = RNNPredictor()
        assert predictor.model is not None
        
    def test_predict_insufficient_data(self):
        predictor = RNNPredictor()
        history = [{'user_move': 'R', 'ai_move': 'P', 'result': 'lose'}]
        # Should return a random choice or similar if data is insufficient
        # BasePredictor usually returns a choice.
        # Check that it doesn't crash
        prediction = predictor.predict(history)
        assert prediction in ['R', 'P', 'S']

    def test_update_and_predict(self):
        predictor = RNNPredictor()
        # Create a dummy history of sufficient length
        # Assuming sequence length required is e.g. 5
        history = []
        for _ in range(20):
            history.append({'user_move': 'R', 'ai_move': 'S', 'result': 'win'})
        
        # Mock training to ensure it runs
        # We need to simulate the state where we have data
        # For simplicity, just call predict and ensure it uses the model
        
        prediction = predictor.predict(history)
        assert prediction in ['R', 'P', 'S']

    def test_tensor_conversion(self):
        predictor = RNNPredictor()
        moves = ['R', 'P', 'S']
        tensor = predictor._moves_to_tensor(moves)
        assert tensor.shape == (1, 3, 3) # Batch 1, Seq 3, Feat 3
