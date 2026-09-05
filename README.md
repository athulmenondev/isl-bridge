# isl-brifge


# Project Specification: AI-Powered Low-Latency Bidirectional Indian Sign Language (ISL) Translation System 

- Base Framework: Smart India Hackathon (SIH) Problem ID: 183 

- Document Version: 1.0 

- Status: Architecture & Engineering Specification 

## 1. Executive Summary & Core Concept 

### 1.1 Project Overview 

The AI-Powered Low-Latency Bidirectional Indian Sign Language (ISL) Translation System is a real-time, two-way communication platform designed to eliminate the barrier between the Deaf/Hard-of-Hearing (DHH) community and the hearing population. Traditional systems often rely on unidirectional dictionaries or static, pre-recorded video clip stitching. In contrast, this platform operates using a unified split-screen Web User Interface that concurrently handles simultaneous multi-modal streams. 

### 1.2 Dual-Pane Interface Concept 

- Left Canvas (Hearing-to-Deaf Path): Captures spoken English or Hindi audio, converts speech into text, translates English/Hindi syntax into authentic Indian Sign Language (ISL) Gloss, and renders the gestures through a dynamic 3D digital avatar. 

- Right Canvas (Deaf-to-Hearing Path): Captures live camera feeds via webcam, extracts 3D spatial body and hand landmarks, decodes continuous ISL gestures into structured text, and synthesizes natural audio output. 

### 1.3 System Overview Diagram

```text
+-------------------------------------------------------------------------+
|               UNIFIED DUAL-PANE WEB DASHBOARD                           |
|                         (React / Tailwind)                              |
+------------------------------------+------------------------------------+
| LEFT CANVAS: SPOKEN → ISL          | RIGHT CANVAS: ISL → SPEECH         |
|                                    |                                    |
| [Audio Input]                      | [Webcam Stream]                    |
|  English / Hindi                   |  Live Video Feed                   |
|        |                           |        |                           |
|        v                           |        v                           |
| (Speech-to-Text ASR Engine)        | (MediaPipe Holistic Keypoints)     |
|        |                           |        |                           |
|        v                           |        v                           |
| (ISL NLP Syntax Parser)             | (Spatial-Temporal Transformer)    |
|        |                           |        |                           |
|        v                           |        v                           |
| (HamNoSys → SiGML Engine)          | (Inferred Text Token Stream)       |
|        |                           |        |                           |
|        v                           |        v                           |
| [3D Avatar WebGL Rendering]        | [Synthesized Audio Output]         |
+------------------------------------+------------------------------------+
|          ASYNCHRONOUS WEBSOCKET / FASTAPI BACKEND BUS                   |
+-------------------------------------------------------------------------+
```



## 2. System Architecture & The 5-Step Linguistic Transformation Pipeline 


To generate accurate real-time 3D animations from natural audio, spoken sentences must undergo structural translation into the unique grammar of ISL. Unlike English or Hindi (which generally follow Subject-Verb-Object structures), ISL utilizes Subject-Object-Verb (SOV) syntax, omits auxiliary verbs and articles, and operates on root-word tokens. 

### 2.1 Transformation Flow Diagram

```text
┌──────────────────────────────────────────────┐
│      Spoken Audio (English / Hindi)          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
       Step 1: Speech-to-Text ASR Engine
                       │
                       ▼
              ┌─────────────────┐
              │ Raw Text String │
              └────────┬────────┘
                       │
                       ▼
       Step 2: NLP Syntax Parser & Reordering
                       │
                       ▼
              ┌──────────────────┐
              │ ISL Gloss Stream │
              └────────┬─────────┘
                       │
                       ▼
       Step 3: Phonetic Transcription Lexicon
                       │
                       ▼
              ┌───────────────────┐
              │ HamNoSys Notation │
              └────────┬──────────┘
                       │
                       ▼
              Step 4: XML Script Generator
                       │
                       ▼
              ┌───────────────────┐
              │ SiGML Data Stream │
              └────────┬──────────┘
                       │
                       ▼
      Step 5: WebGL / Three.js Render Pipeline
                       │
                       ▼
              ┌─────────────────┐
              │ Fluid 3D Avatar │
              │     Motion      │
              └─────────────────┘
```

### 2.2 Detailed Pipeline Stages 

- 1. Speech-to-Text (ASR): Captures incoming microphone streams and transcribes them into text using localized automatic speech recognition. 

- 2. NLP Syntax Parser: Strips non-essential grammatical tokens (e.g., articles like a, an, the; helping verbs like is, am, are) and reorders English/Hindi Subject-Verb-Object (SVO) structures into authentic ISL Subject-Object-Verb (SOV) Gloss tokens. 

