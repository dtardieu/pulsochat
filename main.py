from ConfigManager import ConfigManager
from InteractionLogger import InteractionLogger
from ChatHandler import ChatHandler
import os

CONFIG_DIR = '.'
DATA_DIR = '.'


def main():
    # Load configuration
    config_manager = ConfigManager(CONFIG_DIR)
    config = config_manager.load_config('config1.json')

    # Set up API key
    api_key = os.getenv('OPENAI_KEY')
    if not api_key:
        raise EnvironmentError("OPENAI_KEY environment variable not set.")

    # Initialize logger
    logger = InteractionLogger(DATA_DIR)

    # Initialize chat handler
    chat_handler = ChatHandler(config, api_key, logger)

    print(chat_handler.get_initial_chatbot_value())
    print(chat_handler.response("Hello", [("", ""), ("",""), ("",""),("", ""), ("",""), ("",""), ("", ""), ("",""), ("","")]))

if __name__ == "__main__":
    main()
