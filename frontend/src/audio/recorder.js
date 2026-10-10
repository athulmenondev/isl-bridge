export class AudioRecorder {
  constructor() {
    this.audioCtx = null;
    this.stream = null;
    this.processor = null;
    this.pcmBuffers = [];
    this.isRecording = false;
  }

  async start(onLevelChange) {
    this.pcmBuffers = [];
    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    this.audioCtx = new AudioContextClass();

    const source = this.audioCtx.createMediaStreamSource(this.stream);
    this.processor = this.audioCtx.createScriptProcessor(4096, 1, 1);

    this.processor.onaudioprocess = (e) => {
      if (!this.isRecording) return;
      const input = e.inputBuffer.getChannelData(0);
      
      if (onLevelChange) {
        let sum = 0;
        for (let i = 0; i < input.length; i++) sum += input[i] * input[i];
        const rms = Math.sqrt(sum / input.length);
        onLevelChange(Math.min(1, rms * 5));
      }

      this.pcmBuffers.push(new Float32Array(input));
    };

    source.connect(this.processor);
    this.processor.connect(this.audioCtx.destination);
    this.isRecording = true;
  }

  async stop() {
    this.isRecording = false;
    if (this.processor) this.processor.disconnect();
    if (this.stream) this.stream.getTracks().forEach((track) => track.stop());
    
    const nativeSampleRate = this.audioCtx ? this.audioCtx.sampleRate : 44100;
    if (this.audioCtx) await this.audioCtx.close();

    let totalLength = 0;
    for (const buf of this.pcmBuffers) totalLength += buf.length;
    
    if (totalLength === 0) {
      return null;
    }

    const merged = new Float32Array(totalLength);
    let offset = 0;
    for (const buf of this.pcmBuffers) {
      merged.set(buf, offset);
      offset += buf.length;
    }

    // Resample to 16000 Hz if native AudioContext sample rate is different
    const resampled = this._resample(merged, nativeSampleRate, 16000);
    return this._encodeWAV(resampled, 16000);
  }

  _resample(samples, fromRate, toRate) {
    if (fromRate === toRate) return samples;
    const ratio = fromRate / toRate;
    const newLength = Math.round(samples.length / ratio);
    const result = new Float32Array(newLength);
    for (let i = 0; i < newLength; i++) {
      const pos = i * ratio;
      const index = Math.floor(pos);
      const frac = pos - index;
      const nextIndex = Math.min(index + 1, samples.length - 1);
      result[i] = samples[index] * (1 - frac) + samples[nextIndex] * frac;
    }
    return result;
  }

  _encodeWAV(samples, sampleRate) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    this._writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    this._writeString(view, 8, 'WAVE');
    this._writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    this._writeString(view, 36, 'data');
    view.setUint32(40, samples.length * 2, true);

    let offset = 44;
    for (let i = 0; i < samples.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }

    return new Blob([view], { type: 'audio/wav' });
  }

  _writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }
}