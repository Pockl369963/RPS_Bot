import random
from collections import Counter

class SafetyMechanism:
    def get_winning_move(self, move):
        mapping = {"R": "P", "P": "S", "S": "R"}
        return mapping.get(move, "R") # fallback

    def check_override(self, history):
        """
        履歴をチェックし、緊急介入が必要なら手を返す。
        不要なら (None, None) を返す。
        """
        # データ不足なら発動しない
        if not history:
            return None, None
            
        # 1. Anti-Spam (直近10手)
        recent_10 = history[-10:]
        if len(recent_10) >= 10:
            moves = [h.get("user_move") for h in recent_10 if h.get("user_move")]
            if moves:
                count = Counter(moves)
                most_common_move, freq = count.most_common(1)[0]
                
                # 同一の手が8割以上
                if freq >= 8:
                    # スパム検知。その手に勝つ手を出す
                    return self.get_winning_move(most_common_move), "Safety_AntiSpam"

        # 2. Stop-Loss (直近20手)
        recent_20 = history[-20:]
        if len(recent_20) >= 20:
            # AIの勝利数をカウント
            # ユーザーのresultが "lose" なら AIの勝ち
            ai_wins = sum(1 for h in recent_20 if h.get("result") == "lose")
            
            # 勝率が25%未満 (20戦中5勝未満)
            if ai_wins < 5:
                # 乱数へ切り替え
                return random.choice(["R", "P", "S"]), "Safety_StopLoss"
                
        return None, None
