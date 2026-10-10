import React, { useState, useRef } from 'react';
import { AudioRecorder } from '../audio/recorder';

export default function MicButton({ onSpeechPayload, onLog, language }) {
  const [recording, setRecording] = useState(false);
  const [level, setLevel] = useState(0);
  const recorderRef = useRef(null);

  const toggleRecording = async () => {
    if (!recording) {
      try {
        recorderRef.current = new AudioRecorder();
        await recorderRef.current.start((vol) => setLevel(vol));
        setRecording(true);
        onLog('Recording started... Speak into microphone.');
      } catch (err) {
        onLog(`Microphone access error: ${err.message}`);
      }
    } else {
      setRecording(false);
      setLevel(0);
      onLog('Processing speech input...');

      try {
        const wavBlob = await recorderRef.current.stop();
        if (!wavBlob) {
          onLog('Recording failed: Audio buffer was empty.');
          return;
        }

        const formData = new FormData();
        formData.append('audio', wavBlob, 'input.wav');
        formData.append('language', language);

        const res = await fetch('/translate/speech', {
          method: 'POST',
          body: formData,
        });

        const rawText = await res.text();
        let data;
        try {
          data = JSON.parse(rawText);
        } catch (e) {
          onLog(`Server Error (${res.status}): Server returned non-JSON body.`);
          return;
        }

        if (res.ok) {
          onSpeechPayload(data);
        } else {
          onLog(`Speech ASR error: ${data.error || 'Transcription failed'}`);
        }
      } catch (err) {
        onLog(`Network error during speech upload: ${err.message}`);
      }
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <button
        onClick={toggleRecording}
        style={{
          background: recording ? 'var(--error-red)' : 'var(--accent-purple)',
        }}
      >
        {recording ? '⏹ Stop Recording' : '🎤 Speak'}
      </button>

      {recording && (
        <div
          style={{
            width: '60px',
            height: '10px',
            background: '#232936',
            borderRadius: '5px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${Math.round(level * 100)}%`,
              height: '100%',
              background: 'var(--ok-green)',
              transition: 'width 0.05s ease',
            }}
          />
        </div>
      )}
    </div>
  );
}