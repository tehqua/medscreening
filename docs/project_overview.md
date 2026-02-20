# Project Overview: AI-Powered Medical Consultation System

## 🎯 Introduction

**Vitalis** is an AI Agent system designed to provide intelligent medical consultation services for hospital patients. The system combines advanced AI technology with electronic medical record databases to deliver personalized, accurate, and convenient healthcare consultation experiences.

---

## 🏥 Problems to Solve

### 1. **Difficulty in Accessing Medical Information**

Patients often face challenges when:
- Needing urgent medical advice outside of doctors' office hours
- Wanting to better understand their health condition
- Needing to access their personal medical history
- Uncertain about minor symptoms and whether they need to visit the hospital

### 2. **Healthcare Staff Overload**

- Doctors must repeatedly answer similar questions from patients
- Medical staff spend time explaining basic medical information
- Traditional consultation systems don't leverage existing medical record data

### 3. **Lack of Multimodal Analysis Capability**

- Patients can only describe symptoms verbally but struggle to articulate them accurately
- Images of skin lesions or affected areas require professional analysis
- Lack of tools for preliminary self-examination before hospital visits

---

## 💡 Solution

**Vitalis** provides a comprehensive AI Agent system with the following features:

### ✅ **Intelligent Medical Consultation**

The system uses a specialized medical AI model (**MedGemma**) to:
- Answer questions about health and diseases
- Provide medical advice based on medical knowledge
- Explain medical terminology in understandable terms
- Recommend when hospital visits are necessary

### ✅ **Personal Medical History Lookup**

Patients can:
- Ask about their own medical history
- Look up previous test results and diagnoses
- View medical examination and treatment history
- Receive advice based on personal health records

> **Technology:** Uses RAG (Retrieval-Augmented Generation) to retrieve information from the hospital's electronic medical record database

### ✅ **Medical Image Analysis**

The system is capable of:
- Analyzing images of affected skin areas
- Identifying skin diseases (fungal infections, dermatitis, etc.)
- Classifying severity levels
- Providing preliminary assessments to support decisions about seeing a doctor

> **Technology:** Uses Deep Learning models (Derm Foundation + Logistic Regression) to classify skin diseases into 8 clinical groups

### ✅ **Voice Recognition**

Patients can:
- Ask questions by voice instead of typing
- Convenient for elderly users or those with typing difficulties
- Enhance convenience and user experience

> **Technology:** Speech-to-Text processing to convert audio to text

---

## 🏗️ System Architecture

### **Main Components**

```
┌─────────────────────────────────────────────────────────────┐
│                       USER (Patient)                         │
│              - Login with Patient ID                         │
│              - Interact via Website Chatbot                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │  Input: Text | Voice | Image
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Website)                        │
│                  - Chatbot interface                         │
│                  - Upload image/audio files                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │  REST API
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                 BACKEND API (FastAPI)                        │
│  - User authentication (JWT)                                │
│  - File upload processing                                   │
│  - Conversation history storage                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              AI ORCHESTRATOR (LangGraph)                     │
│          Coordinates specialized AI Agents                   │
│  ┌──────────────────────────────────────────────────┐      │
│  │  1. Input Router                                 │      │
│  │     Classifies query type:                       │      │
│  │     • General medical questions                  │      │
│  │     • Medical history queries                    │      │
│  │     • Image analysis                             │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────┬──────────────────┬─────────────────┐ │
│  │  Speech-to-Text  │  Image Analysis  │  Patient DB RAG │ │
│  │     Agent        │      Agent       │      Agent      │ │
│  └──────────────────┴──────────────────┴─────────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  Medical LLM (MedGemma)                          │      │
│  │  - Synthesizes information from agents           │      │
│  │  - Generates accurate medical responses          │      │
│  │  - Adds disclaimers and safety recommendations   │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────────────────┐
│                        DATABASE                              │
│  • MongoDB: Stores conversations, sessions                  │
│  • Vector DB: Stores medical record embeddings (RAG)        │
│  • Hospital Data: FHIR-formatted medical records            │
└──────────────────────────────────────────────────────────────┘
```

### **3 Main Query Types**

#### 1️⃣ **General Medical Questions**
- User asks about symptoms, diseases, prevention
- Processing: Directly routed to MedGemma LLM
- Example: "What are the symptoms of diabetes?"

