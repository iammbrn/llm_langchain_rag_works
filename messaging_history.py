from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser 
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

model = ChatOllama(model = "mistral", temperature = 0.1)

parser = StrOutputParser()


store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:

    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Answer all questions to the best of your ability."),
        MessagesPlaceholder(variable_name = "messageses")
    ]
)



chain = prompt | model | parser

config = {"configurable": {"session_id": "user1234"}}

with_message_history = RunnableWithMessageHistory(chain, get_session_history)


if __name__ == "__main__":

    while True:

        user_input = input(">")

        if user_input.lower() == "exit":
            break
        
        else:
            """response = with_message_history.invoke(
                [
                    HumanMessage(content = user_input)
                ],
                config = config
            )

            print(response)"""


            for response in with_message_history.stream(
                [
                    HumanMessage(content = user_input)
                ],
                config = config
            ):
                print(response, end = " ")