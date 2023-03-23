This project is based on openai chat-gpt, speech-to-text and  

# Set up
You need to set up the 3 following third party services:
- [openai chat-gpt] (https://platform.openai.com/docs/introduction/overview) 
  - Create your account to get an api key
  - Copy the key into a safe place
- [speech-to-text](https://console.cloud.google.com/speech/recognizers) 
  - Create a GCP account and a billing account if you do not have one yet
  - Enable the service
  - Create a recognizer with parameters:
    - Region: europe-west
    - model: latest-long
    - language codes: fr-FR (bonus: en-US)
- [text-to-speech] (https://console.cloud.google.com/speech/text-to-speech)
  - Create a GCP account and a billing account if you do not have one yet
  - Enable the service

# Create a service account in gcp
- Go to [GCP service accounts] (https://console.cloud.google.com/iam-admin/serviceaccounts)
- Create a new service account with the role "Speech Administrator"
- Once the account is created, click on it, go to `Keys` and add a `JSON` key 
- Store the key somewhere safe


# Install the gcloud cli ?
Follow this [tutorial] (https://cloud.google.com/sdk/docs/install-sdk)


# Run the project
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.py
export OPENAI_API_KEY=your-key
export GOOGLE_APPLICATION_CREDENTIALS=key.json. # path to your service account json key
python gpt-siri.py
```

Wait for the `recording` message to talk and sound on ;) 
