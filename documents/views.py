from django.shortcuts import render, redirect,get_object_or_404
from .forms import DocumentForm
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



def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()

            file_path = doc.file.path
            ext = os.path.splitext(file_path)[1].lower()

            extracted_text = ""

            try:
                # 🖼️ Image types
                if ext in ['.jpg', '.jpeg', '.png']:
                    extracted_text = extract_text(file_path)

                # 📄 PDF (try text, fallback to OCR)
                elif ext == '.pdf':
                    try:
                        extracted_text = extract_pdf_text(file_path)
                        if not extracted_text.strip():
                            raise ValueError("Empty PDF text, fallback to OCR")
                    except:
                        extracted_text = extract_scanned_pdf_text(file_path)

                # 📃 Word (.docx)
                elif ext == '.docx':
                    extracted_text = extract_docx_text(file_path)

                # 📊 Excel
                elif ext in ['.xls', '.xlsx']:
                    extracted_text = extract_excel_text(file_path)

                # 📽️ PowerPoint
                elif ext in ['.ppt', '.pptx']:
                    extracted_text = extract_pptx_text(file_path)

                else:
                    extracted_text = "Unsupported file type."

                # 🤖 Summarize
                summary = generate_summary(extracted_text)

                # Save to model
                doc.extracted_text = extracted_text
                doc.summary = summary
                doc.save()

            except Exception as e:
                doc.extracted_text = f"Extraction failed: {str(e)}"
                doc.summary = "Summary generation skipped due to error."
                doc.save()

            return redirect('document_list')

    else:
        form = DocumentForm()

    return render(request, 'documents/upload.html', {'form': form})


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


def document_list(request):
    documents = Document.objects.all().order_by('-uploaded_at')  # 👈 Removed user filter
    return render(request, 'documents/list.html', {'documents': documents})


def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    return render(request, 'documents/detail.html', {'document': document})