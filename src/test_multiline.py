from backend.tts_service import TTSService, VOICE_CONFIG, is_cuda_available

# Create the TTS service
tts_service = TTSService()

print("Available voices:")
for voice_id, config in VOICE_CONFIG.items():
    print(f"{config['name']} ({voice_id}): {config['language']} {config['emoji']}")

print(f"\nCUDA available: {is_cuda_available()}")

# Test multi-line input
multi_line_text = """This is the first line of text.
This is the second line of text.
And here is a third line to make sure it all works correctly."""

print(f"\nTesting multi-line input:\n{multi_line_text}")

# Test with English voice on CPU
print("\nTesting with English voice (Nicole) on CPU:")
output_file, text, voice, emoji, voice_name, language, device = tts_service.generate_speech(
    multi_line_text, voice='af_nicole', device='cpu'
)

print(f"Generated output file: {output_file}")
print(f"Input text: {text}")
print(f"Voice: {voice_name} ({voice})")
print(f"Emoji: {emoji}")
print(f"Language: {language}")
print(f"Device: {device}")

# Test with Hindi voice on CPU
print("\nTesting with Hindi voice (Sita) on CPU:")
output_file, text, voice, emoji, voice_name, language, device = tts_service.generate_speech(
    multi_line_text, voice='hf_alpha', device='cpu'
)

print(f"Generated output file: {output_file}")
print(f"Input text: {text}")
print(f"Voice: {voice_name} ({voice})")
print(f"Emoji: {emoji}")
print(f"Language: {language}")
print(f"Device: {device}")

# If CUDA is available, test with GPU as well
if is_cuda_available():
    print("\nTesting with English voice (Nicole) on GPU:")
    output_file, text, voice, emoji, voice_name, language, device = tts_service.generate_speech(
        multi_line_text, voice='af_nicole', device='cuda'
    )
    
    print(f"Generated output file: {output_file}")
    print(f"Input text: {text}")
    print(f"Voice: {voice_name} ({voice})")
    print(f"Emoji: {emoji}")
    print(f"Language: {language}")
    print(f"Device: {device}")
else:
    print("\nSkipping GPU tests as CUDA is not available.")

print("\nTest completed successfully!") 