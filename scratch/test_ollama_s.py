from langchain_openai import ChatOpenAI
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Test(BaseModel):
    hi: str

try:
    llm = ChatOpenAI(
        model='qwen3-coder:30b', 
        api_key='ollama', 
        base_url='http://localhost:11434/v1',
        temperature=0
    )
    s_llm = llm.with_structured_output(Test, method='json_mode')
    result = s_llm.invoke("Say hi in JSON format like {'hi': 'hello'}")
    print("SUCCESS:", result)
except Exception as e:
    print("FAILED:", e)
