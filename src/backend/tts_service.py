from kokoro import KPipeline
import soundfile as sf
import os
from pathlib import Path
import glob
import logging
import time
import numpy as np
import torch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice configuration mapping
VOICE_CONFIG = {
    # English voices
    'af_heart': {'lang_code': 'a', 'emoji': '👱‍♀️', 'name': 'Heart', 'language': 'English 🇺🇸'},
    'af_nicole': {'lang_code': 'a', 'emoji': '👩‍💼', 'name': 'Nicole', 'language': 'English 🇺🇸'},
    'af_bella': {'lang_code': 'a', 'emoji': '👩', 'name': 'Bella', 'language': 'English 🇺🇸'},
    
    # Hindi voices
    'hf_alpha': {'lang_code': 'h', 'emoji': '👩‍🦰', 'name': 'Sita', 'language': 'Hindi 🇮🇳'},
    'hf_beta': {'lang_code': 'h', 'emoji': '👩‍🔬', 'name': 'Gita', 'language': 'Hindi 🇮🇳'}
}

# Check GPU availability
def is_cuda_available():
    return torch.cuda.is_available()

class TTSService:
    def __init__(self, output_dir="static/audio"):
        # Default language code will be set when generating speech
        self.pipelines = {}
        # Create output directory relative to the backend folder
        self.output_dir = Path(__file__).parent / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized TTS service with output directory: {self.output_dir}")
        logger.info(f"CUDA available: {is_cuda_available()}")
    
    def get_pipeline(self, lang_code, device='cpu'):
        """Get or create a pipeline for the specified language code and device"""
        key = f"{lang_code}_{device}"
        if key not in self.pipelines:
            logger.info(f"Creating new pipeline for language code: {lang_code} on {device}")
            self.pipelines[key] = KPipeline(lang_code=lang_code, device=device)
        return self.pipelines[key]
    
    def generate_speech(self, text, voice='af_nicole', device='cpu'):
        """
        Generate speech from text and save it as WAV file.
        Returns the path to the generated audio file, the original text, and voice info.
        """
        logger.info(f"Generating speech for text: {text[:50]}... with voice: {voice} on device: {device}")
        
        # Validate device
        if device == 'cuda' and not is_cuda_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            device = 'cpu'
        
        # Get the appropriate language code and voice info
        voice_info = VOICE_CONFIG.get(voice, VOICE_CONFIG['af_nicole'])
        lang_code = voice_info['lang_code']
        emoji = voice_info['emoji']
        voice_name = voice_info['name']
        language = voice_info['language']
        
        # Get the appropriate pipeline
        pipeline = self.get_pipeline(lang_code, device)
        
        # Generate a timestamp for unique filename
        timestamp = int(time.time() * 1000)
        
        # Process the text as a whole without splitting
        generator = pipeline(text=text, voice=voice)
        
        all_audio_segments = []
        
        for i, (gs, ps, audio) in enumerate(generator):
            logger.info(f"Generated segment {i}: {gs[:30] if gs else ''}...")
            all_audio_segments.append(audio)
            
        # If we have multiple segments, concatenate them
        if len(all_audio_segments) > 1:
            combined_audio = np.concatenate(all_audio_segments)
        elif len(all_audio_segments) == 1:
            combined_audio = all_audio_segments[0]
        else:
            logger.error("No audio segments were generated")
            raise Exception("No audio was generated")
                
        # Save the combined audio to a file
        output_file = self.output_dir / f"output_{voice}_{device}_{timestamp}.wav"
        try:
            sf.write(str(output_file), combined_audio, 24000)
            logger.info(f"Successfully generated new audio file: {output_file}")
            return str(output_file), text, voice, emoji, voice_name, language, device
        except Exception as e:
            logger.error(f"Error writing audio file: {e}")
            raise 

#sample hindi text 
# कृपया मुझे अपना नाम बताएं, मेरा नाम [सृ-जन] है और आप [जी-वि-का] के
# लिए क्या करते हैं, मुझे उम्मीद है कि अगर मैं [पू-छूं] तो यह ठीक रहेगा
# क्योंकि आजकल की [दु-नि-या] में लोग [अ-ज-न-बि-यों] के सामने खुलते नहीं हैं।