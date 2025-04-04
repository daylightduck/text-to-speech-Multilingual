document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const convertBtn = document.getElementById('convertBtn');
    const audioPlayer = document.getElementById('audioPlayer');
    const outputSection = document.querySelector('.output-section');
    const historyContainer = document.getElementById('historyContainer');
    const voiceOptions = document.getElementById('voiceOptions');
    const deviceOptions = document.getElementById('deviceOptions');
    let currentAudio = null;
    
    // Keep track of conversion history
    const conversions = [];
    let selectedVoice = 'af_nicole'; // Default voice
    let selectedDevice = 'cpu'; // Default device
    
    // Fetch available voices
    async function fetchVoices() {
        try {
            const response = await fetch('/api/voices');
            const voiceGroups = await response.json();
            
            // Clear voice options
            voiceOptions.innerHTML = '';
            
            // Create voice options grouped by language
            voiceGroups.forEach(group => {
                const languageGroup = document.createElement('div');
                languageGroup.className = 'language-group';
                
                const languageLabel = document.createElement('div');
                languageLabel.className = 'language-label';
                languageLabel.textContent = group.language;
                
                languageGroup.appendChild(languageLabel);
                
                const voices = document.createElement('div');
                voices.className = 'voices';
                
                group.voices.forEach(voice => {
                    const voiceOption = document.createElement('div');
                    voiceOption.className = 'voice-option';
                    voiceOption.dataset.voiceId = voice.id;
                    if (voice.id === selectedVoice) {
                        voiceOption.classList.add('selected');
                    }
                    
                    const voiceEmoji = document.createElement('span');
                    voiceEmoji.className = 'voice-emoji';
                    voiceEmoji.textContent = voice.emoji;
                    
                    const voiceName = document.createElement('span');
                    voiceName.className = 'voice-name';
                    voiceName.textContent = voice.name;
                    
                    voiceOption.appendChild(voiceEmoji);
                    voiceOption.appendChild(voiceName);
                    
                    // Add click event listener
                    voiceOption.addEventListener('click', () => {
                        // Remove 'selected' class from all options
                        document.querySelectorAll('.voice-option').forEach(opt => {
                            opt.classList.remove('selected');
                        });
                        
                        // Add 'selected' class to clicked option
                        voiceOption.classList.add('selected');
                        
                        // Update selected voice
                        selectedVoice = voice.id;
                    });
                    
                    voices.appendChild(voiceOption);
                });
                
                languageGroup.appendChild(voices);
                voiceOptions.appendChild(languageGroup);
            });
        } catch (error) {
            console.error('Error fetching voices:', error);
        }
    }
    
    // Fetch available devices (CPU/GPU)
    async function fetchDevices() {
        try {
            const response = await fetch('/api/devices');
            const devices = await response.json();
            
            // Clear device options
            deviceOptions.innerHTML = '';
            
            // Create device options
            devices.forEach(device => {
                const deviceOption = document.createElement('div');
                deviceOption.className = 'device-option';
                deviceOption.dataset.deviceId = device.id;
                if (device.id === selectedDevice) {
                    deviceOption.classList.add('selected');
                }
                
                const deviceEmoji = document.createElement('span');
                deviceEmoji.className = 'device-emoji';
                deviceEmoji.textContent = device.emoji;
                
                const deviceInfo = document.createElement('div');
                deviceInfo.className = 'device-info';
                
                const deviceName = document.createElement('span');
                deviceName.className = 'device-name';
                deviceName.textContent = device.name;
                
                const deviceDescription = document.createElement('span');
                deviceDescription.className = 'device-description';
                deviceDescription.textContent = device.description;
                
                deviceInfo.appendChild(deviceName);
                deviceInfo.appendChild(deviceDescription);
                
                deviceOption.appendChild(deviceEmoji);
                deviceOption.appendChild(deviceInfo);
                
                // Add click event listener
                deviceOption.addEventListener('click', () => {
                    // Remove 'selected' class from all options
                    document.querySelectorAll('.device-option').forEach(opt => {
                        opt.classList.remove('selected');
                    });
                    
                    // Add 'selected' class to clicked option
                    deviceOption.classList.add('selected');
                    
                    // Update selected device
                    selectedDevice = device.id;
                });
                
                deviceOptions.appendChild(deviceOption);
            });
        } catch (error) {
            console.error('Error fetching devices:', error);
        }
    }
    
    // Fetch voices and devices on page load
    fetchVoices();
    fetchDevices();

    // Function to stop and reset audio
    function stopAndResetAudio() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
        }
        audioPlayer.pause();
        audioPlayer.currentTime = 0;
        audioPlayer.style.display = 'none';
        audioPlayer.src = '';
    }

    convertBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        
        if (!text) {
            alert('Please enter some text');
            return;
        }

        try {
            convertBtn.disabled = true;
            convertBtn.textContent = 'Converting...';

            // Stop and reset any currently playing audio
            stopAndResetAudio();

            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text,
                    voice: selectedVoice,
                    device: selectedDevice
                }),
            });

            const data = await response.json();

            if (data.success) {
                // Add cache-busting parameter to the URL
                const audioUrl = `${data.audio_file}?t=${new Date().getTime()}`;
                const timestamp = new Date().toLocaleString();
                
                // Create a new conversion object
                const conversion = {
                    text: data.text,
                    audioUrl: audioUrl,
                    timestamp: timestamp,
                    voice: data.voice,
                    voiceName: data.voice_name,
                    emoji: data.emoji,
                    language: data.language,
                    device: data.device
                };
                
                // Add to the beginning of the conversions array
                conversions.unshift(conversion);
                
                // Update the UI with the new conversion
                updateConversionHistory();
                
                // Show and play the audio
                audioPlayer.src = audioUrl;
                audioPlayer.style.display = 'block';
            } else {
                throw new Error(data.error || 'Failed to convert text to speech');
            }
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            convertBtn.disabled = false;
            convertBtn.textContent = 'Convert to Speech';
        }
    });

    // Add event listener to handle text input changes
    textInput.addEventListener('input', () => {
        stopAndResetAudio();
    });

    // Function to update the conversion history UI
    function updateConversionHistory() {
        // Clear the history container
        historyContainer.innerHTML = '';
        
        // Add each conversion to the history
        conversions.forEach((conversion, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const timestamp = document.createElement('div');
            timestamp.className = 'history-timestamp';
            timestamp.textContent = `Converted on: ${conversion.timestamp}`;
            
            const voice = document.createElement('div');
            voice.className = 'history-voice';
            
            const voiceEmoji = document.createElement('span');
            voiceEmoji.className = 'history-voice-emoji';
            voiceEmoji.textContent = conversion.emoji;
            
            const voiceName = document.createElement('span');
            voiceName.textContent = `Voice: ${conversion.voiceName} (${conversion.language})`;
            
            voice.appendChild(voiceEmoji);
            voice.appendChild(voiceName);
            
            const device = document.createElement('div');
            device.className = 'history-device';
            
            const deviceEmoji = document.createElement('span');
            deviceEmoji.className = 'history-device-emoji';
            deviceEmoji.textContent = conversion.device === 'cuda' ? '🖥️' : '💻';
            
            const deviceName = document.createElement('span');
            deviceName.textContent = `Device: ${conversion.device === 'cuda' ? 'GPU' : 'CPU'}`;
            
            device.appendChild(deviceEmoji);
            device.appendChild(deviceName);
            
            const text = document.createElement('div');
            text.className = 'history-text';
            text.textContent = `"${conversion.text}"`;
            
            const audio = document.createElement('audio');
            audio.controls = true;
            audio.src = conversion.audioUrl;
            
            historyItem.appendChild(timestamp);
            historyItem.appendChild(voice);
            historyItem.appendChild(device);
            historyItem.appendChild(text);
            historyItem.appendChild(audio);
            
            historyContainer.appendChild(historyItem);
        });
    }
}); 