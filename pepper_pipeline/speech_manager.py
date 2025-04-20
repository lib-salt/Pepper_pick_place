from utils import logger

class SpeechManager:
    def __init__(self, speech_proxy=None):
        self.speech_proxy = speech_proxy

        # Initialise speech settings
        if self.speech_proxy:
            self.speech_proxy.setLanguage("English")
            logger.info("Speech manager initialised")

    def say(self, text):
        # Make Pepper speak
        if self.speech_proxy:
            try:
                self.speech_proxy.say(text)
                logger.debug("Pepper said: {}".format(text))

            except Exception as e:
                logger.error("Error making Pepper talk: {}".format(e))

    def announce_object(self, category):
        # Announce object detection
        text = "I have found a {}".format(category)
        self.say(text)

    def announce_reaching_object(self, category):
        # Announce when Pepper has reached the object
        text = "I have reached the {}".format(category)
        self.say(text)

    def announce_searching(self):
        # Announce that Pepper is searching
        text = "I am looking for objects"
        self.say(text)

    def announce_error(self, error_type="general"):
        # Announce errors
        error_messages = {
            "position": "I cannot determine the position of the object",
            "movement": "I cannot reach the object",
            "detection": "I cannot detect any objects",
            "general": "I encountered a problem"
        }
        
        text = error_messages.get(error_type, error_messages["general"])
        self.say(text)