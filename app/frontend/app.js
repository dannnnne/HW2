document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('messageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = analyzeBtn.querySelector('span');
    const btnLoader = document.getElementById('btnLoader');
    
    const resultCard = document.getElementById('resultCard');
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultMessage = document.getElementById('resultMessage');
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceFill = document.getElementById('confidenceFill');
    
    // 피드백 관련 UI 요소
    const feedbackSection = document.getElementById('feedbackSection');
    const feedbackComment = document.getElementById('feedbackComment');
    const btnCorrect = document.getElementById('btnCorrect');
    const btnIncorrect = document.getElementById('btnIncorrect');
    const feedbackThanks = document.getElementById('feedbackThanks');

    // 현재 분석 상태 저장용
    let currentText = "";
    let currentPrediction = false;

    const icons = {
        danger: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
        safe: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`
    };

    analyzeBtn.addEventListener('click', async () => {
        const text = messageInput.value.trim();
        
        if (!text) {
            messageInput.classList.add('shake');
            setTimeout(() => messageInput.classList.remove('shake'), 500);
            return;
        }

        // Loading state
        analyzeBtn.disabled = true;
        btnText.classList.add('none');
        btnLoader.classList.remove('none');
        
        // Reset card
        resultCard.classList.add('hidden');
        resultCard.classList.remove('danger', 'safe');
        confidenceFill.style.width = '0%';
        
        // 피드백 UI 리셋
        feedbackSection.classList.add('none');
        feedbackComment.value = "";
        feedbackComment.classList.remove('none');
        btnCorrect.classList.remove('none');
        btnIncorrect.classList.remove('none');
        btnCorrect.disabled = false;
        btnIncorrect.disabled = false;
        feedbackThanks.classList.add('none');
        
        currentText = text;

        try {
            // Artificial delay for effect
            await new Promise(r => setTimeout(r, 600));

            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                throw new Error('API Error');
            }

            const data = await response.json();
            showResult(data);

        } catch (error) {
            alert('분석 중 오류가 발생했습니다. 백엔드 서버가 실행 중인지 확인해주세요.');
        } finally {
            analyzeBtn.disabled = false;
            btnText.classList.remove('none');
            btnLoader.classList.add('none');
        }
    });

    function showResult(data) {
        currentPrediction = data.is_spam;
        const confPct = Math.round(data.confidence * 100);
        
        if (data.is_spam) {
            resultCard.classList.add('danger');
            resultIcon.innerHTML = icons.danger;
            resultTitle.textContent = "피싱/스팸 경고!";
            resultMessage.textContent = "이 메시지는 피싱 사기나 악성 스팸일 확률이 매우 높습니다. 링크를 절대 클릭하지 마시고 메시지를 삭제하세요.";
        } else {
            resultCard.classList.add('safe');
            resultIcon.innerHTML = icons.safe;
            resultTitle.textContent = "안전한 메시지";
            resultMessage.textContent = "현재 AI 분석 결과, 이 메시지에서는 알려진 피싱/스팸 패턴이 발견되지 않았습니다. (하지만 항상 주의하세요!)";
        }
        
        confidenceValue.textContent = `${confPct}%`;
        
        resultCard.classList.remove('hidden');
        
        setTimeout(() => {
            confidenceFill.style.width = `${confPct}%`;
            feedbackSection.classList.remove('none');
        }, 500);
    }

    // 피드백 데이터 제출 로직
    async function submitFeedback(isCorrect) {
        const commentValue = feedbackComment.value.trim();
        
        btnCorrect.disabled = true;
        btnIncorrect.disabled = true;
        btnCorrect.classList.add('none');
        btnIncorrect.classList.add('none');
        feedbackComment.classList.add('none');
        feedbackThanks.classList.remove('none');
        
        try {
            await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: currentText,
                    prediction: currentPrediction,
                    is_correct: isCorrect,
                    comment: commentValue
                })
            });
        } catch (e) {
            console.error("Feedback tracking failed:", e);
        }
    }

    btnCorrect.addEventListener('click', () => submitFeedback(true));
    btnIncorrect.addEventListener('click', () => submitFeedback(false));
});
