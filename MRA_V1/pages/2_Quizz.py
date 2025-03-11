import streamlit as st
from backend.user_manager import UserManager
from backend.new_catalog_manager import TrainingManager


def main():
    st.title("Quizz Page")

    # retrieve user name from URL or from session state
    user_name = None
    if "user_name" in st.query_params:
        user_name = st.query_params["user_name"]
    if user_name is None:
        user_name = st.session_state.get("user_name", None)

    if user_name is None:
        st.error("Username not found in URL")
        return
    
    user_manager = UserManager()
    user = user_manager.get_user_by_name(user_name)
    if not user:
        st.error(f"User '{user_name}' not found")
        return

    current_training = user.get_current_training()
    if not current_training:
        st.error("No current training found for the user")
        return
    training_manager = TrainingManager()
    training = training_manager.get_training_by_id(current_training.get_training_id())
    chapters_done = current_training.get_chapters_done()

     # retrieve user name from URL or from session state or take next chapter
    chapterId = None
    next_chapter=None
    if "ch" in st.query_params:
        chapterId = st.query_params["ch"]
    if "ch" in st.session_state:
        chapterId = st.session_state["ch"]
    if not chapterId:
      for chapter in training.get_chapters():
          if chapter.id not in chapters_done:
              chapterId = chapter.id
              st.session_state["ch"] = chapterId
              break

    for chapter in training.get_chapters():
      if chapter.id == chapterId:
          next_chapter = chapter

    if not next_chapter:
        st.success("You have completed all chapters in this training!")
        return

    st.header(f"{next_chapter.subject}")
    st.write(next_chapter.content)
    st.write(next_chapter.question)

    selected_response = st.radio("Select your response:", [answer.text for answer in next_chapter.get_answers()])

    if st.button("Submit"):
        success = False
        for answer in next_chapter.get_answers():
            if answer.text == selected_response:
                if answer.valid:
                    st.success("Correct answer!")
                    success = True
                else:
                    st.error("Incorrect answer.")
                break
        user_manager.set_chapter_finished(user.id, next_chapter.id, success)
        st.button("Essayer une autre question", on_click=lambda: st.switch_page(f"pages/2_Quizz.py"))

if __name__ == "__main__":
    main()
