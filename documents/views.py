# documents/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DocumentForm
from .models import Document
from .ocr_utils import extract_text
from .ai_summarizer import generate_summary

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()

            # Run OCR
            extracted_text = extract_text(doc.file.path)
            doc.extracted_text = extracted_text

            # AI Summary
            summary = generate_summary(extracted_text)
            doc.summary = summary

            doc.save()

            return redirect('document_list')  # replace with your success page
    else:
        form = DocumentForm()

    return render(request, 'documents/upload.html', {'form': form})



def document_list(request):
    documents = Document.objects.filter(user=request.user)
    return render(request, 'documents/list.html', {'documents': documents})