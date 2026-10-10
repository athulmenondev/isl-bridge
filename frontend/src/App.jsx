import React, { useState, useEffect, useRef } from 'react';
import MicButton from './components/MicButton';

export default function App() {
  const [inputText, setInputText] = useState('');
  const [language, setLanguage] = useState('en');
  const [sequence, setSequence] = useState([]);
  const [currentStepIdx, setCurrentStepIdx] = useState(-1);
  const [logs, setLogs] = useState([]);
  const [videoSrc, setVideoSrc] = useState(null);

  const videoRef = useRef(null);

  const addLog = (msg) => {
    setLogs((prev) => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev]);
  };

  const handleTranslateText = async () => {
    if (!inputText.trim()) return;
    addLog(`Translating text: "${inputText}"`);

    try {
      const res = await fetch('/translate/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText, language }),
      });
      const data = await res.json();
      playPayload(data);
    } catch (err) {
      addLog(`Error: ${err.message}`);
    }
  };

  const playPayload = (payload) => {
    if (payload.source && payload.source.text) {
      addLog(`ASR Transcript: "${payload.source.text}" (${payload.source.lang})`);
    }
    addLog(`Received sequence with ${payload.sequence.length} steps.`);
    setSequence(payload.sequence);
    setCurrentStepIdx(0);
  };

  useEffect(() => {
    if (currentStepIdx >= 0 && currentStepIdx < sequence.length) {
      const step = sequence[currentStepIdx];
      let url = null;

      if (step.kind === 'sign') {
        url = step.url;
      } else if (step.kind === 'letter') {
        url = `/static/signfiles/${step.letter.toLowerCase()}.mp4`;
      }

      setVideoSrc(url);

      // Long safety guard timer (15s) in case a stream stalls without triggering onEnded or onError
      const guardTimer = setTimeout(() => {
        addLog(`Step ${currentStepIdx + 1} timed out, skipping...`);
        setCurrentStepIdx((prev) => prev + 1);
      }, 15000);

      return () => clearTimeout(guardTimer);
    } else if (currentStepIdx >= sequence.length && sequence.length > 0) {
      addLog('Sequence playback completed.');
      setCurrentStepIdx(-1);
      setVideoSrc(null);
    }
  }, [currentStepIdx, sequence]);

  const handleVideoEnded = () => {
    // Advance naturally when the MP4 finishes playing completely
    setCurrentStepIdx((prev) => prev + 1);
  };

  const handleVideoError = () => {
    // Skip to next step immediately if the file is missing or corrupted
    setCurrentStepIdx((prev) => prev + 1);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>ISL Bridge — Spoken to Indian Sign Language</h1>

      <div className="dashboard-layout">
        <div className="panel">
          <h3>Input Panel</h3>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="auto">Auto Detect</option>
            </select>
            <input
              type="text"
              placeholder="Type sentence..."
              style={{ flex: 1 }}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleTranslateText()}
            />
            <button onClick={handleTranslateText}>Translate</button>

            <MicButton
              language={language}
              onSpeechPayload={playPayload}
              onLog={addLog}
            />
          </div>

          <h3>Event Log</h3>
          <div className="event-log">
            {logs.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </div>
        </div>

        <div className="panel">
          <h3>ISL Sign Video Stage</h3>
          <div style={{ background: '#000', borderRadius: '8px', height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {videoSrc ? (
              <video
                key={videoSrc}
                ref={videoRef}
                src={videoSrc}
                autoPlay
                muted
                playsInline
                onEnded={handleVideoEnded}
                onError={handleVideoError}
                style={{ maxHeight: '100%', maxWidth: '100%' }}
              />
            ) : (
              <span style={{ color: 'var(--text-muted)' }}>No Active Sign</span>
            )}
          </div>

          <h3>Sequence Timeline</h3>
          <div className="timeline-chips">
            {sequence.map((step, idx) => (
              <span
                key={idx}
                className={`chip ${step.kind} ${idx === currentStepIdx ? 'active' : ''}`}
              >
                {step.kind === 'sign' ? `▶ ${step.asset}` : `🔤 ${step.letter}`}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}