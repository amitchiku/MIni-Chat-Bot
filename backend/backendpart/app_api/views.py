import base64
import json
import os
import re
import requests
import threading
import google.generativeai as genai
from django.shortcuts import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .RegisterSerializer import RegisterSerializer
from .LoginSerializer import LoginSerializer
from .models import PDFDocument
from .PdfDocumentSerializer import PDFDocumentSerializer
from PyPDF2 import PdfReader

User = get_user_model()


def home(request):
    return HttpResponse("Hello World!")

class LoginView(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'message': 'Error during registration', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        if getattr(request, 'auth', None):
            request.auth.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


def get_tesseract_path():
    from pathlib import Path
    from shutil import which

    env_path = os.environ.get('TESSERACT_CMD')
    if env_path and Path(env_path).exists():
        return env_path

    system_path = which('tesseract')
    if system_path:
        return system_path

    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in possible_paths:
        if Path(path).exists():
            return path
    return None


def extract_text_from_image(uploaded_file):
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        return ''

    def _extract_with_tesseract(file_obj):
        tesseract_path = get_tesseract_path()
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        file_obj.seek(0)
        image = Image.open(file_obj).convert('RGB')
        return pytesseract.image_to_string(image, lang='eng') or ''

    try:
        return _extract_with_tesseract(uploaded_file)
    except Exception:
        try:
            from easyocr import Reader
            uploaded_file.seek(0)
            image = Image.open(uploaded_file).convert('RGB')
            ocr_reader = Reader(['en'], gpu=False)
            results = ocr_reader.readtext(image)
            return ' '.join([text for _, text, _ in results])
        except Exception:
            return ''


def get_gemini_api_key():
    api_key = os.getenv('GEMINI_API_KEY', '').strip() or os.getenv('OPENAI_API_KEY', '').strip()
    if not api_key or api_key.startswith('your_google_gemini_api_key_here'):
        return None, 'GEMINI_API_KEY is not configured or is set to a placeholder value.'
    return api_key, None


def parse_gemini_response(response_json):
    try:
        if isinstance(response_json, dict):
            if 'candidates' in response_json and isinstance(response_json['candidates'], list):
                candidates = response_json['candidates']
                if candidates:
                    first_candidate = candidates[0]
                    if isinstance(first_candidate, dict):
                        if 'content' in first_candidate:
                            content = first_candidate['content']
                            if isinstance(content, dict) and 'parts' in content:
                                parts = content['parts']
                                if isinstance(parts, list):
                                    texts = []
                                    for part in parts:
                                        if isinstance(part, dict) and 'text' in part:
                                            texts.append(str(part['text']).strip())
                                    return ' '.join([t for t in texts if t]).strip()
            if 'output' in response_json:
                output = response_json['output']
                if isinstance(output, list) and output:
                    first_output = output[0]
                    if isinstance(first_output, dict):
                        if 'content' in first_output:
                            content = first_output['content']
                            if isinstance(content, list):
                                texts = []
                                for item in content:
                                    if isinstance(item, dict) and 'text' in item:
                                        texts.append(str(item['text']).strip())
                                    elif isinstance(item, str):
                                        texts.append(item.strip())
                                return ' '.join([t for t in texts if t]).strip()
                        if 'text' in first_output:
                            return str(first_output['text']).strip()
            if 'response' in response_json and isinstance(response_json['response'], str):
                return response_json['response'].strip()
            if 'result' in response_json and isinstance(response_json['result'], str):
                return response_json['result'].strip()
        return ''
    except Exception:
        return ''


def is_gemini_legacy_token(api_key):
    return isinstance(api_key, str) and (api_key.startswith('AQ.') or api_key.startswith('ya29.') or api_key.startswith('ya29-'))


def build_gemini_request(api_key, prompt, model='gemini-1.5-flash', max_output_tokens=256, temperature=0.2):
    """Build request using v1beta generateContent and `contents` payload.

    This deployment uses the API key as a query parameter for simplicity.
    """
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    headers = {
        'Content-Type': 'application/json',
    }

    payload = {
        'contents': [
            {
                'type': 'text',
                'text': prompt,
            }
        ],
        'temperature': temperature,
        'maxOutputTokens': max_output_tokens,
    }

    url = f"{endpoint}?key={api_key}"
    return url, headers, payload


def call_gemini_api(question_text, context_text):
    api_key, error = get_gemini_api_key()

    if error:
        return None, error

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = (
            "You are a document assistant. "
            "Answer the question using only the text from the uploaded document. "
            "If the answer is not present, reply with "
            "'No exact answer found for that question.'\n\n"
            f"Document Text:\n{context_text}\n\n"
            f"Question:\n{question_text}"
        )

        response = model.generate_content(prompt)
        answer = response.text

        if not answer or answer.strip() == '':
            answer = 'No exact answer found for that question.'

        return answer, None

    except Exception as e:
        return None, f"Gemini API error: {str(e)}"


def push_document_to_third_party(title, document_text, model='gemini-2.5-flash'):
    api_key, error = get_gemini_api_key()
    if error:
        return None, error

    try:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(model)

        safe_text = document_text
        if len(safe_text) > 3000:
            safe_text = safe_text[:3000] + '\n\n...[truncated document content]'

        prompt = (
            'This is a document ingestion request. Read the document text and acknowledge receipt. '
            'Do not answer any user questions here; just confirm that the document was received for later use.\n\n'
            f'Document title: {title}\n\nDocument text:\n{safe_text}\n\nAcknowledgement:'
        )

        response = gemini_model.generate_content(prompt)
        return response.text, None
    except Exception as exc:
        return None, f'Gemini API error: {str(exc)}'


def _background_push(title, document_text, pdf_id=None, model='gemini-2.5-flash'):
    try:
        acknowledgement, push_error = push_document_to_third_party(title, document_text, model=model)
        if push_error:
            # keep simple logging; developers can extend to store warnings in DB
            print(f"Background push failed for PDF id={pdf_id}, title={title}: {push_error}")
        else:
            print(f"Background push acknowledgement for PDF id={pdf_id}, title={title}: {acknowledgement}")
    except Exception as e:
        print(f"Unexpected error during background push: {e}")


def answer_question_from_text(text, question):
    if not text or not text.strip():
        return 'No content is available for this document.'

    question_lower = question.lower()
    question_tokens = set(re.findall(r'\w+', question_lower))
    question_tokens = {token for token in question_tokens if len(token) > 2}
    if not question_tokens:
        return 'Please ask a clearer question.'

    section_keywords = {
        'education': ['education', 'school', 'college', 'institute', 'degree', 'cgpa', 'semester'],
        'experience': ['experience', 'work', 'company', 'internship', 'role', 'worked'],
        'projects': ['project', 'projects', 'portfolio', 'website'],
        'skills': ['skill', 'skills', 'technology', 'technologies', 'tools'],
        'certifications': ['certificate', 'certification', 'certifications'],
        'summary': ['summary', 'objective', 'about'],
        'contact': ['email', 'phone', 'contact', 'address']
    }

    def parse_sections(text):
        sections = {}
        current_section = None
        section_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped and re.match(r'^[A-Z][A-Z0-9 &\-\,\.]+$', stripped) and len(stripped) > 3:
                if current_section and section_lines:
                    sections[current_section] = ' '.join(section_lines).strip()
                current_section = stripped
                section_lines = []
            elif current_section:
                section_lines.append(stripped)
        if current_section and section_lines:
            sections[current_section] = ' '.join(section_lines).strip()
        return sections

    def best_sentence_for_text(content, question_tokens):
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', content) if s.strip()]
        scored = []
        for sentence in sentences:
            sentence_tokens = set(re.findall(r'\w+', sentence.lower()))
            score = len(sentence_tokens & question_tokens)
            if score > 0:
                scored.append((score, sentence))
        if scored:
            scored.sort(key=lambda item: (-item[0], len(item[1])))
            return scored[0][1]
        return None

    sections = parse_sections(text)
    matched_section = None
    for section, aliases in section_keywords.items():
        if any(keyword in question_lower for keyword in aliases):
            for heading in sections:
                if section in heading.lower() or any(alias in heading.lower() for alias in aliases):
                    matched_section = sections[heading]
                    break
            if matched_section:
                break

    if matched_section:
        specific_answer = best_sentence_for_text(matched_section, question_tokens)
        if specific_answer:
            return specific_answer
        return matched_section

    specific_answer = best_sentence_for_text(text, question_tokens)
    if specific_answer:
        return specific_answer

    paragraphs = [p.strip() for p in re.split(r'\n{2,}|\.\s+', text) if p.strip()]
    scored_paragraphs = []
    for paragraph in paragraphs:
        paragraph_tokens = set(re.findall(r'\w+', paragraph.lower()))
        score = len(paragraph_tokens & question_tokens)
        if score > 0:
            scored_paragraphs.append((score, paragraph))
    if scored_paragraphs:
        scored_paragraphs.sort(key=lambda item: item[0], reverse=True)
        return scored_paragraphs[0][1]

    return 'No exact answer found for that question. Please try again with a more specific query.'


@api_view(['POST'])
@csrf_exempt
def upload_pdf(request):
    title = request.POST.get('title', '').strip()
    document_text = request.POST.get('text', '').strip()
    uploaded_file = request.FILES.get('file')
    text_content = ''

    if uploaded_file:
        filename = uploaded_file.name.lower()
        content_type = uploaded_file.content_type or ''

        if filename.endswith('.pdf') or 'pdf' in content_type:
            uploaded_file.seek(0)
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text() or ''
                text_content += page_text + '\n'
            if not text_content.strip():
                return Response({'message': 'Could not extract text from the uploaded PDF.'}, status=status.HTTP_400_BAD_REQUEST)
        elif filename.endswith('.txt') or content_type.startswith('text'):
            raw_data = uploaded_file.read()
            try:
                text_content = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                text_content = raw_data.decode('latin1', errors='ignore')
            if not text_content.strip():
                return Response({'message': 'The uploaded text file is empty.'}, status=status.HTTP_400_BAD_REQUEST)
        elif content_type.startswith('image/') or filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
            text_content = extract_text_from_image(uploaded_file)
            if not text_content.strip():
                return Response({'message': 'Could not extract text from the uploaded image. Please use a clear, readable image or ensure OCR support is installed.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Unsupported file type. Upload a PDF, text file, or image.'}, status=status.HTTP_400_BAD_REQUEST)
    elif document_text:
        text_content = document_text
    else:
        return Response({'message': 'No file or text provided for upload.'}, status=status.HTTP_400_BAD_REQUEST)

    if not title:
        title = uploaded_file.name if uploaded_file else 'Untitled Document'

    pdf_document = PDFDocument.objects.create(title=title, embedding=text_content)

    # Push document to third-party in background to avoid slowing down upload response
    try:
        thread = threading.Thread(target=_background_push, args=(pdf_document.title, pdf_document.embedding, pdf_document.id), daemon=True)
        thread.start()
    except Exception as e:
        print(f"Failed to start background push thread: {e}")

    return Response({'message': 'Document uploaded successfully', 'id': pdf_document.id, 'title': pdf_document.title}, status=status.HTTP_201_CREATED)


class PDFDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            pdf_document = PDFDocument.objects.get(pk=pk)
            serializer = PDFDocumentSerializer(pdf_document)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PDFDocument.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


class AskQuestionView(APIView):
    @csrf_exempt
    def post(self, request, format=None):
        question = request.data.get('question', '').strip()
        pdf_id = request.data.get('pdfId')

        if not question:
            return Response({'message': 'Question not provided'}, status=status.HTTP_400_BAD_REQUEST)

        if pdf_id:
            try:
                pdf_document = PDFDocument.objects.get(pk=pdf_id)
            except PDFDocument.DoesNotExist:
                return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            pdf_document = PDFDocument.objects.order_by('-upload_date').first()
            if not pdf_document:
                return Response({'message': 'No documents are available. Upload a document first.'}, status=status.HTTP_404_NOT_FOUND)

        answer, error_message = call_gemini_api(question, pdf_document.embedding)
        if error_message:
            fallback_answer = answer_question_from_text(pdf_document.embedding, question)
            return Response(
                {
                    'answer': fallback_answer,
                    'warning': 'Third-party Gemini API error: ' + error_message + ' — returning a local fallback answer.',
                },
                status=status.HTTP_200_OK,
            )

        return Response({'answer': answer}, status=status.HTTP_200_OK)


class AskQuestionViewWithPdfId(APIView):
    def get(self, request, format=None):
        pdf_id = request.query_params.get('pdfId')
        if not pdf_id:
            return Response({'message': 'PDF id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            pdf_document = PDFDocument.objects.get(pk=pdf_id)
            return Response({'message': 'Successfully retrieved document', 'title': pdf_document.title, 'id': pdf_document.id}, status=status.HTTP_200_OK)
        except PDFDocument.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


class PDFHistoryView(APIView):
    def get(self, request, format=None):
        pdf_documents = PDFDocument.objects.all().order_by('-upload_date')
        pdf_history = []
        for pdf_document in pdf_documents:
            pdf_history.append({
                'id': pdf_document.id,
                'title': pdf_document.title,
                'upload_date': pdf_document.upload_date,
            })
        return Response(pdf_history, status=status.HTTP_200_OK)


@api_view(['GET'])
def test_gemini_api(request):
    """Diagnostic endpoint: lists available Gemini models and tests API connection."""
    api_key, error = get_gemini_api_key()
    if error:
        return Response({'ok': False, 'error': error}, status=status.HTTP_400_BAD_REQUEST)

    try:
        genai.configure(api_key=api_key)
        
        # Try to list available models
        models = genai.list_models()
        model_list = []
        for m in models:
            model_list.append(str(m.name))
        
        if not model_list:
            return Response({'ok': False, 'error': 'No models available'}, status=status.HTTP_502_BAD_GATEWAY)
        
        # Try each model until one works
        last_error = None
        for model_name in model_list[:5]:  # Try first 5 models
            try:
                clean_name = model_name.replace('models/', '')
                model = genai.GenerativeModel(clean_name)
                prompt = 'Say hello.'
                response = model.generate_content(prompt)
                return Response({'ok': True, 'model_used': clean_name, 'answer': response.text[:100], 'all_models': model_list[:10]}, status=status.HTTP_200_OK)
            except Exception as e:
                last_error = str(e)
                continue
        
        return Response({'ok': False, 'error': f'No models worked. Last error: {last_error}', 'available_models': model_list[:10]}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as exc:
        return Response({'ok': False, 'error': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
