from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAI
from environs import Env

env = Env()
env.read_env()


def build_chain():
    """Tworzy i zwraca łańcuch LangChain do streszczania i tagowania"""
    print("sumerrize and tag")

    llm = ChatOpenAI(
        openai_api_base=env.str("OPENAI_API_BASE"),   # <- to jest kluczowe
        openai_api_key=env.str("OPENAI_API_KEY"),           # <- klucz z OpenRouter
        model_name="openai/gpt-4.1",                 # <- model OpenRoutera
    )
   

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Jesteś pomocnym asystentem, który streszcza wypowiedzi i tworzy trafne tagi."),
        ("human", """Na podstawie poniższego tekstu:

        {input}

        Zwróć JSON z dwoma kluczami:
        - "summary": jednozdaniowe podsumowanie treści,
        - "tags": lista 5 słów kluczowych lub fraz.""")
        ])


    parser = JsonOutputParser()
    

    return RunnablePassthrough() | prompt | llm | parser

def summarize_and_tag(text: str) -> dict:
    """Zwraca streszczenie i 5 tagów jako słownik"""
    
    chain = build_chain()
    return chain.invoke({"input": text})




