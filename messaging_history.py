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

# Her kullanıcıya özel mesaj geçmişi saklamak için boş bir store
store = {}



# Belirli bir session ID'ye ait sohbet geçmişini döner. Yoksa bellekte oluşturur.
def get_session_history(session_id: str) -> BaseChatMessageHistory:

    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]



# Sistem ve kullanıcı mesajları için bir prompt şablonu oluştur
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Answer all questions to the best of your ability."),
        MessagesPlaceholder(variable_name = "messageses") # Mesaj geçmişi buraya eklenecek
    ]
)



chain = prompt | model | parser

# Kullanıcı oturumunu temsil eden bir config nesnesi oluşturulur.
config = {"configurable": {"session_id": "user1234"}}

# Zinciri geçmiş takibi (history) ile sar. 
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

            # Mesajı geçmişle birlikte işleyip model yanıtlarını akış (stream) şeklinde al
            for response in with_message_history.stream(
                [
                    HumanMessage(content = user_input)
                ],
                config = config
            ):
                print(response, end = " ") # Gelen her token’ı anında ekrana bas (stream output)