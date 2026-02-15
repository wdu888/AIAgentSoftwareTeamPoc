"""
Test script to verify the correct Qwen configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if the API key is loaded correctly
api_key = os.getenv("DASHSCOPE_API_KEY")
print(f"DASHSCOPE_API_KEY loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API key starts with: {api_key[:10]}..." if len(api_key) > 10 else f"API key: {api_key}")

# Test importing and initializing with the correct approach
try:
    from langchain_qwq import ChatQwen
    
    # Test creating a simple instance
    llm = ChatQwen(
        model="qwen-turbo",
        api_key=api_key,
        temperature=0.7
    )
    
    print("[SUCCESS] ChatQwen instance created successfully")
    print(f"[INFO] Model: {llm.model}")
    print(f"[INFO] API key in model: {'Yes' if llm.api_key else 'No'}")
    
except Exception as e:
    print(f"[ERROR] Error creating ChatQwen instance: {e}")
    
    # Try alternative approach if needed
    try:
        # Alternative: Using environment variable directly
        import os
        os.environ["DASHSCOPE_API_KEY"] = api_key or ""
        
        from langchain_qwq import ChatQwen
        llm = ChatQwen(
            model="qwen-turbo",
            temperature=0.7
        )
        
        print("[SUCCESS] Alternative ChatQwen instance created successfully")
        print(f"[INFO] Model: {llm.model}")
        
    except Exception as e2:
        print(f"[ERROR] Alternative approach also failed: {e2}")