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
        document.getElementById('btn-start-quiz').addEventListener('click', (e) => {
            this.scheduleQuiz();
        });
    }

    scheduleQuiz() {
        this.server.scheduleQuiz(
            this.quizState.state.quiz_code,
            this.quizState.user.user_token,
            10,
            (data) => {this.onQuizScheduled(data);}
        )
    }

    onQuizScheduled(data) {
        // TODO: check the data is the correct state
        this.localState.storeQuizState(data);
        this.quizState = data;
        this.renderQuizState();
    }

    renderQuizState() {
        this.localState.userName = this.quizState.user.name;
        let quizStatusText = `Quiz "${this.quizState.state.name}" (#` +
            `${this.quizState.state.quiz_code}) `;
        document.getElementById("start-quiz-panel").style.display = 'none';
        if (this.quizState.state.status == 'PENDING') {
            quizStatusText += 'is not started yet';
            if (this.quizState.user.user_role == 'COMMANDER') {
                quizStatusText += '. Share the link to the quiz with your friends ' +
                    'and then start the quiz.';
                // show the button to start the quiz
                document.getElementById("start-quiz-panel").style.display = 'block';
            }
        }
        else if (this.quizState.state.status == 'SCHEDULED')
            quizStatusText += `will start at ${this.quizState.state.starts_at}`;
        else if (this.quizState.state.status == 'STARTED')
            quizStatusText += 'is started';
        else if (this.quizState.state.status == 'FINISHED')
            quizStatusText += 'is finished';
        else if (this.quizState.state.status == 'EXPIRED')
            quizStatusText += 'is expired';
        document.getElementById("quiz-status-text").innerText = quizStatusText;

        document.getElementById("quiz-round-status").innerText = JSON.stringify(this.quizState);

        this.renderPlayers();
    }

    renderPlayers() {
        const parentDiv = document.getElementById('quiz-players');
        while (parentDiv.firstChild) {
            parentDiv.removeChild(parentDiv.firstChild);
        }
        // sort the user names: the current user would come first
        const ownUser = this.quizState.user.name;
        let names = this.quizState.all_user_names.filter(item => {
            return item == ownUser ? null : item;
        });
        names = [ownUser, ...names];

        names.forEach((u) => {
            const playerDiv = document.createElement('div');
            let markup = encodeHTML(u);
            if (u == ownUser)
                markup = `<b>${markup}</b>`;
            playerDiv.innerHTML = markup;
            parentDiv.appendChild(playerDiv);
        });
    }
}