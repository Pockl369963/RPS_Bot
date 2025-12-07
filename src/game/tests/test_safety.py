import pytest
from game.ai.safety import SafetyMechanism

class TestSafetyMechanism:
    def test_anti_spam(self):
        """ユーザーが同じ手を連打している場合、検知して勝つ手を出すか"""
        safety = SafetyMechanism()
        
        # "R" を連打している履歴
        history = [{"user_move": "R"}] * 10
        
        # 検知されるはず (Rに対する勝ち手 = P)
        move, strategy = safety.check_override(history)
        assert move == "P"
        assert strategy == "Safety_AntiSpam"

    def test_stop_loss(self):
        """AIが負け越している場合、Randomに切り替わるか"""
        safety = SafetyMechanism()
        
        # 直近20戦でAIが全敗している履歴
        # {"result": "lose"} -> AIから見た負け（ユーザーの勝ち）と定義するか、
        # GameLogモデルでは "result" は「ユーザーから見た結果」("win", "lose") なので、
        # ユーザーが "win" なら AIは負け。
        history = [{"result": "win"}] * 20
        
        move, strategy = safety.check_override(history)
        
        # ランダム発動 (手はRPSのどれか)
        assert move in ["R", "P", "S"]
        assert strategy == "Safety_StopLoss"
        
    def test_no_trigger(self):
        """何も問題ない場合はNoneを返すか"""
        safety = SafetyMechanism()
        
        # 普通の履歴
        history = [
            {"user_move": "R", "result": "win"},
            {"user_move": "P", "result": "lose"},
        ] * 5
        
        move, strategy = safety.check_override(history)
        assert move is None
        assert strategy is None
