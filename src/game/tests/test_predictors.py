import pytest
from game.ai.predictors import (
    RandomPredictor,
    MarkovPredictor,
    FrequencyPredictor,
    PatternMatcherPredictor
)

class TestPredictors:
    def test_pattern_matcher_predictor(self):
        """PatternMatcherが過去のシーケンスを認識するか"""
        predictor = PatternMatcherPredictor()
        
        # パターン: R -> P -> S を繰り返す
        history = [
            # 1回目
            {"user_move": "R"}, {"user_move": "P"}, {"user_move": "S"},
            # 2回目
            {"user_move": "R"}, {"user_move": "P"}, {"user_move": "S"},
            # 3回目: R -> P まで来た
            {"user_move": "R"}, {"user_move": "P"},
        ]
        
        # 直近が R -> P なので、過去の例に従えば次は S
        prediction = predictor.predict(history)
        assert prediction == "S"
    def test_random_predictor(self):
        """RandomPredictorがR, P, Sのいずれかを返すか"""
        predictor = RandomPredictor()
        history = []
        prediction = predictor.predict(history)
        assert prediction in ["R", "P", "S"]

    def test_markov_predictor_basic(self):
        """MarkovPredictorがパターンを学習するか (1st Order)"""
        predictor = MarkovPredictor()
        
        # ユーザーは「グー」の次に必ず「パー」を出す癖があるとする
        # R -> P という遷移を学習させる
        history = [
            {"user_move": "R", "result": "lose"},
            {"user_move": "P", "result": "win"},
            {"user_move": "R", "result": "lose"},
            {"user_move": "P", "result": "win"},
            {"user_move": "R", "result": "lose"}, # 直前がR
        ]
        
        # 次は確率的に P が予測されるはず (R -> P)
        prediction = predictor.predict(history)
        assert prediction == "P"

    def test_frequency_predictor(self):
        """FrequencyPredictorが最も多い手を予測するか"""
        predictor = FrequencyPredictor()
        
        # ユーザーは「チョキ」を多用する
        history = [
            {"user_move": "S"},
            {"user_move": "S"},
            {"user_move": "R"},
            {"user_move": "S"},
            {"user_move": "P"},
        ]
        
        # S が多いので S を予測するはず
        prediction = predictor.predict(history)
        assert prediction == "S"

    def test_empty_history(self):
        """履歴がない場合の挙動"""
        # どの予測器もエラー落ちせず、ランダム等を返すべき
        predictors = [RandomPredictor(), MarkovPredictor(), FrequencyPredictor()]
        for p in predictors:
            assert p.predict([]) in ["R", "P", "S"]