#### 2️⃣ **Personal Medical History Queries**
- User asks about their own medical history, test results
- Processing: RAG Agent → Retrieves data from Patient Database → MedGemma
- Example: "What were my last blood test results?"

#### 3️⃣ **Multimodal Analysis (Text + Image/Audio)**
- User sends images or audio with questions
- Processing: Image/Speech Agent → Analysis → MedGemma synthesis
- Example: *[Sends image of red skin area]* "Is this a fungal infection?"

---

## 👥 Target Users

### **Users: Patients**

- Patients registered at the hospital
- Have a unique **Patient ID**
- Have medical records stored in the hospital system

### **Usage Flow:**

1. **Login:** Enter Patient ID
2. **Ask questions:** Type text, speak, or upload images
3. **Receive consultation:** AI analyzes and provides advice
4. **Look up history:** Query personal medical records

---

## 📥 System Input

| Input Type | Description | Example |
|------------|-------------|---------|
| **Text** | Text-based questions | "I have a headache for 2 days" |
| **Speech** (optional) | Voice questions | *[Audio file .wav/.mp3]* |
| **Image** (optional) | Images of affected skin areas | *[Image file .jpg/.png]* |

---

## 🔐 Security and Privacy

### **User Authentication**

- Login using **Patient ID** (pre-assigned)
- Uses **JWT Token** to secure sessions
- Each patient can only access their own records

### **Medical Data Protection**

- Complies with medical information security regulations
- Medical record data isolated by Patient ID
- Connection encryption (HTTPS in production)
- Rate limiting to prevent abuse

---

## 📊 System Data

### **Hospital Medical Records (FHIR Format)**

The system utilizes **over 1,000 detailed medical records** in FHIR (Fast Healthcare Interoperability Resources) format, including:
- Patient demographics
- Clinical encounters
- Laboratory observations
- Medication prescriptions
- Condition diagnoses
- Medical procedures
- *...and more comprehensive healthcare data*

### **Vector Database**

- Converts medical record data into embeddings
- Enables semantic search capabilities
- Rapid retrieval of information relevant to queries

---

## ✨ Key Features

### 🎯 **Personalized Consultation**

- Based on individual patient medical history
- AI understands context and medical background
- Recommendations tailored to personal health status

### 🖼️ **Intelligent Image Analysis**

- Upload images of affected skin areas
- AI analyzes and classifies diseases
- Results include confidence scores
- Suggests whether doctor consultation is needed

### 🎤 **Voice Communication**

- Ask questions by voice
- System automatically converts to text
- Convenient for elderly users

### 🔍 **Fast Medical History Lookup**

- Query previous test results
- View medical examination history
- Check prescribed medications

### ⚡ **Real-time Response**

- Chatbot responds immediately
- No need to wait for doctor appointments
- Available 24/7

---

## 🎓 Important Notes

### ⚠️ **Medical Disclaimer**

> **Vitalis is a consultation support tool, NOT a replacement for real doctors.**

- The system provides reference information
- Always recommends seeing a doctor when necessary
- Does not provide definitive diagnoses
- Detects emergency situations and advises immediate hospital visits

### 🎯 **System Objectives**

- **Education:** Help patients understand their health
- **Screening:** Classify severity levels
- **Support:** Provide information before consultations
- **Time-saving:** Reduce workload for medical staff

---

## 📈 Benefits

### **For Patients**

✅ Easy and fast access to medical information  
✅ Preliminary consultation before hospital visits  
✅ Convenient medical history lookup  
✅ Free for hospital patients  

### **For Hospitals**

✅ Reduce basic consultation workload for doctors  
✅ Improve patient care service quality  
✅ Leverage existing medical record data  
✅ Enhance digital healthcare experience  

---

## 🔮 Future Development

- [ ] Integration of specialized AI models (cardiology, pulmonology, etc.)
- [ ] Multi-language support
- [ ] Mobile applications (iOS/Android)
- [ ] Direct video calls with doctors
- [ ] Nutrition and exercise consultation chatbots
- [ ] Medication and follow-up appointment reminders

---

**Vitalis** - *AI-Powered Healthcare for You* 🏥💙
