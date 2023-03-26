class IndexPageManager {
  constructor() {
      this.server = new Server();
  }

  initialize() {
    this.setupTabs();
    // request topics to list on the "New quiz" page
    this.server.getQuizTopics((topics) => {
        this.renderTopics(topics);
    });
    console.log("Initialized");
  }

  renderTopics(topics) {
    const radioGroup = document.createElement('div');
    topics.forEach(topic => {
      const label = document.createElement('label');
      label.classList.add('topics-radio-group');
      const radio = document.createElement('input');

      radio.type = 'radio';
      radio.name = 'topic';
      radio.value = topic.id;

      label.textContent = topic.name;
      label.appendChild(radio);

      radioGroup.appendChild(label);
    });
    const parentDiv = document.getElementById('quiz-topics');
    parentDiv.appendChild(radioGroup);
  }

  setupTabs() {
    const tabs = document.querySelectorAll('.tabs button');
    const tabNames = ['tab-join', 'tab-start']
    tabs.forEach((btn, i) => {
        btn.addEventListener('click', (e) => {
            this.openTab(e.currentTarget, tabNames[i]);
        })
    });
    this.openTab(tabs[tabs.length - 1], tabNames[tabs.length - 1]);
  }

  openTab(srcElement, tabName) {
      // Declare all variables
      let i, tabPanel, tabButton;

      // Get all elements with class="tab-panel" and hide them
      tabPanel = document.getElementsByClassName("tab-panel");
      for (i = 0; i < tabPanel.length; i++) {
        tabPanel[i].classList.remove("active");
      }

      // Get all elements with class="tab-button" and remove the class "active"
      tabButton = document.getElementsByClassName("tab-button");
      for (i = 0; i < tabButton.length; i++) {
        tabButton[i].classList.remove("active");
      }

      // Show the current tab, and add an "active" class to the button that opened the tab
      document.getElementById(tabName).classList.add("active");
      srcElement.classList.add("active");
    }
}
