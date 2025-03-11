from openai import OpenAI
import streamlit as st
from chat.new_chat_manager import ChatAgent

def main():
  st.title("Training")

  if "chatmgr" not in st.session_state:
        client = ChatAgent()
        client.get_next_message()
        st.session_state["chatmgr"] = client
        

  client = st.session_state.chatmgr
  messages = client.get_messages()
  
  for message in messages:
      if "display" in message and message["display"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

  if client.is_session_finished():
      if st.button("Premier apprentissage"):
          result = messages[-1]["json"]
          st.session_state["user_name"] = result.get("user_name")
          st.switch_page(f"pages/2_Quizz.py")
 
  else:
    if prompt := st.chat_input("What is up?"):
        client.respond_to_user( prompt)
        st.rerun()


if __name__ == "__main__":
    main()


  