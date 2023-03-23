const record = require("node-record-lpcm16");
const fs = require("fs");
const speech = require("@google-cloud/speech");
const openai = require("openai");

const GOOGLE_SPEECH_URL =
  "http://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium";

const client = new speech.SpeechClient();

const config = {
  encoding: "LINEAR16",
  sampleRateHertz: 16000,
  languageCode: "fr-FR",
  speechContexts: [
    {
      phrases: [],
      boost: 0,
    },
  ],
};

const request = {
  config: config,
  interimResults: false,
};

const gpt4Model = "gpt-3.5-turbo";
const api_key = process.env.OPENAI_API_KEY;
const API_URL = "https://api.openai.com/v1/chat/completions";

const createMessage = (role, content) => {
  return {
    role: role,
    content: content,
  };
};

const get_gpt4_response = async (prompt) => {
  openai.api_key = api_key;
  const response = await openai.Completion.create({
    engine: gpt4Model,
    prompt: `You are a helpful assistant.\n${prompt}`,
    maxTokens: 3000,
  });
  return response.choices[0].text;
};

const texttospeech_gcp = async (text) => {
  const { TextToSpeechClient } = require("@google-cloud/text-to-speech");
  const client = new TextToSpeechClient();
  const request = {
    input: { text: text },
    voice: { languageCode: "fr-FR", ssmlGender: "NEUTRAL" },
    audioConfig: { audioEncoding: "MP3", speakingRate: 1.5 },
  };
  const [response] = await client.synthesizeSpeech(request);
  const writeFile = util.promisify(fs.writeFile);
  await writeFile("output.mp3", response.audioContent, "binary");
  console.log('Audio content written to file "output.mp3"');
};

const play_audio_from_mp3 = () => {
  const player = require("play-sound")((opts = {}));
  player.play("output.mp3", function (err) {
    if (err) throw err;
  });
};

const main = async () => {
  const recognizeStream = client
    .streamingRecognize(request)
    .on("error", console.error)
    .on("data", async (data) => {
      const transcript = data.results[0].alternatives[0].transcript;
      console.log(`Transcript: ${transcript}`);
      const chat = await get_gpt4_response(transcript);
      console.log(chat);
      await texttospeech_gcp(chat);
      play_audio_from_mp3();
    });

  console.log("Listening...");
  record
    .start({
      sampleRateHertz: 16000,
      threshold: 0,
      verbose: false,
      recordProgram: "rec",
      silence: "10.0",
    })
    .on("error", console.error)
    .pipe(recognizeStream);

  console.log("Press Ctrl+C to stop recording...");
};

main();
