import os
import json
from dotenv import load_dotenv
import streamlit as st
import config

from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.agents import AgentType, initialize_agent, Tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

load_dotenv()
config = config.read_config()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
persist_directory = os.path.join(config["chroma_base_dir"], config["chroma_collection"])

# Initialize the LLM
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620", 
    anthropic_api_key=ANTHROPIC_API_KEY, 
    temperature=0.0)

# Initialize the embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Initialize the vector store
vector_store = Chroma(
    collection_name=config["chroma_collection"],
    embedding_function=embeddings,
    persist_directory=persist_directory
)

# Initialize the RAG QA chain
rag_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever()
)

# Initialize the SerpAPIWrapper for web search
serp_api_wrapper = SerpAPIWrapper(serpapi_api_key=os.getenv("SERP_API_KEY"))

# Define the RAG tool function
def use_rag_tool(query: str) -> str:
    return rag_qa.run(query)

# Define the web search tool function   
def use_serp_tool(query: str) -> str:
    return serp_api_wrapper.run(query)

if __name__ == "__main__":
    # Define the tools
    print(config["topic_name"])
    print(config["topic_scope"])
    tools = [
        Tool(
            name="RAGTool",
            description=f"Use this tool to answer questions using the authoritative documents in the vector store about {config['topic_name']}. This is the primary tool you should use.",
            func=use_rag_tool
        ),
        Tool(
            name="WebSearchTool",
            description=f"Use this tool to search the web for additional information about {config['topic_name']}, or if the question is outside the scope of the RAG tool",  
            func=use_serp_tool
        )
    ]

    # Define the system prompt
    SYSTEM_PROMPT = f"""
        You are an AI assistant with specialized knowledge of the following topics:
        {config["topic_name"]}.

        - Call the RAGTool if the user's question is within the scope as defined by: {config["topic_scope"]}.
        - If the question is outside the topic and scope defined above, or if you need additional external information, call the WebSearchTool.
        - In most cases, you should use both tools, and weigh relevance of each tool's response.
        - If the RAGTool provides a relevant answer with sufficient detail and confidence, you should consider its response to be authoritative.
        - Provide accurate answers, preferring concise answers unless the user asks for more detail.
        - Provide your response in markdown format.
    """
    
    print(SYSTEM_PROMPT)

    # Initialize the agent
    agent_executor = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        system_message=SYSTEM_PROMPT
    )

    # Initialize the Streamlit app
    st.title("Anthropic Claude Q&A Agent (RAG + Web Search)")

    # Initialize the session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        
    # Get the user's input
    user_input = st.text_input("Ask a question:")

    # Send the user's input to the agent and get the response, add both to the session state
    if st.button("Send") and user_input.strip():
        st.session_state["messages"].append({"User": user_input})
        response = agent_executor.invoke({"input": user_input})
        st.session_state["messages"].append({"Agent": response})
        
    # Redraw the UI with all the messages in the session state
    for message in st.session_state["messages"]:
        # make a list from the keys dictionary view object and extract the first (only) element
        role = list(message.keys())[0]
        # make a list from the values dictionary view object and extract the first (only) element
        content = list(message.values())[0]
        if role == "User":
            st.markdown(f"**You:** {content}")
        else:
            st.markdown(f"**Agent:** {content}")