import os
import json
from dotenv import load_dotenv
import streamlit as st

from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.agents import AgentType, initialize_agent, Tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

def read_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    
    return config

def use_rag_tool(query: str) -> str:
    return rag_qa.run(query)


def use_serp_tool(query: str) -> str:
    serp_api_wrapper = SerpAPIWrapper(serpapi_api_key=os.getenv("SERP_API_KEY"))
    return serp_api_wrapper.run(query)

if __name__ == "__main__":
    load_dotenv()
    config = read_config()
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620", 
        anthropic_api_key=ANTHROPIC_API_KEY, 
        temperature=0.0)

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

    tools = [
        Tool(
            name="RAGTool",
            description=f"Use this tool to answer questions using the authoritative documents in the vector store about {config['topic']}. This is the primary tool you should use.",
            func=use_rag_tool
        ),
        Tool(
            name="WebSearchTool",
            description=f"Use this tool to search the web for additional information about {config['topic']}, or if the question is outside the scope of the RAG tool",  
            func=use_serp_tool
        )
    ]

    SYSTEM_PROMPT = f"""
    You are an AI assistant with specialized knowledge of the following topics:
    {config["topic"]}.

    - If the user's question is relevant to these topics, call the RAGTool.
    - If the question is outside these topics, or if you need additional external info,
    call the WebSearchTool.
    - In most cases, you should use both tools, and weigh relevance of each tool's response.
    - If the RAGTool provides a relevant answer, you should consider its response to be authoritative.
    - Provide accurate answers, preferring concise answers unless the user asks for more detail.
    - provide your response in markdown format.
    """
    
    print(SYSTEM_PROMPT)

    agent_chain = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
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
        
    for message in st.session_state["messages"]:
        role, content = list(message.items())[0]  # Extract the first key-value pair
        if role == "User":
            st.markdown(f"**You:** {content}")
        else:
            st.markdown(f"**Agent:** {content}")