import re
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


def extract_text_from_image(uploaded_file):
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        return ''
    try:
        image = Image.open(uploaded_file)
        return pytesseract.image_to_string(image) or ''
    except Exception as exc:
        return ''


def answer_question_from_text(text, question):
    if not text:
        return 'No content is available for this document.'

    question_tokens = set(re.findall(r'\w+', question.lower()))
    question_tokens = {token for token in question_tokens if len(token) > 2}
    if not question_tokens:
        return 'Please ask a clearer question.'

    paragraphs = [p.strip() for p in re.split(r'\n{2,}|\.\s+', text) if p.strip()]
    scored = []
    for paragraph in paragraphs:
        paragraph_tokens = set(re.findall(r'\w+', paragraph.lower()))
        score = len(paragraph_tokens & question_tokens)
        if score > 0:
            scored.append((score, paragraph))

    if scored:
        scored.sort(key=lambda item: item[0], reverse=True)
        best_paragraph = scored[0][1]
        return best_paragraph

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
            try:
                text_content = extract_text_from_image(uploaded_file)
            except RuntimeError as exc:
                return Response({'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            if not text_content.strip():
                text_content = '[Image uploaded without text extraction]'
        else:
            return Response({'message': 'Unsupported file type. Upload a PDF, text file, or image.'}, status=status.HTTP_400_BAD_REQUEST)
    elif document_text:
        text_content = document_text
    else:
        return Response({'message': 'No file or text provided for upload.'}, status=status.HTTP_400_BAD_REQUEST)

    if not title:
        title = uploaded_file.name if uploaded_file else 'Untitled Document'

    pdf_document = PDFDocument.objects.create(title=title, embedding=text_content)

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

        answer = answer_question_from_text(pdf_document.embedding, question)
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
