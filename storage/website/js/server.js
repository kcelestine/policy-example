class Server {
    constructor() {
        this.baseUrl = 'http://localhost:8055/api/';
    }

    async checkStatus(response) {
        if (response.status >= 200 && response.status < 300)
            return await response.json()
        throw await response.json()
    }

    processErrorInResponse(error) {
        if (error.detail)
            alert(error.detail);
        else {
            alert('Generic error occurred, please check the log');
            console.log(error);
        }
    }

    getQuizTopics(onCompleted) {
        const url = this.baseUrl + 'quiz-topics'
        fetch(url)
            .then(this.checkStatus)
            .then(data => {
                onCompleted(data);
            })
            .catch(error => {
                this.processErrorInResponse(error);
            });
    }

    startQuiz(quizId, userName, onCompleted) {
        const url = this.baseUrl + 'quiz-start'
        fetch(url, {
                method: 'POST',
                body: JSON.stringify({"topic_id": quizId, "user_name": userName}),
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            })
            .then(this.checkStatus)
            .then(data => {
                onCompleted(data);
            })
            .catch(error => {
                this.processErrorInResponse(error);
            });
    }

    joinQuiz(quizCode, userName, onCompleted) {
        const url = this.baseUrl + 'quiz-join';
        fetch(url, {
                method: 'POST',
                body: JSON.stringify({"quiz_code": parseInt(quizCode), "user_name": userName}),
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            })
            .then(this.checkStatus)
            .then(data => {
                onCompleted(data);
            })
            .catch(error => {
                this.processErrorInResponse(error);
            });
    }
}
