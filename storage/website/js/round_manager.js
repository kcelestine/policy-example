class RoundPageManager {
    constructor() {
        this.server = new Server();
        this.localState = new LocalStateManager();
        this.quizState = null;
    }

    initialize() {
        document.getElementById('user-name').value = this.localState.userName;
        this.quizState = this.localState.readQuizState();
        this.renderQuizState();
    }

    renderQuizState() {
        document.getElementById("quiz-round-status").innerText = JSON.stringify(this.quizState);
    }
}