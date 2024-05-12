from config import OPENAI_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_KEY)


def test_openai_connection(message):
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": message}])
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    print("OpenAI Chatbot. Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting chat...")
            break
        response = test_openai_connection(user_input)
        print(f"AI: {response}")

if __name__ == "__main__":
    main()

