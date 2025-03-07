This project is a **GitHub App**, which is used to listen to the Webhook events of the GitHub repository and automatically perform corresponding operations based on different events, 
such as:
- **Pull Request event** → automatic comment
- **Issue event** → automatic comment
- **Push event** → create an issue to record submission information

- ## Features
- *Webhook event monitoring*
- *Development based on Flask + GitHub API*
- *API authentication using JWT and Installation Token*

- ## Installation

- ### **1. Clone the repository**
- git clone https://github.com/Lauyoyo/yoyo-test.git
- cd yoyo-test

- ### **2. Get a webhook proxy URL**
- In your browser, navigate to https://smee.io/
- Click Start a new channel
- Copy the full URL under "Webhook Proxy URL"

- ### **3. Create GitHub App**
- Under "Homepage URL", enter https://github.com/your_username.
- Under "Webhook URL", enter your webhook proxy URL from step 2.
- Under "Repository permissions", next to "Pull requests, Issues and Contents" select Read & write.
- Under "Subscribe to events", select Pull request, Push and Issues.

- ### **4. Configure .env file**
- APP_ID="YOUR_APP_ID"
- WEBHOOK_SECRET="YOUR_WEBHOOK_SECRET"
- PRIVATE_KEY_PATH="YOUR_PRIVATE_KEY_PATH"

- ### **5. Install App**

- ## **6. Running the Flask server**
- python app.py
- By default, it listens to http://127.0.0.1:3000/ and waits for Webhook events

- ## **7. Start Server**
- npx smee -u Webhook Proxy URL -t http://localhost:3000/api/webhook

- ## Test

