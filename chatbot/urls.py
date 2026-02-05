from django.urls import path
from django.shortcuts import render
from .views import menstrual_chatbot

urlpatterns = [
    # page that shows chat UI
    path("chat/", lambda request: render(request, "chat.html"), name="chat"),

    # API endpoint for chatbot
    path("ask/", menstrual_chatbot, name="menstrual_chatbot"),
]