- 3. HamNoSys Transcription: Maps ISL Gloss tokens to the Hamburg Notation System (HamNoSys), defining the physical execution parameters of each sign (handshape, palm orientation, location, and movement trajectory). 

- 4. SiGML Generation: Converts HamNoSys structural symbols into Signing Gesture Markup Language (SiGML), an XML-compliant format designed for WebGL animation engines. 

- 5. 3D Avatar Rendering: WebGL engines (Three.js) parse the XML tags to dynamically position, interpolate, and execute joint rotations on a skeletal 3D avatar rig. 

## 3. Modular Engineering Division (4-Member Strategy)

To facilitate independent verification, unit testing, and isolated performance profiling, the core system architecture is divided into four distinct modules:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODULE 1 — MEMBER 1 OWNER                            │
│                                                                         │
│                Speech Recognition & ISL NLP Engine                      │
│                                                                         │
│  Inputs  : Live Microphone Stream (English / Hindi)                     │
│  Outputs : Structured ISL Gloss Tokens                                  │
│  Tech    : Whisper / Vosk ASR                                           │
│            Python NLTK / spaCy                                          │
│            Rule-Based Syntax Transformation                             │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODULE 2 — MEMBER 2 OWNER                            │
│                                                                         │
│             HamNoSys / SiGML & 3D Avatar WebGL Engine                   │
│                                                                         │
│  Inputs  : ISL Gloss Tokens                                             │
│  Outputs : Smooth 60 FPS Skeletal 3D Avatar Movements                   │
│  Tech    : SiGML XML Parser                                             │
│            Three.js / WebGL                                             │
│            Blender Character Rig                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODULE 3 — MEMBER 3 OWNER                            │
│                                                                         │
│           Computer Vision & Sign-to-Text Deep Learning                  │
│                                                                         │
│  Inputs  : Real-Time Video Camera Feed                                  │
│  Outputs : Inferred Text Sentences                                      │
│  Tech    : MediaPipe Holistic (543 Keypoints)                           │
│            Spatial-Temporal Transformer / Deep Learning Model           │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODULE 4 — MEMBER 4 OWNER                            │
│                                                                         │
│             Audio Synthesis & Split-Screen UI Platform                  │
│                                                                         │
│  Inputs  : Inferred Text Tokens & Dual Data Pipes                       │
│  Outputs : Synthesized Natural Speech Audio Output                      │
│            & Integrated Web Application                                 │
│  Tech    : React.js, Tailwind CSS                                       │
│            WebSockets, FastAPI Core Backend                             │
│            Edge-TTS                                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

## 4. In-Depth Technical Specification by Module 

### Module 1: Speech Recognition & ISL NLP Engine 

Owner: Team Member 1 

- Objective: Capture continuous multi-lingual speech and convert it into grammatical ISL Gloss tokens. 

Core Pipeline: 

1. Audio is captured via Web Audio API and routed to a localized speech recognition model (e.g., Whisper-Base or Vosk) to minimize network API latency. 

2. Transcribed plain text passes into a custom Natural Language Processing (NLP) rulebased pipeline. 

3. Dependency parsing identifies nouns, verbs, and direct objects. 

4. Suffixes and inflections are lemmatized to their root forms (e.g., "running" → RUN ). 

5. Words are reordered into SOV order, and stop-words are filtered out. Verification Method: Unit-tested via custom log feeds comparing raw input text against expected ISL Gloss arrays. 

### Module 2: HamNoSys/SiGML & 3D Avatar WebGL Engine 

Owner: Team Member 2 

Objective: Transform text-based ISL Gloss into continuous, natural 3D character movements without motion stuttering. 



<!-- Start of picture text -->
expand<br>tune<br>chat_spark<br><!-- End of picture text -->

Core Pipeline: 

1. Receives Gloss tokens from Module 1 and looks up corresponding HamNoSys structural codes in an extended dictionary. 

2. Converts HamNoSys parameters (handshape, palm orientation, location, movement profile) into valid XML SiGML streams. 

3. The SiGML player parses bone rotation vectors and streams them to a Three.js WebGL canvas. 

4. Applies Slerp (Spherical Linear Interpolation) to blend transitions between consecutive signs, preventing abrupt snapping between positions. 

- Verification Method: Isolated WebGL test bench measuring render frame rates ( ≥55 FPS ) and verifying bone position vectors against manual sign reference images. 

### Module 3: Computer Vision & Sign-to-Text Deep Learning 

- Owner: Team Member 3 

- Objective: Detect dynamic hand gestures, body postures, and facial expressions from a live camera feed and classify them into text. 

Core Pipeline: 

