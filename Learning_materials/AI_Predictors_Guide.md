# AI予測器実装ガイド：基本編 (3.1 & 3.2)

このドキュメントでは、じゃんけんBotの「頭脳」となるAI予測器の実装プロセスを解説します。
まずは基本的な3つの予測器（ランダム、マルコフ連鎖、頻度分析）を作成しました。

---

## 1. クラス設計

すべての予測器は、共通の基底クラス `BasePredictor` を継承します。これにより、後で実装する「戦略セレクター」が統一的に扱えるようになります。

### インターフェース
```python
class BasePredictor(ABC):
    @abstractmethod
    def predict(self, history: list) -> str:
        pass
```

---

## 2. 各予測器のロジック

### 2.1 RandomPredictor (ランダム)
最も単純な予測器です。完全にランダムに手を返します。
これは「負けないための最低ライン」として、あるいはデータ不足時のフォールバックとして重要です。

```python
return random.choice(["R", "P", "S"])
```

### 2.2 MarkovPredictor (1次マルコフ連鎖)
「人は繰り返す」という性質を利用します。直前に出した手 (`last_move`) の次に、何が出やすいかを過去の履歴から学習します。

*   **例**: 過去に「グー(R) -> パー(P)」という流れが多ければ、今回ユーザーが「グー」を出した後には「パー」が来ると予測します。
*   **実装**: 辞書の辞書 `transitions[current][next]` で遷移回数をカウントし、最も回数の多い遷移先を予測値としました。

### 2.3 FrequencyPredictor (頻度分析)
「癖」を利用します。ユーザーが通算で最も多く出している手を予測します。

*   **実装**: `collections.Counter` を使い、履歴の中で最頻出の手を探しました。

---

## 3. テスト駆動開発 (TDD) の流れ

1.  **Red**: `test_predictors.py` に、期待する挙動（「グーの次はパーを予測すべき」など）を記述し、実行して失敗させました。
2.  **Green**: `predictors.py` にロジックを実装し、テストを通過させました。

### テストケース例 (Markov)
```python
history = [
    {"user_move": "R"}, {"user_move": "P"}, # R -> P
    {"user_move": "R"}, {"user_move": "P"}, # R -> P
    {"user_move": "R"}                      # 直前は R
]
# R の次は P が多いので、P を予測するはず
assert predictor.predict(history) == "P"
```

---

次は、より高度な「パターンマッチング予測器」の実装に進みます。
