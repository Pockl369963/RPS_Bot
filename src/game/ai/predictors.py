import random
from abc import ABC, abstractmethod
from collections import Counter, defaultdict

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
        
        # 履歴を舐めて遷移をカウント (A -> B)
        # history[-1] は現在の状況なので、その前までを使ってモデルを作る
        # あるいは全履歴を使う。ここでは全履歴を使う。
        # 直前の手 (last_move) に対して、次に来やすい手を予測したい。
        
        for i in range(len(history) - 1):
            current_move = history[i].get("user_move")
            next_move = history[i+1].get("user_move")
            if current_move and next_move:
                transitions[current_move][next_move] += 1
        
        # 直前のユーザーの手
        last_user_move = history[-1].get("user_move")
        if not last_user_move or last_user_move not in transitions:
            return random.choice(["R", "P", "S"])
        
        # 次の手の候補と頻度
        candidates = transitions[last_user_move]
        if not candidates:
             return random.choice(["R", "P", "S"])
             
        # 最も頻度の高い手を選択 (Greedy)
        # 確率的に選ぶなら random.choices を使うが、
        # ここでは「最も可能性が高い手」を予測値とする
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
        if n < 4: # 最低でもパターン(2or3) + 続き(1) が必要
             return random.choice(["R", "P", "S"])
        
        # 長いパターンから順に検索 (例: 5手前のパターン 〜 2手前のパターン)
        # min_pattern_len = 2
        # max_pattern_len = 10 (適当な上限)
        
        for k in range(min(10, n - 1), 1, -1):
            pattern = moves[-k:] # 直近 k 手
            
            # パターンが過去（今回除く）に出現したか検索
            # moves[:-1] は「今の直前」まで（つまり今回を含まない）だが、
            # パターンマッチングは「今の直前k手」が「それ以前」にあったかを探す。
            # 検索対象は moves[:-(k)] ではなく、moves[:-1] の中で pattern を探す。
            # ただし、patternの次の手を知りたいので、
            # moves[: -1] の中で pattern が出現し、かつその直後に文字がある場所を探す。
            
            # 簡単のため string.rfind を使う
            # 検索範囲は「最後の pattern」を含まない範囲
            search_text = moves[:-1] 
            idx = search_text.rfind(pattern)
            
            if idx != -1:
                # 見つかったパターンの直後の手を取得
                # search_text[idx] から始まる長さ k の文字列が pattern。
                # その次は search_text[idx + k]
                # search_text の長さが足りているかチェック
                if idx + k < len(search_text):
                    next_move = search_text[idx + k]
                    return next_move
                
                # もし検索範囲の末尾で見つかってしまった場合（続きがない）、
                # さらに前を探す必要があるが、rfindなのでそれは「なし」と等しい
                # (search_text自体が「続きを知っている過去のデータ」であるべき)
                
        return random.choice(["R", "P", "S"])
