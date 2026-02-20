# Vitalis – Detailed Agent Workflow

## Overview

Vitalis is an AI Agent system implemented with **LangGraph** that orchestrates multiple specialized sub-agents to deliver personalized medical consultation via a web chatbot. The system supports three input modalities (text, audio, image) and three query types (general medical advice, personal medical history lookup, multimodal image/audio analysis).

---

## Architecture Summary

```
User (Patient)
    │
    ▼  (Text / Audio / Image)
Frontend (React)
    │
    ▼  REST API
Backend (FastAPI)
    │  Auth (JWT), file upload, conversation storage (MongoDB)
    ▼
Orchestrator Agent (LangGraph)
    ├─► input_router         ← Entry point, validates & classifies input
    ├─► process_speech       ← Speech-to-Text Agent
    ├─► process_image        ← Image Analysis Agent (Derm Foundation)
    ├─► reasoning_node       ← MedGemma LLM (Ollama)
    │       └─► call_tool   ← RAG Agent (Patient Database)
    ├─► safety_check         ← Guardrails: privacy, medical disclaimers
    └─► error_handler        ← Fallback for errors
```

---

## LangGraph State

The workflow state (`AgentState`) carries:

| Field | Type | Description |
|---|---|---|
| `patient_id` | str | Authenticated patient identifier |
| `messages` | list | Conversation history (last 5 messages) |
| `current_input_type` | str | `text` / `speech` / `image` / `multimodal` |
| `user_text_input` | str | Raw text from user |
| `audio_file_path` | str | Path to uploaded audio (.wav/.mp3) |
| `image_file_path` | str | Path to uploaded image (.jpg/.png) |
| `transcribed_text` | str | STT output |
| `image_analysis_result` | dict | Skin disease classification result |
| `rag_context` | dict | Retrieved patient records |
| `rag_needed` | bool | Flag to trigger RAG retrieval |
| `routing_decision` | str | Next node decision |
| `final_response` | str | Generated AI response |
| `emergency_detected` | bool | Emergency flag |
| `safety_check_passed` | bool | Safety validation flag |

---

## Workflow Nodes

### 1. `input_router` (Entry Point)

**Purpose:** Validate input and route to the correct next node.

**Steps:**
1. Determine `input_type` from presence of audio/image/text fields
2. Validate `patient_id` format
3. Validate image file (allowed extensions: jpg, jpeg, png, bmp, webp; max 10MB)
4. Validate audio file (allowed extensions: wav, mp3, ogg, m4a, webm; max 50MB)
5. Set `routing_decision`:
   - `process_speech` → if audio present
   - `process_image` → if image only
   - `reasoning` → if text only
   - `error` → if validation fails

**Outputs:**
- Routes to: `process_speech`, `process_image`, `reasoning`, or `error_handler`

---

### 2. `process_speech` (Speech-to-Text Agent)

**Purpose:** Transcribe audio input to text.

**Model:** Whisper (via `speech_to_text_process` module)

**Steps:**
1. Load audio from `audio_file_path`
2. Run Whisper transcription
3. Post-process and clean transcribed text
4. Store result in `transcribed_text`
5. If image also present → route to `process_image`; else → route to `reasoning`

**Input:** Audio file path (.wav/.mp3/.ogg/.m4a/.webm)  
**Output:** `transcribed_text` (string)

---

### 3. `process_image` (Image Analysis Agent)

**Purpose:** Classify skin condition from image.

**Model:** Derm Foundation (feature extractor) + Logistic Regression classifier

**Steps:**
1. Load image from `image_file_path`
2. Extract embeddings using Derm Foundation model
3. Classify into 8 clinical groups:
   - Acne / Actinic Keratosis / Basal Cell Carcinoma / Dermatitis
   - Eczema / Melanoma / Psoriasis / Rosacea
4. Return `class_name`, `confidence`, `clinical_notes`

**Input:** Image file path (.jpg/.png/.bmp/.webp)  
**Output:** `image_analysis_result` dict:
```json
{
  "class_name": "Eczema",
  "confidence": 0.87,
  "clinical_notes": "Inflammatory skin condition...",
  "all_probabilities": {...}
}
```

Always routes to `reasoning` after completion.

---

### 4. `reasoning_node` (MedGemma LLM)

**Purpose:** Core AI reasoning – generate medical response.

**Model:** MedGemma (via Ollama)

**Steps:**
1. Extract user text (from `user_text_input` or `transcribed_text`)
2. Sanitize and validate input
3. **Emergency Detection:** Check for keywords (chest pain, difficulty breathing, unconscious, etc.) → if emergency, generate emergency response immediately
4. Build LLM context:
   - Include image analysis results if available
   - Include RAG patient records if available
5. **RAG Trigger:** Check if query contains medical-history keywords (`my history`, `my medication`, `my test results`, `my blood pressure`, etc.)
   - If RAG needed and not yet retrieved → route to `call_tool`
6. Call MedGemma via Ollama with system prompt + patient context + conversation history
7. Store `final_response`
8. Route to `safety_check`

**Input:** User query + (optional) image analysis + (optional) RAG context  
**Output:** `final_response` (string medical response)

---

### 5. `call_tool` → `_retrieve_patient_records` (RAG Agent)

**Purpose:** Retrieve patient medical history from vector database.

**Technology:** RAG pipeline (embeddings + vector search over FHIR medical records)

