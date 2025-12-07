# フロントエンド開発ガイド (Phase 5)

ユーザーがAIと対戦するための「顔」となる画面を実装しました。
AIの高度な頭脳を感じさせる、プレミアムなデザインを目指しました。

---

## 1. 構成要素

### 1.1 HTML (`templates/game/index.html`)
セマンティックなマークアップを行いました。
*   `<header>`: スコアボード（勝敗数、勝率）を表示。
*   `<main>`: ゲームの主要エリア。プレイヤーとAIの手を表示するアリーナ。
*   `<div class="controls">`: R, P, S のアクションボタン。
*   `<footer>`: リセットボタンなどを配置。

### 1.2 CSS (`static/css/game.css`)
**Tech-Noir / Cyberpunk** を意識したモダンなデザインです。

*   **Glassmorphism**: 半透明のカード背景とぼかし効果 (`backdrop-filter`) でこれからのAIらしさを表現。
*   **Neon Glow**: 勝敗に応じて画面全体や要素が発光 (`box-shadow`) します。
    *   Win: Green Glow
    *   Lose: Red Glow
*   **Typography**: `Inter` と `JetBrains Mono` を組み合わせ、視認性とメカニカルな雰囲気を両立。

### 1.3 JavaScript (`static/js/game.js`)
APIとの通信とUIの動的な更新を担います。

*   **API通信**: `fetch` APIを使い、非同期に `/api/play/` を叩きます。
*   **State維持**: ブラウザの `localStorage` に `player_id` を保存し、リロードしても戦績が消えないようにしました。
    *   初回プレイ時: IDなしでリクエスト -> サーバーがID発行 -> `localStorage` に保存。
    *   次回以降: 保存されたIDを送信 -> サーバーが履歴を特定。
*   **アニメーション**: 結果が返ってきた瞬間に数値をカウントアップさせたり、手をポップさせたりして、「生きている」感を演出しました。

---

## 2. 連携フロー

1.  ユーザーが [ROCK] ボタンを押す。
2.  JSが `POST /api/play/` `{move: "R", player_id: "..."}` を送信。
3.  サーバー（AI）が手を決定し、結果をJSONで返す。
4.  JSが受け取り、画面の数字と手の表示を更新。
5.  結果に応じて画面が光る。

---

これで全ての開発フェーズが完了しました。
ブラウザで `http://127.0.0.1:8000/` にアクセスすれば、最強のAIと対戦できます。
