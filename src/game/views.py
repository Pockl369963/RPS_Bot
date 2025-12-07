from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from .models import Player, GameLog
from .ai.strategy import StrategySelector
from .ai.safety import SafetyMechanism

@csrf_exempt
def play_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        player_id = data.get("player_id")
        user_move = data.get("move")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if user_move not in ["R", "P", "S"]:
        return JsonResponse({"error": "Invalid move"}, status=400)

def index_view(request):
    return render(request, 'game/index.html')

    # 1. Playerの取得または作成
    player = None
    if player_id:
        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            pass # Invalid IDなら新規作成へ
            
    if not player:
        player = Player.objects.create()

    # 2. 履歴の取得 (AI入力用)
    # 古い順に取得
    logs = GameLog.objects.filter(player=player).order_by('timestamp')
    history = [{"user_move": log.user_move, "result": log.result} for log in logs]

    # 3. AIの初期化とウォームアップ (ステートレス対応)
    selector = StrategySelector()
    safety = SafetyMechanism()
    
    # 過去の履歴を使ってスコアを復元 (直近50件程度で十分)
    # 注意: 全履歴を入れると重くなる可能性がある
    warmup_history = history[-50:] if len(history) > 50 else history
    
    # ウォームアップ: 過去の時点でどう予測したかをシミュレートしてスコア更新
    # しかし、正確にやるには「その時点でのhistory」が必要。
    # ここでは簡易的に、現在のhistoryから直近N個を使って学習させる。
    # 正確な再現は計算コストが高いので、今回は「直近の傾向」だけ掴ませる。
    
    temp_hist = []
    # warmup_historyの最初から順番に見ていく
    for h in warmup_history:
        # この時点での手を選ぶ (スコア更新用データをセットするため)
        # 実際にはここでは予測結果を使わないが、select_moveを呼ばないとlast_strategy_movesがセットされない
        selector.select_move(temp_hist)
        
        # ユーザーの手でスコア更新
        selector.update_scores(h["user_move"])
        
        # 履歴に追加
        temp_hist.append(h)

    # 4. 今の手を決定
    ai_move, strategy_name = selector.select_move(history)

    # 安全策チェック
    override_move, override_strategy = safety.check_override(history)
    if override_move:
        ai_move = override_move
        strategy_name = override_strategy

    # 5. 勝敗判定
    result = "draw"
    if user_move == ai_move:
        result = "draw"
        player.draws += 1
    elif (user_move == "R" and ai_move == "S") or \
         (user_move == "P" and ai_move == "R") or \
         (user_move == "S" and ai_move == "P"):
        result = "win" # User win
        player.wins += 1
    else:
        result = "lose" # User lose
        player.losses += 1
    
    player.total_games += 1
    player.save()

    # 6. ログ保存
    GameLog.objects.create(
        player=player,
        round_number=player.total_games,
        user_move=user_move,
        ai_move=ai_move,
        result=result,
        strategy_used=strategy_name
    )

    # 7. レスポンス
    return JsonResponse({
        "result": result,
        "ai_move": ai_move,
        "player_id": str(player.id),
        "stats": {
            "total": player.total_games,
            "wins": player.wins,
            "losses": player.losses,
            "draws": player.draws,
            "win_rate": player.wins / player.total_games if player.total_games > 0 else 0
        },
        "strategy": strategy_name
    })

@csrf_exempt
def reset_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    try:
        data = json.loads(request.body)
        player_id = data.get("player_id")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not player_id:
        return JsonResponse({"error": "Player ID required"}, status=400)

    try:
        player = Player.objects.get(id=player_id)
        # ログ削除
        GameLog.objects.filter(player=player).delete()
        # カウンタ類リセット
        player.total_games = 0
        player.wins = 0
        player.losses = 0
        player.draws = 0
        player.current_phase = 1
        player.save()
        
        return JsonResponse({"status": "success", "message": "Memory erased."})
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"}, status=404)
