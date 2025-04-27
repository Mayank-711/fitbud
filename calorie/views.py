from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.


def home(request):

    return render(request,'home.html')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai
import environ

# Load environment variables
env = environ.Env()
environ.Env.read_env()

# Get the Gemini API key securely
GEMINI_API_KEY = env('GEMINI_API')

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

@csrf_exempt
def analyze_meal(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            query = body.get('query', '').strip()

            if not query:
                return JsonResponse({'error': 'No food items provided'}, status=400)

            # Create Gemini model instance
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Build the prompt
            prompt = f"""
You are a nutrition expert.
Analyze the following meal: {query}
Return the output strictly in JSON with this format:
{{
    "items": [
        {{
            "item_name": "",
            "quantity": "",
            "calories": 0,
            "protein_grams": 0,
            "carbohydrates_grams": 0,
            "fat_grams": 0
        }}
    ],
    "totals": {{
        "total_calories": 0,
        "total_protein_grams": 0,
        "total_carbohydrates_grams": 0,
        "total_fat_grams": 0
    }},
    "disclaimer": "Nutritional values are estimates. Actual values depend on preparation methods and ingredients."
}}
Important: Reply ONLY the JSON. No text, no explanation.
"""

            # Call Gemini
            response = model.generate_content(prompt)

            gemini_response = response.text

            # Clean if necessary
            try:
                parsed_response = json.loads(gemini_response)
            except json.JSONDecodeError:
                gemini_response = gemini_response.replace('```json', '').replace('```', '').strip()
                parsed_response = json.loads(gemini_response)
            print(parsed_response)
            return JsonResponse(parsed_response, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)