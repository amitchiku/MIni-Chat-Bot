# 🤖 ChatBot AI – Intelligent Document Q&A System

An AI-powered document question-answering platform built with **React, Django, Tailwind CSS, RAG (Retrieval-Augmented Generation), OCR, JWT Authentication, and SQLite/MySQL**. The application allows users to upload PDFs, images, or text documents, store them securely, and interact with the uploaded content using natural language queries.

---

## 🚀 Features

### 🔐 Authentication & Authorization

* User Registration
* User Login
* JWT Authentication
* Protected Routes
* Secure API Access

### 📄 Document Processing

* Upload PDF Documents
* Upload Images (PNG, JPG, JPEG)
* Upload Text Files
* OCR-based Text Extraction
* Automatic Content Processing

### 🧠 AI-Powered Question Answering

* Retrieval-Augmented Generation (RAG)
* Semantic Search
* Context-Aware Responses
* Document-Based Chat
* Accurate Information Retrieval

### 📚 User History

* Store Uploaded Documents
* Track User Conversations
* Retrieve Previous Queries
* Manage Document Records

### 💾 Database Management

* Store User Information
* Store Uploaded Files
* Store Extracted Text
* Store Chat History
* Maintain Query Logs

### 🎨 Modern UI/UX

* Responsive Design
* Tailwind CSS Styling
* Interactive Components
* Clean Dashboard
* Mobile Friendly Interface

---

## 🛠️ Tech Stack

### Frontend

* React.js
* JavaScript (ES6+)
* Tailwind CSS
* Axios
* React Router DOM

### Backend

* Django
* Django REST Framework
* JWT Authentication
* Python

### AI & NLP

* RAG (Retrieval-Augmented Generation)
* OCR (Optical Character Recognition)
* Semantic Search
* Document Retrieval Pipeline

### Database

* SQLite (Development)
* MySQL (Production Ready)

### Version Control

* Git
* GitHub

---

## 📂 Project Structure

```bash
Chat-with-pdf/
│
├── front-end/
│   │
│   ├── public/
│   │
│   ├── src/
│   │   ├── components/
│   │   │
│   │   ├── Auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── Profile.jsx
│   │   │
│   │   ├── Display/
│   │   │   └── ChatUI.jsx
│   │   │
│   │   ├── Upload/
│   │   ├── Search/
│   │   ├── UserHistory/
│   │   │
│   │   ├── utils/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── App.css
│   │
│   └── package.json
│
├── backend/
│   │
│   ├── app_api/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── LoginSerializer.py
│   │   ├── RegisterSerializer.py
│   │   └── PdfDocumentSerializer.py
│   │
│   ├── backendpart/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── manage.py
│   └── db.sqlite3
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ System Workflow

### Step 1: User Authentication

* User registers an account.
* JWT token is generated after login.

### Step 2: Document Upload

* Upload PDF, Image, or Text File.
* File is stored in the database.

### Step 3: Text Extraction

* OCR extracts text from images.
* PDF parser extracts document content.

### Step 4: Knowledge Processing

* Extracted content is processed.
* Data is indexed for retrieval.

### Step 5: User Query

* User asks questions related to uploaded content.

### Step 6: RAG Retrieval

* Relevant information is retrieved from stored knowledge.

### Step 7: AI Response

* Context-aware response is generated and displayed.

---

## 🔧 Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/chatbot-ai.git
cd chatbot-ai
```

### Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py runserver
```

### Frontend Setup

```bash
cd front-end

npm install

npm start
```

---

## 🌐 API Modules

### Authentication APIs

* Register User
* Login User
* JWT Token Generation

### Document APIs

* Upload PDF
* Upload Image
* Upload Text

### Chat APIs

* Ask Questions
* Retrieve Answers
* Conversation History

### User APIs

* User Profile
* User Documents
* Query History

---

## 🔒 Security Features

* JWT Authentication
* Protected APIs
* User-Specific Data Isolation
* Secure File Uploads
* Input Validation
* Authentication Middleware

---

## 📈 Future Enhancements

* OpenAI Integration
* LangChain Support
* Pinecone Vector Database
* FAISS Vector Search
* Multi-Language OCR
* Voice Assistant
* Real-Time Chat
* Cloud Deployment (AWS/Azure/GCP)
* Docker Support
* Kubernetes Deployment

---

## 🎯 Use Cases

* Research Document Analysis
* Educational Q&A Systems
* Enterprise Knowledge Base
* Legal Document Search
* Medical Document Insights
* Personal Document Assistant

---

👨‍💻 Author
Amit Nayak And Baibhab Moharan
📧 Email: amitchiku2006@gmail.com
📧 Email: baibhabamoharana19@gmail.com


🐙 GitHub: https://github.com/amitchiku
🐙 GitHub: https://github.com/baibhab-19


### Skills

* React.js
* JavaScript
* Django
* Python
* Tailwind CSS
* MySQL
* Git & GitHub
* OCR
* RAG Systems
* REST APIs

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

Contributions, suggestions, and feedback are always welcome.
