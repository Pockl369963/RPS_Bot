import pytest
from django.urls import reverse
from game.models import Player, GameLog
import json
from django.test import Client

@pytest.mark.django_db
class TestGameAPI:
    def setup_method(self):
        self.client = Client()

    def test_play_api_new_player(self):
        """新規プレイヤーが手を送信した場合、プレイヤー作成して対戦を行う"""
        url = reverse('api_play') # まだ未定義なのでここで落ちるかも、あるいは404
        data = {
            "player_id": None, # 新規
            "move": "R"
        }
        
        # 404にならず、正しく処理されるか (Red phase では 404 or Result Fail)
        response = self.client.post(url, data, content_type="application/json")
        
        # 期待値: 200 OK
        assert response.status_code == 200
        
        # レスポンスの中身確認
        res_json = response.json()
        assert "result" in res_json
        assert "ai_move" in res_json
        assert "stats" in res_json
        assert "player_id" in res_json # 新規発行されたID
        
        # DB確認
        assert Player.objects.count() == 1
        assert GameLog.objects.count() == 1

    def test_play_api_existing_player(self):
        """既存プレイヤーの場合、履歴を考慮して対戦を行う"""
        player = Player.objects.create(wins=10)
        url = reverse('api_play')
        data = {
            "player_id": str(player.id),
            "move": "P"
        }
        
        response = self.client.post(url, data, content_type="application/json")
        assert response.status_code == 200
        
        res_json = response.json()
        assert res_json["player_id"] == str(player.id)
        
        # Statsが更新されているか（少なくともgamesは増えている）
        assert res_json["stats"]["total"] == 1 # 初期値0 + 1 (winsは初期値10だがtotalはGameLog数依存なら0スタートかも。モデルの初期値依存)
        # 補足: Player作成時に total_games=0 なので 1 になるはず
        
        player.refresh_from_db()
        assert player.total_games == 1

    def test_reset_api(self):
        """リセットAPIが呼ばれると履歴がクリアされるか"""
        player = Player.objects.create(total_games=10, wins=5)
        # ログも作っておく
        GameLog.objects.create(player=player, round_number=1, user_move="R", ai_move="S", result="win", strategy_used="Random")
        
        url = reverse('api_reset')
        data = {"player_id": str(player.id)}
        
        response = self.client.post(url, data, content_type="application/json")
        assert response.status_code == 200
        
        # DB確認
        player.refresh_from_db()
        assert player.total_games == 0
        assert player.wins == 0
        
        # ログが消えているか
        assert GameLog.objects.filter(player=player).count() == 0

    def test_index_view(self):
        """トップページが正しく表示されるか"""
        url = reverse('index')
        response = self.client.get(url)
        assert response.status_code == 200
        assert 'EVOLUTIONARY' in response.content.decode('utf-8')
