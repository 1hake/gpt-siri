This project is based on openai chat-gpt, speech-to-text and  

# Set up
You need to set up the 3 following third party services:
- [openai chat-gpt](https://platform.openai.com/docs/introduction/overview) 
  - Create your account to get an api key
  - Copy the key into a safe place
- [speech-to-text](https://console.cloud.google.com/speech/recognizers) 
  - Create a GCP account and a billing account if you do not have one yet
  - Enable the service
  - Create a recognizer with parameters:
    - Region: europe-west
    - model: latest-long
    - language codes: fr-FR (bonus: en-US)
- [text-to-speech](https://console.cloud.google.com/speech/text-to-speech)
  - Create a GCP account and a billing account if you do not have one yet
  - Enable the service

# Create a service account in gcp
- Go to [GCP service accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
- Create a new service account with the role "Speech Administrator"
- Once the account is created, click on it, go to `Keys` and add a `JSON` key 
- Store the key somewhere safe


# Install the gcloud cli if asked during the processus
Follow this [tutorial](https://cloud.google.com/sdk/docs/install-sdk)


# Project setup
Copy the `.env.example` file to `.env` and fill the variables:
```bash
OPENAI_API_KEY=your-key
GOOGLE_APPLICATION_CREDENTIALS=key.json. # path to your service account json key
```

Then run:
```bash
brew install portaudio
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.py
```

# Run the project
```bash
source venv/bin/activate
export $(cat .env | grep "^[^#]" | xargs)  # set up env var from .env
python gpt-siri.py
```

Wait for the `recording` message to talk (sound on !) and... enjoy :)


# Install it as a raycast command script (optional)
- Install [raycast](https://raycast.com/)
- Create a new bash script command named voice-gpt with raycast in the root directory of the repo
- Copy the content of `voice-gpt.sh.example` into the `voice-gpt.sh` file created by raycast
- Create a shortcut in raycast to run the command easily :)
