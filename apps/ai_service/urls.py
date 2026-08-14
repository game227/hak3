from django.urls import path
from . import views

app_name = 'ai_service'

urlpatterns = [
    path('', views.ai_assistant_view, name='ai_assistant_root'),
    path('assistant/', views.ai_assistant_view, name='ai_assistant'),
    path('matchmaker/', views.ai_assistant_view, name='ai_matchmaker'),
    path('api/chat/', views.ai_chat_api, name='ai_chat_api'),
    path('api/matchmaker/', views.smart_matchmaker_api, name='smart_matchmaker_api'),
]
