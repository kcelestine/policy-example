class Server {
  constructor() {
    this.baseUrl = 'http://localhost:8055/api/';
  }

  getQuizTopics(onCompleted) {
    const url = this.baseUrl + 'quiz-topics'
    fetch(url)
      .then(response => response.json())
      .then(data => {
        onCompleted(data);
      })
      .catch(error => {
        console.error(error);
      });
  }
}