import os
import json
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from transformers import AutoTokenizer, AutoModelForCausalLM

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# MODELS_DIR = os.path.join(BASE_DIR, "models")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # -> home/
MODELS_DIR = os.path.join(BASE_DIR, "models")            # -> home/models/
class JarvisEngine:
    def __init__(self):
        # Tier 1: intent classifier
        self.intent_model = load_model(os.path.join(MODELS_DIR, "jarvis_intent_model.keras"))

        with open(os.path.join(MODELS_DIR, "tokenizer.pkl"), "rb") as f:
            self.tokenizer = pickle.load(f)

        with open(os.path.join(MODELS_DIR, "label_encoder.pkl"), "rb") as f:
            self.label_encoder = pickle.load(f)

        with open(os.path.join(MODELS_DIR, "intents.json"), "r") as f:
            self.intents_data = json.load(f)

        # Tier 2: generative fallback
        tier2_path = os.path.join(MODELS_DIR, "final_model")
        self.gen_tokenizer = AutoTokenizer.from_pretrained(tier2_path)
        self.gen_model = AutoModelForCausalLM.from_pretrained(tier2_path)

        self.max_len = 20          # match your training pad length
        self.confidence_threshold = 0.60

    def predict_intent(self, text):
        seq = self.tokenizer.texts_to_sequences([text])
        padded = pad_sequences(seq, maxlen=self.max_len, padding="post")
        pred = self.intent_model.predict(padded, verbose=0)[0]
        confidence = float(np.max(pred))
        intent = self.label_encoder.inverse_transform([np.argmax(pred)])[0]
        return intent, confidence

    def get_tier1_response(self, intent, username='there'):
        for item in self.intents_data["intents"]:
            if item["intent"] == intent:
                response = np.random.choice(item["responses"])
                return response.replace("{username}", username)
        return None

    def get_tier2_response(self, text):
        inputs = self.gen_tokenizer.encode(text + self.gen_tokenizer.eos_token, return_tensors="pt")
        # outputs = self.gen_model.generate(
        #     inputs, max_length=100, pad_token_id=self.gen_tokenizer.eos_token_id
        outputs = self.gen_model.generate(
         inputs,
          max_length=100,
        pad_token_id=self.gen_tokenizer.eos_token_id,
        do_sample=True,
        top_k=50,
         top_p=0.92,
            temperature=0.7,
            repetition_penalty=1.3,
            no_repeat_ngram_size=3,
             )
        reply = self.gen_tokenizer.decode(outputs[:, inputs.shape[-1]:][0], skip_special_tokens=True)
        return reply

    def respond(self, text, username='there'):
        intent, confidence = self.predict_intent(text)
        if confidence >= self.confidence_threshold:
            return self.get_tier1_response(intent, username=username)
        return self.get_tier2_response(text)