from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('list/', views.document_list, name='document_list'),  # ✅ Add this
    # path('ajax-search/', views.ajax_search_documents, name='ajax_search_documents'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('document/<int:pk>/', views.delete_document, name='delete_document'),
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
]