1. Captures live camera frames at 30 FPS and passes them through MediaPipe Holistic. 2. Extracts 543 3D spatial landmark coordinates ( 33 pose landmarks, 468 face landmarks, 21 keypoints per hand). 

3. Normalizes spatial coordinates relative to neck/shoulder reference points to achieve distance invariance relative to the camera. 

4. Passes sequences of normalized coordinate frames into a temporal neural network (LSTM or Spatial-Temporal Transformer) trained on benchmark datasets (e.g., INCLUDE, ISLCSLTR). 

5. Outputs predicted word tokens and constructs coherent sentence predictions. 

- Verification Method: Confusion matrix evaluations measuring classification accuracy ( ≥90% ) across test sign video samples. 

### Module 4: Audio Synthesis & Split-Screen UI Platform 

Owner: Team Member 4 

- Objective: Integrate all four modules into a cohesive interface, handle asynchronous clientserver data streams, and synthesize clear voice audio. 

Core Pipeline: 

1. Constructs a responsive dual-pane web application using React.js and Tailwind CSS. 

2. Implements an asynchronous FastAPI + WebSocket backend to maintain full-duplex communication with low transmission overhead. 

3. Receives text predictions from Module 3 and routes them to a neural Text-to-Speech engine (e.g., Edge-TTS or gTTS). 

4. Plays synthesized audio streams through the client interface with minimal buffer delay. Verification Method: End-to-end network latency testing measuring glass-to-glass delay ( < 1.2 seconds ) across both communication paths. 

## 5. Technical Comparison with Existing Approaches

| Feature / Dimension      | Traditional Dictionaries / Translators | Video-Stitching Systems        | Our Proposed Modular Solution                      |
| ------------------------ | -------------------------------------- | ------------------------------ | -------------------------------------------------- |
| **Directionality**       | Unidirectional (Text-to-Sign only)     | Unidirectional (Text-to-Video) | **Full Bidirectional (Audio ↔ Sign)**              |
| **Grammatical Fidelity** | Word-for-Word Literal Mapping          | Word-for-Word Literal Mapping  | **True ISL Grammar (SOV Reordering)**              |
| **Animation Quality**    | Pre-recorded Video Clips               | Choppy Video Cuts              | **Fluid 3D Avatar with Vector Interpolation**      |
| **Extensibility**        | Fixed Video Repositories               | Hard-Coded Video Assets        | **Parametric SiGML / HamNoSys Dynamic Rigging**    |
| **System Architecture**  | Monolithic Codebase                    | Static File Server             | **4-Node Decoupled Micro-Services via WebSockets** |




## 6. Real-World Use Cases 

1. Public Infrastructure & Transit Hubs: Deployment at railway enquiry counters, airport boarding gates, and bus terminals where real-time audio announcements are converted to 3D avatar animations on public display monitors, while deaf passengers can sign into terminal cameras to receive audio-synthesized assistance. 

2. Inclusive Educational Desks: Integration into classroom setups to facilitate communication between hearing teachers and DHH students. Teachers speak naturally while the avatar renders the lesson in sign language; students sign back and the system plays spoken responses through classroom speakers. 

3. Healthcare & Emergency Counters: Implementation at hospital reception desks and triage units, enabling medical staff and deaf patients to exchange critical health information accurately without waiting for an on-site human interpreter. 

## 7. Performance Targets & Evaluation Metrics 

To validate the platform during project reviews, the system is evaluated against four quantitative performance metrics: 

1. End-to-End Latency: 

End-to-End Latency = _T_ Audio Input ⟶ _T_ Avatar Render start ≤ 1.2 seconds 

2. Gesture Recognition Accuracy: 

Correctly Classified Gestures Gesture Recognition Accuracy = ≥ 90% Total Test Gestures 

3. Frame Rendering Rate: 

Frame Rendering Rate = Animation Output Speed ≥50 FPS (WebGL Canvas 



#### 4. Word Error Rate (WER): 

Word Error Rate (WER) = 

_S_ + _D_ + _I_ ≤ 10% (for Module 1 ASR Output) _N_ 

(Where _S_ is Substitutions, _D_ is Deletions,  is Insertions, and _I N_ is Total Words) 

## 8. Conclusion 

By addressing Smart India Hackathon Problem ID 183 with a distributed, 4-member modular architecture, this project provides a scalable, production-ready solution to sign language translation. 

The division into distinct pipelines (Speech/NLP Parser, 3D Avatar Engine, Computer Vision Gesture Classifier, and Audio Synthesis/UI Core) ensures that each component can be independently tested, optimized, and verified. The resulting platform delivers an accessible, low-latency, bidirectional bridge between spoken language and Indian Sign Language. 


