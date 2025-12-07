import random
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from .models import RPSLSTM

class BasePredictor(ABC):
    """すべての予測器の基底クラス"""
    @abstractmethod
    def predict(self, history: list) -> str:
        """
        履歴を受け取り、次のユーザーの手 ('R', 'P', 'S') を予測する
        
        Args:
            history (list): 辞書のリスト。各辞書は {"user_move": "R", ...} などの形式。
                            古い順に並んでいることを想定。
        Returns:
            str: 予測されたユーザーの手 ("R", "P", "S")
        """
        pass

class RandomPredictor(BasePredictor):
    """ランダムに予測する (ベースライン)"""
    def predict(self, history: list) -> str:
        return random.choice(["R", "P", "S"])

class MarkovPredictor(BasePredictor):
    """1次マルコフ連鎖: 直前の手から次の手の遷移確率を利用"""
    def predict(self, history: list) -> str:
        if len(history) < 2:
            return random.choice(["R", "P", "S"])
        
        # 遷移データの構築
        transitions = defaultdict(lambda: defaultdict(int))
        
        for i in range(len(history) - 1):
            current_move = history[i].get("user_move")
            next_move = history[i+1].get("user_move")
            if current_move and next_move:
                transitions[current_move][next_move] += 1
        
        # 直前のユーザーの手
        last_user_move = history[-1].get("user_move")
        if not last_user_move or last_user_move not in transitions:
            return random.choice(["R", "P", "S"])
        
        candidates = transitions[last_user_move]
        if not candidates:
             return random.choice(["R", "P", "S"])
             
        predicted_move = max(candidates, key=candidates.get)
        return predicted_move

class FrequencyPredictor(BasePredictor):
    """頻度分析: 過去に最も多く出した手を予測"""
    def predict(self, history: list) -> str:
        if not history:
             return random.choice(["R", "P", "S"])
        
        moves = [h.get("user_move") for h in history if h.get("user_move")]
        if not moves:
             return random.choice(["R", "P", "S"])
             
        count = Counter(moves)
        return count.most_common(1)[0][0]

class PatternMatcherPredictor(BasePredictor):
    """パターンマッチング: 過去の履歴から最長一致するシーケンスを探し、その続きを予測"""
    def predict(self, history: list) -> str:
        moves = "".join([h.get("user_move", "") for h in history if h.get("user_move")])
        n = len(moves)
        if n < 4: 
             return random.choice(["R", "P", "S"])
        
        for k in range(min(10, n - 1), 1, -1):
            pattern = moves[-k:]
            search_text = moves[:-1] 
            idx = search_text.rfind(pattern)
            
            if idx != -1:
                if idx + k < len(search_text):
                    next_move = search_text[idx + k]
                    return next_move
                
        return random.choice(["R", "P", "S"])

class RNNPredictor(BasePredictor):
    """RNN (LSTM) を用いた予測"""
    def __init__(self, seq_length=10, hidden_size=32):
        self.seq_length = seq_length
        self.model = RPSLSTM(input_size=3, hidden_size=hidden_size, output_size=3)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)
        self.criterion = nn.CrossEntropyLoss()
        self.mapping = {'R': [1, 0, 0], 'P': [0, 1, 0], 'S': [0, 0, 1]}
        self.idx_to_move = {0: 'R', 1: 'P', 2: 'S'}
        self.move_to_idx = {'R': 0, 'P': 1, 'S': 2}
        
    def _moves_to_tensor(self, moves):
        # moves: list of 'R', 'P', 'S'
        features = [self.mapping[m] for m in moves]
        return torch.tensor([features], dtype=torch.float32) # (1, seq, 3)

    def predict(self, history: list) -> str:
        if len(history) < self.seq_length:
            return random.choice(['R', 'P', 'S'])
            
        # Get last seq_length user moves
        user_moves = [h['user_move'] for h in history[-self.seq_length:] if h.get('user_move')]
        if len(user_moves) < self.seq_length:
             return random.choice(['R', 'P', 'S'])

        # Predict next user move
        self.model.eval()
        with torch.no_grad():
            input_tensor = self._moves_to_tensor(user_moves)
            output = self.model(input_tensor) # (1, 3)
            predicted_idx = torch.argmax(output).item()
            predicted_move = self.idx_to_move[predicted_idx]
            
        # Train on the latest data if we have enough
        if len(history) > self.seq_length + 1:
            self._train_step(history)
            
        return predicted_move

    def _train_step(self, history):
        # Train on the last available sequence
        # We try to predict history[-1] given history[-(seq+1):-1]
        
        # Extract user mvoes
        moves = [h['user_move'] for h in history if h.get('user_move')]
        if len(moves) < self.seq_length + 1:
            return

        prev_seq = moves[-(self.seq_length+1):-1]
        target_move = moves[-1]
        
        if len(prev_seq) != self.seq_length:
            return

        self.model.train()
        input_tensor = self._moves_to_tensor(prev_seq)
        target_tensor = torch.tensor([self.move_to_idx[target_move]], dtype=torch.long)
        
        self.optimizer.zero_grad()
        output = self.model(input_tensor)
        loss = self.criterion(output, target_tensor)
        loss.backward()
        self.optimizer.step()
