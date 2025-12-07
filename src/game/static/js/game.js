document.addEventListener('DOMContentLoaded', () => {
    // --- State Management ---
    const getPlayerId = () => localStorage.getItem('rps_player_id');
    const setPlayerId = (id) => localStorage.setItem('rps_player_id', id);

    // --- DOM Elements ---
    const els = {
        wins: document.getElementById('wins'),
        losses: document.getElementById('losses'),
        draws: document.getElementById('draws'),
        winRate: document.getElementById('win-rate'),
        aiWinRate: document.getElementById('ai-win-rate'),
        totalGames: document.getElementById('total-games'),
        userHand: document.getElementById('user-hand'),
        aiHand: document.getElementById('ai-hand'),
        result: document.getElementById('result-message'),
        btns: document.querySelectorAll('.choice-btn'),
        resetBtn: document.getElementById('reset-btn'),
    };

    const EMOJIS = { "R": "✊", "P": "✋", "S": "✌️" };
    const TEXTS = { "win": "YOU WIN", "lose": "YOU LOSE", "draw": "DRAW" };
    const COLORS = { "win": "#22c55e", "lose": "#ef4444", "draw": "#eab308" };

    // --- Core Logic ---
    async function playRound(move) {
        // UI Interaction
        setLoadingState(true);

        try {
            const playerId = getPlayerId();
            const payload = { move: move };
            if (playerId) payload.player_id = playerId;

            const res = await fetch('/api/play/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("API Error");

            const data = await res.json();

            // Save ID if new
            if (data.player_id && !playerId) {
                setPlayerId(data.player_id);
            }

            updateUI(move, data);

        } catch (e) {
            console.error(e);
            els.result.textContent = "ERROR";
        } finally {
            setLoadingState(false);
        }
    }

    async function resetMemory() {
        if (!confirm("Are you sure you want to erase AI memory? This cannot be undone.")) return;

        const playerId = getPlayerId();
        if (!playerId) return;

        try {
            await fetch('/api/reset/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ player_id: playerId })
            });

            localStorage.removeItem('rps_player_id');
            location.reload(); // Simple reload to clear state
        } catch (e) {
            console.error(e);
        }
    }

    // --- UI Helpers ---
    function setLoadingState(isLoading) {
        els.btns.forEach(btn => btn.disabled = isLoading);
        if (isLoading) {
            els.result.textContent = "...";
        }
    }

    function updateUI(userMove, data) {
        // Hands
        els.userHand.innerHTML = `<span class="animate-pop">${EMOJIS[userMove]}</span>`;
        els.aiHand.innerHTML = `<span class="animate-pop">${EMOJIS[data.ai_move]}</span>`;

        // Result Text
        els.result.textContent = TEXTS[data.result];
        els.result.style.color = COLORS[data.result];


        // Stats
        const s = data.stats;
        animateValue(els.wins, parseInt(els.wins.textContent), s.wins);
        animateValue(els.losses, parseInt(els.losses.textContent), s.losses);
        animateValue(els.draws, parseInt(els.draws.textContent), s.draws);
        animateValue(els.totalGames, parseInt(els.totalGames.textContent), s.total);
        els.winRate.textContent = `${(s.win_rate * 100).toFixed(1)}%`;
        els.aiWinRate.textContent = `${(s.ai_win_rate * 100).toFixed(1)}%`;

        // Dynamic Theme (Border Glow)
        document.querySelector('.container').style.boxShadow = `0 0 50px ${COLORS[data.result]}20`; // 20 = low opacity
    }

    function animateValue(obj, start, end) {
        if (start === end) return;
        obj.textContent = end;
        obj.animate([
            { transform: 'scale(1.5)', color: '#fff' },
            { transform: 'scale(1)', color: 'var(--text-primary)' }
        ], { duration: 300 });
    }

    // --- Init ---
    els.btns.forEach(btn => {
        btn.addEventListener('click', () => playRound(btn.dataset.move));
    });

    els.resetBtn.addEventListener('click', resetMemory);
});
