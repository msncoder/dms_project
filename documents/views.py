from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import DocumentForm,CustomUserCreationForm
from django.contrib import messages
from .ocr_utils import (
    extract_text,
    extract_pdf_text,
    extract_scanned_pdf_text,
    extract_docx_text,
    extract_excel_text,
    extract_pptx_text,
)
from .ai_summarizer import generate_summary
import os
from PIL import Image
import pytesseract
from .models import Document
from django.http import JsonResponse
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .tasks import process_document




# Authentication starts

def is_admin(user):
    return user.is_authenticated and user.role in ['admin','superadmin']

def is_editor(user):
    return user.is_authenticated and user.role == 'editor'

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('document_list')
        
    else:
        form = CustomUserCreationForm()
    return render(request,'accounts/register.html',{'form':form})



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('document_list')
        else:
            messages.error(request,'Invalid Credentials')

    return render(request,'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

# authentication ends 
    

@login_required
def document_list(request):
    if request.user.role == 'editor':
        documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')  
    else:
        documents = Document.objects.all().order_by('-uploaded_at')  # 👈 Removed user filter
    return render(request, 'documents/list.html', {'documents': documents})

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.user == document.user or is_admin(request.user):
        return render(request, 'documents/detail.html', {'document': document})
    return redirect('document_list')

@login_required
def delete_document(request, pk):
    print("delete")
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        if request.user == document.user or is_admin(request.user):
            print("Deleting:", document.title)
            document.delete()
            return redirect('document_list')
        else:
            print("No permission to delete.")
    return redirect('document_detail', pk=pk)


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()

            # 📦 Call Celery task
            process_document.delay(doc.id, doc.file.path)

            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'documents/upload.html', {'form': form})


# @login_required
# def upload_document(request):
#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             doc = form.save(commit=False)
#             doc.user = request.user
#             doc.save()

#             file_path = doc.file.path
#             ext = os.path.splitext(file_path)[1].lower()

#             extracted_text = ""

#             try:
#                 # 🖼️ Image types
#                 if ext in ['.jpg', '.jpeg', '.png']:
#                     extracted_text = extract_text(file_path)

#                 # 📄 PDF (try text, fallback to OCR)
#                 elif ext == '.pdf':
#                     try:
#                         extracted_text = extract_pdf_text(file_path)
#                         if not extracted_text.strip():
#                             raise ValueError("Empty PDF text, fallback to OCR")
#                     except:
#                         extracted_text = extract_scanned_pdf_text(file_path)

#                 # 📃 Word (.docx)
#                 elif ext == '.docx':
#                     extracted_text = extract_docx_text(file_path)

#                 # 📊 Excel
#                 elif ext in ['.xls', '.xlsx']:
#                     extracted_text = extract_excel_text(file_path)

#                 # 📽️ PowerPoint
#                 elif ext in ['.ppt', '.pptx']:
#                     extracted_text = extract_pptx_text(file_path)

#                 else:
#                     extracted_text = "Unsupported file type."

#                 # 🤖 Summarize
#                 summary = generate_summary(extracted_text)

#                 # Save to model
#                 doc.extracted_text = extracted_text
#                 doc.summary = summary
#                 doc.save()

#             except Exception as e:
#                 doc.extracted_text = f"Extraction failed: {str(e)}"
#                 doc.summary = "Summary generation skipped due to error."
#                 doc.save()

#             return redirect('document_list')

#     else:
#         form = DocumentForm()

#     return render(request, 'documents/upload.html', {'form': form})


# def ajax_search_documents(request):
#     query = request.GET.get('q', '')
#     if query:
#         vector = SearchVector('title', 'summary', 'category')
#         search_query = SearchQuery(query)
#         docs = Document.objects.annotate(
#             rank=SearchRank(vector, search_query)
#         ).filter(rank__gte=0.1).order_by('-rank')
#     else:
#         docs = Document.objects.all().order_by('-uploaded_at')

#     results = []
#     for doc in docs:
#         results.append({
#             'user': doc.user.username,
#             'title': doc.title,
#             'category': doc.category,
#             'summary': doc.summary[:80],
#             'file_url': doc.file.url,
#             'uploaded_at': doc.uploaded_at.strftime("%d %b %Y %H:%M"),
#         })

#     return JsonResponse({'documents': results})

