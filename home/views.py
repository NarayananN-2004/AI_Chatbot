from django.shortcuts import render
from django.http import HttpResponse

from django.contrib import messages
from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from django.conf import settings
from django.utils.safestring import mark_safe
from google import genai
from google.genai import errors
import markdown

from django.contrib.auth import authenticate, login as auth_login ,logout

from django.contrib.auth.decorators import login_required

def home(request):
    #return HttpResponse("Hello, welcome to the home page!")
    return render(request, 'home.html')
    
# def register(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email_address = request.POST.get('email_address')
#         password = request.POST.get('password')

#         if Logininfo.objects.filter(email_address=email_address).exists():
#             messages.error(request, "An account with this email/username already exists.")
#             return render(request, 'register.html')  # back to the form

#         Logininfo.objects.create(
#             email_address=email_address,
#             password=password,
#             username=username
#         )
#         return redirect('login')  # or wherever you send new users
#     return render(request, 'register.html')
   

# def login(request):
#     if request.method == 'POST':
#         email_address = request.POST.get('email_address')
#         password = request.POST.get('password')
#         if email_address=="NARAYANAN@gmail.com"and password=="14112004":
#             return redirect('/admin/')
#         else:
#                 try:
#                     user = Logininfo.objects.get(email_address=email_address)
#                 except Logininfo.DoesNotExist:
#                     messages.error(request, "No account found with that email/password.")
#                     return render(request, 'login.html')

#                 if user.password == password:
#                     request.session['user_id'] = user.id  # simple session-based "login"
#                     return redirect('/chat/')  # wherever you send logged-in users
#                 else:
#                     messages.error(request, "Incorrect password/email.")
#                     return render(request, 'login.html')

#     return render(request, 'login.html')
def logout_page(request):
    logout(request)
    return redirect("/login/")

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect('/login/')

        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/chat/')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('/login/')

    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email_address = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email_address).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('/register/')  # back to the form
        else:
            user = User.objects.create(
                username=username,
                email=email_address)
            user.set_password(password)
            user.save()
            return redirect('login')  # or wherever you send new users
    return render(request, 'register.html')
        

import time
from django.conf import settings
from google import genai
from google.genai import errors
@login_required(login_url='/login/')
def ask_gemini(request):
    ai_output = None
    user_question = ""
    if request.method == "POST":
        user_question = request.POST.get("question", "")

        if user_question:
            client = genai.Client(api_key=settings.GOOGLE_AI_API_KEY)
            max_retries = 3
            raw_output = None

            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model="gemma-4-26b-a4b-it",  # gemini-3.5-flash",
                        contents=user_question,
                    )
                    raw_output = response.text
                    break  # success, stop retrying

                except errors.ServerError as e:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raw_output = "The AI is a bit overloaded right now. Please try again in a moment."

                except errors.ClientError as e:
                    raw_output = f"Request error: {e.message}"
                    break

                except Exception as e:
                    raw_output = f"An unexpected error occurred: {str(e)}"
                    break

            # Convert Gemini's Markdown into safe HTML for the template
            ai_output = mark_safe(
                markdown.markdown(raw_output, extensions=["fenced_code", "tables"])
            )

    return render(request, "chat.html", {
        "question": user_question,
        "output": ai_output
    })



















# def ask_gemini(request):
#     ai_output = None
#     user_question = ""

#     if request.method == "POST":
#         user_question = request.POST.get("question", "")

#         if user_question:
#             client = genai.Client(api_key=settings.GOOGLE_AI_API_KEY)
#             max_retries = 3

#             for attempt in range(max_retries):
#                 try:
#                     response = client.models.generate_content(
#                         model="gemma-4-26b-a4b-it",#gemini-3.5-flash",
#                         contents=user_question,
#                     )
#                     ai_output = response.text
#                     break  # success, stop retrying

#                 except errors.ServerError as e:
#                     # 5xx errors (503 overloaded, 500, etc.) — worth retrying
#                     if attempt < max_retries - 1:
#                         time.sleep(2 ** attempt)  # 1s, then 2s
#                         continue
#                     ai_output = "The AI is a bit overloaded right now. Please try again in a moment."

#                 except errors.ClientError as e:
#                     # 4xx errors (bad key, bad request, quota) — retrying won't help
#                     ai_output = f"Request error: {e.message}"
#                     break

#                 except Exception as e:
#                     # anything unexpected
#                     ai_output = f"An unexpected error occurred: {str(e)}"
#                     break

#     return render(request, "chat.html", {
#         "question": user_question,
#         "output": ai_output
#     })


# from django.conf import settings
# from google import genai

# def ask_gemini(request):
#     ai_output = None
#     user_question = ""

#     if request.method == "POST":
#         # Get the question from the HTML form
#         user_question = request.POST.get("question", "")
        
#         if user_question:
#             try:
#                 # Initialize client using the key from settings.py
#                 client = genai.Client(api_key=settings.GOOGLE_AI_API_KEY)
                
#                 # Generate content using the recommended model
#                 response = client.models.generate_content(
#                     model="gemini-3.5-flash",
#                     contents=user_question,
#                 )
                
#                 # Extract the text output
#                 ai_output = response.text
                
#             except Exception as e:
#                 ai_output = f"An error occurred: {str(e)}"

#     return render(request, "chat.html", {
#         "question": user_question,
#         "output": ai_output
#     })
# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.apps import apps

# @csrf_exempt
# def jarvis_chat(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_text = data.get("message", "")

#         engine = apps.get_app_config("home").engine
#         reply = engine.respond(user_text)

#         return JsonResponse({"response": reply})

#     return render(request, "jarvis.html")




import json
from django.shortcuts import render
from django.apps import apps

def jarvis_chat(request):
    question = ""
    output = None

    if request.method == "POST":
        question = request.POST.get("question", "")
        engine = apps.get_app_config("home").engine
        username = request.user.username if request.user.is_authenticated else "there"
        output = engine.respond(question, username=username)

    return render(request, "jarvis.html", {
        "question": question,
        "output": output,
    })