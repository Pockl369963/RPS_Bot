# Playerモデル実装ガイド (TDD)

このドキュメントでは、**Evolutionary RPS** プロジェクトにおける `Player` モデルの実装プロセスを、テスト駆動開発 (TDD) のアプローチに沿って解説します。

---

## 1. 目的

ユーザー（プレイヤー）の戦績を管理するためのデータベースモデル `Player` を作成します。
開発には **TDD (Test-Driven Development)** を採用し、「テストを先に書き、そのテストを通すためのコードを書く」という手順で進めます。

---

## 2. 実装プロセス

### Step 1: テストコードの作成 (Red)

まだモデルが存在しない状態で、理想的な挙動をテストコードとして定義します。この時点ではテストは失敗します（Red）。

**ファイル:** `src/game/tests/test_models.py`

```python
import pytest
from game.models import Player
import uuid

@pytest.mark.django_db
def test_create_player():
    """Playerモデルが正しく作成できるかテスト"""
    # データを保存
    player = Player.objects.create()
    
    # IDがUUID形式で自動生成されているか確認
    assert isinstance(player.id, uuid.UUID)
    
    # 初期値（戦績0）が正しく設定されているか確認
    assert player.total_games == 0
    assert player.wins == 0
    assert player.losses == 0
    assert player.draws == 0
    assert player.current_phase == 1
    
    # DBに1件保存されたことを確認
    assert Player.objects.count() == 1
```

### Step 2: テスト環境の設定

`pytest` が Django プロジェクトの設定を認識できるように、`pyproject.toml` に設定を追加しました。

**ファイル:** `pyproject.toml`

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "rps_project.settings"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
pythonpath = "src"
testpaths = ["src"]
```

### Step 3: モデルの実装 (Green)

テストのエラー（`ImportError` や `OperationalError`）を解消するために、モデルを定義します。

**ファイル:** `src/game/models.py`

```python
from django.db import models
import uuid

class Player(models.Model):
    # UUIDをプライマリキーとして使用（推測されにくいID）
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 戦績データ（デフォルトは0）
    total_games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    
    # ゲームの進行度（フェーズ1〜5）
    current_phase = models.IntegerField(default=1)

    def __str__(self):
        return f"Player {self.id}"
```

### Step 4: マイグレーションの作成と適用

Djangoモデルの変更をデータベースに反映させるために、マイグレーションを行います。

```bash
# マイグレーションファイルの作成
uv run python src/manage.py makemigrations game

# マイグレーションの適用（今回はテスト実行時にpytest-djangoが自動で適用してくれるため、手動実行は確認用）
# uv run python src/manage.py migrate
```

### Step 5: 検証 (Refactor/Verification)

テストを実行し、全てが正しく動作することを確認します。

```bash
uv run pytest src/game/tests/test_models.py
```

実行結果:
```text
src\game\tests\test_models.py . [100%]
1 passed
```

これで、安全かつ確実に `Player` モデルの実装が完了しました。
