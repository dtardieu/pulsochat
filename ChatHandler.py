from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate


class ChatHandler:
    """Manages the chat interactions and responses."""

    def __init__(self, config, api_key, logger):
        self.config = config
        self.api_key = api_key
        self.logger = logger
        self.model_name = config["model_name"]
        self.prompt_list = config["prompt_list"]
        self.question_list = config["question_list"]
        self.meta_prompt = config["meta_prompt"]
        self.current_prompt_index = 0
        self.nb_interactions = 0

        self.chat = ChatOpenAI(model=self.model_name, openai_api_key=self.api_key)

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template("{prompt}"),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        self.chain = self.prompt_template | self.chat

    def get_initial_chatbot_value(self):
        """Returns the initial value for the chatbot (first question)."""
        return self.question_list[0]

    def response(self, message, history=[]):
        """Generates a response based on the message and conversation history."""
        # Reset counters for a new session

        if len(history)+1 <= 2:
            self.nb_interactions = 0
            self.current_prompt_index = 0

        # Determine if we should use a predefined question or generate a response
        if len(history)+1 < 2*len(self.question_list):
            print(f"history lenght: {len(history)}")
            print(history)
            print(f"question: {self.question_list[(len(history)+1)//2]}")
            response = self.question_list[(len(history)+1)//2]
        else:
            # Update prompt index based on interactions
            if self.nb_interactions >= self.prompt_list[self.current_prompt_index]["interactions"]:
                self.current_prompt_index = min(self.current_prompt_index + 1, len(self.prompt_list) - 1)
                self.nb_interactions = 0

            # Generate AI response
            promptfull = self.meta_prompt + self.prompt_list[self.current_prompt_index]["prompt"]

            print(history+[{"role": "user", "content": message}])

            response_obj = self.chain.invoke({
                "prompt": promptfull,
                "messages": history+[{"role": "user", "content": message}]
            })
            response = response_obj.content.replace('text', 'vision').replace('Text', 'Vision')
            self.nb_interactions += 1

        # Log and return the response
        self.logger.log_interaction(message, response)
        return response
