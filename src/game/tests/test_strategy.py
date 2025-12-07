import pytest
from game.ai.strategy import StrategySelector
from game.ai.predictors import RandomPredictor

class TestStrategySelector:
    def test_initialization(self):
        """初期化時の状態チェック"""
        selector = StrategySelector()
        # デフォルトでいくつかの戦略が登録されているはず
        assert len(selector.predictors) > 0
        assert len(selector.strategies) > 0 # P0, P1 などの展開後

    def test_selection_and_update(self):
        """スコアに基づいて戦略を選択し、更新するか"""
        selector = StrategySelector()
        
        # 履歴: ユーザーはずっと "R" を出している
        history = [{"user_move": "R"}] * 10
        
        # 1. 予測実行
        ai_move, strategy_name = selector.select_move(history)
        assert ai_move in ["R", "P", "S"]
        assert isinstance(strategy_name, str)
        
        # 2. 結果報告 (Update)
        # ユーザーが今回も "R" を出したとする
        # AIがもし "P" を出していれば、その戦略のスコアが上がるはず
        selector.update_scores("R")
        
        # 例: RandomPredictorだけのシンプルな状態で確認したいが、
        # ここではブラックボックステストとして「エラーなく動くか」を重視
