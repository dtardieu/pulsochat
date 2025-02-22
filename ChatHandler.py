import openai
from nltk.tokenize import sent_tokenize
import json

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
        self.client = openai.OpenAI(api_key=self.api_key)
        self.state=0

    def get_initial_chatbot_value(self):
        """Returns the initial value for the chatbot (first question)."""
        return self.question_list[0]

    def get_current_state(self):
        return self.state

    def reset(self):
        self.current_prompt_index = 0
        self.nb_interactions = 0
        #self.state=0
        #TODO reset history ????
        #TODO shut up !

    def response(self, message, history=[], stream=False):
        """Generates a response based on the message and conversation history."""
        if len(history) + 1 <= 2:
            self.nb_interactions = 0
            self.current_prompt_index = 0
            self.state = 0

        if len(history) + 1 < 2 * len(self.question_list):
            self.state += 1
            response = self.question_list[(len(history) + 1) // 2]
            self.logger.log_interaction(message, response)
            yield response
        else:
            if self.nb_interactions >= self.prompt_list[self.current_prompt_index]["interactions"]:
                self.current_prompt_index = min(self.current_prompt_index + 1, len(self.prompt_list) - 1)
                self.nb_interactions = 0

            self.state += 1
            promptfull = self.meta_prompt + self.prompt_list[self.current_prompt_index]["prompt"]
            messages = [{"role": "system", "content": promptfull}] + history + [{"role": "user", "content": message}]

            #print("chat_handler")
            #print(json.dumps(messages, indent=4))

            #stream = False
            response_obj = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=stream
            )
            
            if stream:
                generated_text, printable_text = "", ""
                for chunk in response_obj:
                    new_text = chunk.choices[0].delta.content or ""
                    generated_text += new_text
                    printable_text += new_text
                    sentences = sent_tokenize(printable_text)
                    if len(sentences) > 1:
                        yield sentences[0]
                        printable_text = new_text
                yield printable_text  # Return last part
            else:
                response = response_obj.choices[0].message.content
                self.logger.log_interaction(message, response)
                return response
            
            #TODO log quand on stream ???
            self.nb_interactions += 1
