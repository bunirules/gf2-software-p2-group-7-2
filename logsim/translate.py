import sys

# import required packages for translation


class Translator:
    def __init__(self, lang="ENG"):
        """Initialise the translate class."""
        self.lang_options = {"English": "ENG", "Espa\xf1ol": "ES"}
        if lang in self.lang_options.values():
            self.lang = lang
        else:
            print(f'\nLanguage ID ("{lang}") invalid. Options are:')
            print(list(self.lang_options.values()))
            sys.exit()

    def get_translation(self, string):
        """Translates the given string to the selected language.

        Arguments:
            string -- string to be translated

        Returns:
            translated string
        """
        # translate string
        return string
