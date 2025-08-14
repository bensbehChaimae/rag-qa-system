# import cohere

# def test_cohere_embedding(api_key: str, text: str):
#     try:
#         co = cohere.Client(api_key)
#         response = co.embed(texts=[text])
#         vectors = response.embeddings

#         if vectors and len(vectors) > 0:
#             print(f"Embedding vector length: {len(vectors[0])}")
#             print(f"Sample vector values: {vectors[0][:5]}")  # print first 5 values
#         else:
#             print("No embeddings returned")

#     except Exception as e:
#         print(f"Error while embedding text: {e}")

# if __name__ == "__main__":
#     YOUR_API_KEY = ""  # Replace with your actual API key
#     TEST_TEXT = "What is AWS"
#     test_cohere_embedding(YOUR_API_KEY, TEST_TEXT)
