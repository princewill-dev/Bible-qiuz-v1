from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import openai


def ChatPage(request):
    return render(request, 'promptapi/chat.html')



@csrf_exempt
def prompt(request):
    if request.method == 'POST':
        client = OpenAI()
        
        # Create a thread
        thread = client.beta.threads.create()
        
        # Add a message to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=request.POST.get('message', '')
        )
        
        try:
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id="asst_lD18wPA62dVLHYSbUscX8KAD",
                model="gpt-4-turbo-2024-04-09",
                tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
                instructions="""you are a helpful bible quiz expert, with an extend knowledge of the KJV Bible, you will answer questions about the Bible from the attached storage"""
            )
        except Exception as e:
            return render(request, 'promptapi/chat.html', {
                'error': f"Error: {e}",
                'message': request.POST.get('message', '')
            })
        
        # Wait for the run to complete
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run.status == "failed":
                return render(request, 'promptapi/chat.html', {
                    'error': 'Assistant run failed',
                    'message': request.POST.get('message', '')
                })
        
        # Get the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_response = messages.data[0].content[0].text.value
        
        return render(request, 'promptapi/chat.html', {
            'response': assistant_response,
            'message': request.POST.get('message', '')
        })
    
    # If GET request, just show the empty form
    return render(request, 'promptapi/prompt.html')