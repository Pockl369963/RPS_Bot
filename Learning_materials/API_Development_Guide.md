# API開発ガイド (Phase 4)

このフェーズでは、作成したAIエンジンを外部（フロントエンド）から利用できるようにするためのWeb APIを実装しました。

---

## 1. 実装したエンドポイント

### 4.1 `/api/play/` (POST)
ユーザーの手を受け取り、AIの手を決定して勝敗を返すメインAPIです。

*   **Request**:
    ```json
    {
        "player_id": "uuid-string... (optional)",
        "move": "R"
    }
    ```
*   **Response**:
    ```json
    {
        "result": "win",       // ユーザーから見た勝敗
        "ai_move": "S",        // AIの手
        "player_id": "uuid...",// プレイヤーID (新規作成時はここで発行)
        "stats": { ... },      // 現在の戦績
        "strategy": "Markov_P0" // どの戦略が手を選んだか
    }
    ```

#### 実装のポイント: ステートレスなAI学習
Web APIは基本的に「ステートレス（状態を持たない）」であるべきです。しかし、AIは学習のために「過去の記憶」を必要とします。
今回は以下のアプローチでこれを解決しました。

1.  **DB保存**: 全対戦ログは `GameLog` モデルに永続化する。
2.  **ウォームアップ**: APIリクエストが来るたびに、直近の履歴（例えば50件）をDBから読み出す。
3.  **再学習**: `StrategySelector` を初期化し、読み出した履歴を使って高速に「記憶の復元（学習シミュレーション）」を行う。

これにより、サーバー再起動などを挟んでもAIの学習状態が維持されているように振る舞います。

```python
# views.py (簡易コード)
logs = GameLog.objects.filter(player=player)
history = [...]

# AIを初期化して、過去の自分をシミュレート
selector = StrategySelector()
for h in history[-50:]:
    selector.select_move(...) # 予測させる
    selector.update_scores(h["user_move"]) # 結果を教える (学習)

# 準備万端の状態で本番予測
ai_move, strategy = selector.select_move(history)
```

### 4.2 `/api/reset/` (POST)
プレイヤーの記憶を消去します。

*   **Request**: `{"player_id": "..."}`
*   **Logic**: DBから該当プレイヤーの `GameLog` を全削除し、勝敗数を0リセットします。

---

## 2. テスト (TDD)

`src/game/tests/test_views.py` にて、以下のシナリオを検証しました。

1.  **新規プレイヤー**: `player_id` なしで送ると、IDが発行されて対戦できるか。
2.  **既存プレイヤー**: IDを指定すると、戦績が加算されるか。
3.  **リセット**: リセット後に戦績が0に戻るか。

---

これでバックエンドの主要機能は全て完成しました。
次は Phase 5 (Frontend) で、実際に遊べるUIを作成します。
