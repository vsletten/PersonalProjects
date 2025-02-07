import os
import json
from dotenv import load_dotenv
import streamlit as st

from langchain_anthropic import AnthropicLLM
from langchain.embeddings import OpenAIEmbeddings
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.utilities import SerpAPIWrapper
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

def read_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    
    return config

load_dotenv()
config = read_config()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

llm = AnthropicLLM(model="claude-3-5-sonnet-20240620", anthropic_api_key=ANTHROPIC_API_KEY, temperature=0.0)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

persist_directory = os.path.join(config["chroma_base_dir"], config["chroma_collection"])
vector_store = Chroma(
    collection_name=config["chroma_collection"],
    embedding_function=embeddings,
    persist_directory=persist_directory
)

rag_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever()
)

def use_rag_tool(query: str) -> str:
    return rag_qa.run(query)

serp_api_wrapper = SerpAPIWrapper(serp_api_key=SERP_API_KEY)

def use_serp_tool(query: str) -> str:
    return serp_api_wrapper.run(query)

tools = [
    Tool(
        name="RAG",
        description="Use this tool to answer questions about the documents in the vector store",
        func=use_rag_tool
    ),
    Tool(
        name="SerpAPI",
        description="Use this tool to search the web for information",  
        func=use_serp_tool
    )
]

SYSTEM_PROMPT = f"""
You are an AI assistant with specialized knowledge of the following topics:
{config["topic"]}.

- If the user's question is relevant to these topics, call the RAGTool.
- If the question is outside these topics, or if you need additional external info,
  call the WebSearchTool.
- Provide concise, accurate answers.
"""

agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    system_message=SYSTEM_PROMPT
)

st.title("Anthropic Claude Q&A Agent (RAG + Web Search)")

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    
user_input = st.text_input("Ask a question:")

if st.button("Send") and user_input.strip():
    st.session_state["messages"].append({"User": user_input})
    response = agent_chain.run(user_input)
    st.session_state["messages"].append({"Agent": response})
    
for role, content in st.session_state["messages"]:
    if role == "User":
        st.markdown(f"**You:** {content}")
    else:
        st.markdown(f"**Agent:** {content}")