class LocalStateManager {
    constructor() {
        this._userName = null;
    }

    get userName() {
        if (this._userName === null)
            this._userName = window.localStorage.getItem('quizz_username', '');
        return this._userName;
    }

    set userName(value) {
        if (this._userName == value)
            return;
        this._userName = value;
        window.localStorage.setItem('quizz_username', value);
    }

    storeQuizState(quizState) {
        let state = quizState;
        if (state)
            state = JSON.stringify(state);
        window.localStorage.setItem('quizz_state', state);
    }

    readQuizState() {
        const dataStr = window.localStorage.getItem('quizz_state', '');
        return JSON.parse(dataStr);
    }
}