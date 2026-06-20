from google import genai

# The SDK automatically picks up your GEMINI_API_KEY from your environment variables!
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Connection test. Reply with only the words: Grid system online.",
)

print("\n--- API TEST RESULT ---")
print(response.text.strip())
print("-----------------------\n")