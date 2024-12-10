from django.shortcuts import render,HttpResponse,redirect
from Hello.models import Contact
from datetime import datetime
from django.contrib import messages

def home(request):
  return render(request,"home.html")

def about(request):
  return render(request,"about.html")

def contactus(request):
  return render(request,"contactus.html")

def app(request):
  return render(request,"app.html")
