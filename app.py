from genai_api import genai_api

if __name__ == "__main__":
    response = genai_api.call_genai("Explain how AI works in a few words")
    if response:
        print(response)