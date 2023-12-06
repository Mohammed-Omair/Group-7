import functions_framework
from openai import OpenAI

client = OpenAI(api_key = "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")

@functions_framework.http
def hello_http(request):

    request_args = request.args


    if request_args and 'question' in request_args:
        question = request_args['question']
    else:
        return "question is not present in query params"
    
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a helpful assistant which gives single sentance answer to the questions and designed to output JSON."},
        {"role": "user", "content": f'give single sentance summary/meaning to {question}'}
    ]
    )
    
    return response.choices[0].message.content