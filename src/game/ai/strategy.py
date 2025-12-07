import random
from game.ai.predictors import (
    RandomPredictor,
    MarkovPredictor,
    FrequencyPredictor,
    PatternMatcherPredictor
)

class StrategySelector:
    def __init__(self):
        self.predictors = {
            "Random": RandomPredictor(),
            "Markov": MarkovPredictor(),
            "Frequency": FrequencyPredictor(),
            "Pattern": PatternMatcherPredictor(),
        }
        
        # 戦略キー: "PredictorName_Type" (Type: P0, P1)
        self.strategies = []
        for name in self.predictors:
            self.strategies.append(f"{name}_P0")
            self.strategies.append(f"{name}_P1")
            
        # スコアの初期化
        self.scores = {s: 0 for s in self.strategies}
        
        # 前回の各戦略の「出し手」を保存（スコア更新用）
        self.last_strategy_moves = {}

    def get_winning_move(self, move):
        mapping = {"R": "P", "P": "S", "S": "R"}
        return mapping.get(move, random.choice(["R", "P", "S"]))

    def select_move(self, history):
        """
        履歴に基づいて学習・予測を行い、最終的な手を決定する
        """
        # 各予測器からの予測を取得
        predictions = {}
        for name, predictor in self.predictors.items():
            predictions[name] = predictor.predict(history)
            
        # 各戦略ごとの「次の手」を算出
        strategy_moves = {}
        for name, pred in predictions.items():
            # P0: 予測されたユーザーの手(pred)に勝つ手
            p0_move = self.get_winning_move(pred)
            strategy_moves[f"{name}_P0"] = p0_move
            
            # P1: ユーザーがP0を読んで裏をかいてくる(predに勝つ手を出してくる)と仮定し、それに勝つ手
            # ユーザーの裏 = get_winning_move(p0_move) -> これに勝つ手を出す
            user_counter = self.get_winning_move(p0_move)
            p1_move = self.get_winning_move(user_counter)
            strategy_moves[f"{name}_P1"] = p1_move

        # 直近の戦略の手を保存（後でupdate_scoresで使う）
        self.last_strategy_moves = strategy_moves
        
        # 最高スコアの戦略を選択
        # スコアが同じ場合はランダム、あるいは固定順
        best_strategy = max(self.scores, key=self.scores.get)
        
        # 稀にランダムウォーク (Exploration) を入れるのもありだが、
        # ここでは純粋にスコアが高いものを選ぶ
        
        return strategy_moves[best_strategy], best_strategy

    def update_scores(self, user_move):
        """
        ユーザーが実際に出した手を受け取り、前回の戦略の勝敗を評価してスコアを更新
        """
        if not self.last_strategy_moves:
            return

        for strategy, move in self.last_strategy_moves.items():
            if move == user_move:
                # 引き分け
                self.scores[strategy] += 0
            elif self.get_winning_move(user_move) == move:
                 # ユーザーが勝った = AI(strategy)が負けた
                 self.scores[strategy] -= 1
            else:
                 # AIが勝った (moveがuser_moveに勝つ)
                 # move beats user_move check:
                 if self.get_winning_move(move) != user_move: # moveがuser_moveに負けてない、かつ引き分けでもない
                     # つまり勝ち
                     self.scores[strategy] += 1
                     
        # 減衰処理 (過去の栄光を引きずりすぎないように)
        # for s in self.scores:
        #     self.scores[s] *= 0.95
