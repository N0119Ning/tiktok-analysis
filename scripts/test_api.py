import os

BASE_DIR = 'e:/pycharm_project2/tiktok_project'

env_path = os.path.join(BASE_DIR, '.env')
print(f"Loading .env from: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

api_key = ''
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        content = f.read()
        print(f"File content: {repr(content)}")
        for line in content.splitlines():
            line = line.strip().strip('`')
            print(f"Processing line: {repr(line)}")
            if line.startswith('DEEPSEEK_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                print(f"Found API key: {api_key[:10]}...{api_key[-5:]}")

print(f"Final API key length: {len(api_key)}")

if not api_key:
    print("ERROR: API key not found!")
    exit(1)

try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url='https://api.deepseek.com')
    
    print("\nSending test request to DeepSeek...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, say hi in Chinese"}
        ],
        max_tokens=50
    )
    
    print(f"Response: {response.choices[0].message.content}")
    print("\nAPI Key is working!")
    
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
