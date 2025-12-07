# GameLogモデル実装ガイド (TDD)

このドキュメントでは、**Evolutionary RPS** プロジェクトにおける `GameLog` モデルの実装プロセスを解説します。
`Player` モデルに引き続き、対戦履歴を保存するためのモデルをTDDで実装します。

---

## 1. 目的

1手ごとの対戦記録（ユーザーの手、AIの手、勝敗、使用された戦略など）を保存する `GameLog` モデルを作成します。
このモデルは `Player` モデルと **多対1 (Many-to-One)** のリレーション（ForeignKey）を持ちます。

---

## 2. 実装プロセス

### Step 1: テストコードの作成 (Red)

`GameLog` モデルが `Player` と正しく紐付き、各フィールドが保存されることを確認するテストを書きます。

**ファイル:** `src/game/tests/test_models.py`

```python
@pytest.mark.django_db
def test_create_gamelog():
    """GameLogモデルが正しく作成され、Playerと紐づくかテスト"""
    from game.models import GameLog # まだ存在しないためImportErrorになる

    # 親となるPlayerを作成
    player = Player.objects.create()
    
    # GameLogを作成
    log = GameLog.objects.create(
        player=player,
        round_number=1,
        user_move="R",
        ai_move="S",
        result="win",
        strategy_used="Random",
    )
    
    # 検証
    assert log.player == player
    assert log.result == "win"
    
    # 逆参照の確認（PlayerからGameLogを参照できるか）
    assert player.gamelog_set.count() == 1
    assert player.gamelog_set.first() == log
```

### Step 2: モデルの実装 (Green)

テストのエラー (`ImportError`) を解消するため、`models.py` に `GameLog` クラスを追加します。

**ファイル:** `src/game/models.py`

```python
class GameLog(models.Model):
    # Playerとのリレーション (ON_DELETE=CASCADE: Playerが消えたらログも消える)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    
    # 対戦詳細
    round_number = models.IntegerField()
    user_move = models.CharField(max_length=1)  # "R", "P", "S"
    ai_move = models.CharField(max_length=1)    # "R", "P", "S"
    result = models.CharField(max_length=10)    # "win", "lose", "draw"
    
    # AIがどの戦略を使ったか（分析用）
    strategy_used = models.CharField(max_length=50)
    
    # 日時
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GameLog {self.id} for {self.player}"
```

### Step 3: マイグレーション

変更をDBに反映します。

```bash
uv run python src/manage.py makemigrations game
# -> 0002_gamelog.py が作成される
```

### Step 4: 検証 (Verification)

再度テストを実行し、PASSすることを確認します。

```bash
uv run pytest src/game/tests/test_models.py
```

実行結果:
```text
src\game\tests\test_models.py .. [100%]
2 passed
```
（`Player`のテストと合わせて2つのテストが通過）

---

## 3. ポイント

*   **ForeignKey**: `models.ForeignKey` を使い、他のモデルとの関係性を定義しました。
*   **TDDのサイクル**: 常に「テスト失敗 -> 実装 -> テスト成功」の順序を守ることで、要件漏れを防ぎ、バグの少ないコードを実装しました。