**Steps:**
1. Use `patient_id` + user query as search input
2. Semantic search over vector DB (1000+ FHIR medical records)
3. Retrieve top-K most relevant records
4. Return context with sources

**Input:**
- `patient_id`: string
- `query`: user's question text
- `top_k`: number of records to retrieve (configurable, default 3)

**Output:** `rag_context` dict:
```json
{
  "context": "Patient's last blood test on 2024-01-15 showed...",
  "sources": ["encounter_001", "lab_result_045", "medication_012"]
}
```

After retrieval, routes back to `reasoning_node` with context loaded.

---

### 6. `safety_check` (Guardrails)

**Purpose:** Validate response before returning to user.

**Checks:**
1. Content validation – detect dangerous/inappropriate medical claims
2. Privacy validation – ensure no cross-patient data leakage
3. Response cleaning – strip artifacts, normalize whitespace
4. (Optional) Add medical disclaimer

**Output:** Final cleaned `final_response` → `END`

---

### 7. `error_handler`

**Purpose:** Catch and handle any unrecoverable errors.

**Output:** Generic error message → `END`

---

## Query Type Workflows

### 🔵 Case 1: General Medical Question (Text Only)

```
Input: text = "What are symptoms of diabetes?"

input_router → reasoning_node → safety_check → END

Response: MedGemma explanation of diabetes symptoms
```

**Stages & IO:**

| Stage | Input | Output |
|---|---|---|
| input_router | Text query | routing: reasoning |
| reasoning_node | User text | Medical explanation from MedGemma |
| safety_check | Draft response | Validated final response |

---

### 🟢 Case 2: Personal Medical History Query (RAG)

```
Input: text = "What were my last blood test results?"
       patient_id = "P-12345"

input_router → reasoning_node → call_tool → reasoning_node → safety_check → END

Response: Summary of patient's actual lab results from FHIR database
```

**Stages & IO:**

| Stage | Input | Output |
|---|---|---|
| input_router | Text query | routing: reasoning |
| reasoning_node (1st) | User text | Detects history keyword → routes to call_tool |
| call_tool | patient_id + query | RAG context (relevant FHIR records) |
| reasoning_node (2nd) | Text + RAG context | Personalized response grounded in real records |
| safety_check | Draft response | Validated final response |

---

### 🟡 Case 3: Image Analysis (Skin Condition)

```
Input: image = skin_photo.jpg
       text = "Is this a fungal infection?"

input_router → process_image → reasoning_node → safety_check → END

Response: Skin disease classification + MedGemma explanation
```

**Stages & IO:**

| Stage | Input | Output |
|---|---|---|
| input_router | Image file | routing: process_image |
| process_image | Image (.jpg/.png) | Derm class: "Eczema" (87% confidence) |
| reasoning_node | Text + image analysis | Medical explanation based on classification |
| safety_check | Draft response | Validated final response |

---

### 🟠 Case 4: Voice Query (Speech-to-Text)

```
Input: audio = question.wav
       text = (optional)

input_router → process_speech → reasoning_node → safety_check → END

Response: Same as text query flow after transcription
```

**Stages & IO:**

| Stage | Input | Output |
|---|---|---|
| input_router | Audio file | routing: process_speech |
| process_speech | Audio (.wav/.mp3) | Transcribed text |
| reasoning_node | Transcribed text | Medical response from MedGemma |
| safety_check | Draft response | Validated final response |

---

### 🔴 Case 5: Emergency Detection

```
Input: text = "I have severe chest pain and can't breathe"

input_router → reasoning_node → safety_check → END

Response: EMERGENCY ALERT - Call 115 immediately
```

**Stages & IO:**

| Stage | Input | Output |
|---|---|---|
| input_router | Emergency text | routing: reasoning |
| reasoning_node | Emergency keywords detected | Immediate 911-style emergency response |
| safety_check | Emergency response | Final emergency alert response |

---

### 🟣 Case 6: Multimodal (Audio + Image)

```
Input: audio = voice_question.wav
       image = skin_photo.jpg

input_router → process_speech → process_image → reasoning_node → safety_check → END

Response: Response combining transcribed speech context + image analysis
```

---

## Backend API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/auth/login` | POST | Patient login with patient_id → JWT token |
| `/chat/message` | POST | Send message (text/audio/image) → AI response |
| `/chat/history` | GET | Get conversation history |
| `/files/upload` | POST | Upload audio/image file |

**Auth Flow:**
1. Patient sends `patient_id` to `/auth/login`
2. Backend verifies against hospital database
3. Returns JWT token
4. All subsequent requests include `Authorization: Bearer <token>`

---

## Data Layer

| Storage | Technology | Purpose |
|---|---|---|
| Conversation History | MongoDB | Stores chat sessions and messages |
| Patient Records | FHIR JSON files | 1000+ structured medical records |
| Vector Embeddings | Vector DB | Semantic search for RAG pipeline |
| Uploaded Files | Local FS (`/uploads`) | Temporary audio/image storage |

---

## Safety & Guardrails

| Check | Description |
|---|---|
| Input Validation | File type, size, patient ID format |
| Emergency Detection | Keywords: chest pain, difficulty breathing, unconscious, severe bleeding |
| Content Guardrails | No definitive diagnoses, no dangerous advice |
| Privacy Protection | Responses never expose other patients' data |
| Medical Disclaimer | AI is support tool, not a replacement for doctors |
| Rate Limiting | Prevents API abuse |

---

*Generated: 2026-02-19 | Vitalis v1.0*
