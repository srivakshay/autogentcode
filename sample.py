import os
import asyncio
import base64
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# 1. Configuration for Azure OpenAI (via ADK's model interface)
# ADK can interface with Azure models by setting the model string 
# to "azure/<deployment-name>" when using compatible backends.
AZURE_MODEL = f"azure/{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}"

# 2. Define the Agent
image_analyzer = LlmAgent(
    name="ImageAnalyzer",
    model=AZURE_MODEL,
    instruction="""
    You are an expert visual analyst. 
    Your task is to examine the provided image and describe its contents clearly.
    Focus on objects, colors, context, and any visible text. 
    Provide a concise summary of what the image is about.
    """
)

def encode_image_to_base64(image_path):
    """Helper to convert local image to base64 for ADK parts."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

### 2. Main Test Function

async def main():
    # Setup Runner
    runner = InMemoryRunner(agent=image_analyzer)
    
    # Path to your test image
    image_path = "sample_image.jpg" 
    
    if not os.path.exists(image_path):
        print(f"Please provide a valid image path. {image_path} not found.")
        return

    # Convert image to a Part object
    image_base64 = encode_image_to_base64(image_path)
    
    # Construct the multimodal message
    user_message = types.Content(
        role="user",
        parts=[
            types.Part(text="What is in this image?"),
            types.Part(
                inline_data=types.Blob(
                    data=image_base64,
                    mime_type="image/jpeg"
                )
            )
        ]
    )

    print("--- Analyzing Image ---")
    
    # Run the agent
    # Note: Replace 'user_123' and 'session_456' with your logic if needed
    events = runner.run(
        user_id="test_user",
        session_id="test_session",
        new_message=user_message
    )

    # Process and print the stream of events
    for event in events:
        if event.is_final_response():
            print("\nAnalysis Result:")
            print(event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
