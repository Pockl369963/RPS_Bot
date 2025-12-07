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
        assert 'じゃんけんAI' in response.content.decode('utf-8')

    def test_play_api_win_rate_logic(self):
        """勝率計算でDrawが除外されているか確認"""
        player = Player.objects.create(wins=1, losses=1, draws=2, total_games=4)
        url = reverse('api_play')
        
        # 次の手で勝ったとする (Win=2, Loss=1, Draw=2) -> 勝率 = 2 / 3 = 66.6%
        # AIの手をコントロールするのは難しいので、レスポンスの計算ロジックのみ確認
        # しかしplay_viewは実行時に+1されるので、
        # 既存プレイヤーでplay_viewを呼ぶと、1戦追加される。
        
        # モックを使わず、予測可能な状況を作るのは難しいが、
        # 単にレスポンスの win_rate が wins / (wins + losses) になっているか検算すればよい。
        
        data = {"player_id": str(player.id), "move": "R"}
        response = self.client.post(url, data, content_type="application/json")
        res_json = response.json()
        stats = res_json["stats"]
        
        wins = stats["wins"]
        losses = stats["losses"]
        win_rate = stats["win_rate"]
        
        expected_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        assert win_rate == expected_rate
        
        # 引き分けが含まれていないことを確認 (total != wins + losses の場合)
        if stats["draws"] > 0:
            assert wins + losses < stats["total"]
            # 旧ロジック (wins / total) と一致しないことを確認 (勝率が0でなければ)
            if wins > 0:
                 assert win_rate != (wins / stats["total"])
