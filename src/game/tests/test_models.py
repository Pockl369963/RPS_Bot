import pytest
from game.models import Player
import uuid

@pytest.mark.django_db
def test_create_player():
    """Playerモデルが正しく作成できるかテスト"""
    player = Player.objects.create()
    
    # UUIDが自動生成されているか
    assert isinstance(player.id, uuid.UUID)
    
    # 初期値の確認
    assert player.total_games == 0
    assert player.wins == 0
    assert player.losses == 0
    assert player.draws == 0
    assert player.current_phase == 1
    
    # インスタンスが保存されているか
    assert Player.objects.count() == 1

@pytest.mark.django_db
def test_create_gamelog():
    """GameLogモデルが正しく作成され、Playerと紐づくかテスト"""
    from game.models import GameLog # まだ作っていないのでここでインポート（エラーになるはず）

    player = Player.objects.create()
    
    log = GameLog.objects.create(
        player=player,
        round_number=1,
        user_move="R",
        ai_move="S",
        result="win",
        strategy_used="Random",
    )
    
    # データが正しく保存されているか
    assert log.player == player
    assert log.round_number == 1
    assert log.user_move == "R"
    assert log.ai_move == "S"
    assert log.result == "win"
    assert log.strategy_used == "Random"
    assert log.timestamp is not None
    
    # 逆参照 (player.gamelog_set) が機能するか
    assert player.gamelog_set.count() == 1
    assert player.gamelog_set.first() == log
