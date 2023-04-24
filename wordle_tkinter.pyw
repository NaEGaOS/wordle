import tkinter as tk
import random
import json


class GUI:
    def __init__(self, max_guesses: int = 6) -> None:
        with open(r"game_files\five_letter_words.txt", "r") as word_file:  # get valid words
            self.valid_words = word_file.read().split("\n")
        with open(r"game_files\settings.json", "r") as settings_file:  # get settings
            self.settings = json.load(settings_file)
        with open(r"game_files\colours.json", "r") as colours_file:  # get colours
            self.colours = json.load(colours_file)
        self.root = tk.Tk()
        self.root.title("wordle")
        self.max_guesses = max_guesses
        # binds
        def write_guess(letter: str, add: bool):  # for keyboard input
            if add:
                self.guess += letter.lower() if len(self.guess) < 5 else ""
                i = len(self.guess) - 1
                self.words_reference[(self.current_word, i)].config(text=self.guess[i],
                                                                    fg=self.colours["foreground"][self.colourmode])
            else:
                self.guess = self.guess[:-1]
                self.words_reference[(self.current_word, len(self.guess))].config(text="")

        for letter in "qwertzuiopasdfghjklyxcvbnmQWERTZUIOPASDFGHJKLYXCVBNM":
            self.root.bind(f"<{letter}>", lambda event, letter=letter: write_guess(letter, True))
        self.root.bind("<BackSpace>", lambda event: write_guess("", False))
        self.root.bind("<Return>", lambda event: self.update_words())
        self.root.bind("<Escape>", lambda event: self.reset())
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        # variables
        self.answer = random.choice(self.valid_words)
        print(self.answer)
        self.guess = ""
        self.guessed_words = set()  # because mutable and no duplicates
        self.red_letters = set()
        self.yellow_letters = set()
        self.green_letters = set()
        self.colourmode = self.settings["default colourmode"]
        self.current_word = 0  # keeps track of current row (idk why I called it "word")
        self.root.config(bg=self.colours["background"][self.colourmode])
        # frames
        self.keyboard_frame = tk.Frame(self.root, bg=self.colours["background"][self.colourmode])
        self.word_frame = tk.Frame(self.root, bg=self.colours["background"][self.colourmode])
        # widgets
        self.colourmode_button = tk.Button(self.root, text="colour mode", command=self.update_colours,
                                           bg=self.colours["button background"][self.colourmode],
                                           fg=self.colours["foreground"][self.colourmode])
        self.feedback_label = tk.Label(self.root, text="", bg=self.colours["background"][self.colourmode],
                                       fg=self.colours["foreground"][self.colourmode],
                                       font=(self.settings["font"], self.settings["word font size"]))
        # generate keyboard
        self.keys_reference = {}  # to access generated instances
        keys = (
            ("q", "w", "e", "r", "t", "y", "u", "i", "o", "p"),
            ("a", "s", "d", "f", "g", "h", "j", "k", "l"),
            ("z", "x", "c", "v", "b", "n", "m")
        )
        width, height = self.settings["keyboard size"]
        for i, line in enumerate(keys):
            for j, key in enumerate(line):
                current_label = tk.Label(self.keyboard_frame, text=key, width=width, height=height,
                                         font=(self.settings["font"], self.settings["keyboard font size"]),
                                         bg=self.colours["button background"][self.colourmode],
                                         fg=self.colours["foreground"][self.colourmode])
                current_label.grid(row=i, column=j, padx=1, pady=1)
                self.keys_reference[key] = current_label
        # generate words for frame
        self.words_reference = {}  # to access generated instances
        width, height = self.settings["word size"]
        for i in range(self.max_guesses):
            for j in range(5):
                current_label = tk.Label(self.word_frame, width=width, height=height,
                                         font=(self.settings["font"], self.settings["word font size"]),
                                         bg=self.colours["button background"][self.colourmode])
                current_label.grid(row=i, column=j, padx=1, pady=1)
                self.words_reference[(i, j)] = current_label
    
    def update_keyboard_colour(self) -> None:
        for key in self.keys_reference:  # accessing keyboard keys
            if key in self.red_letters:
                self.keys_reference[key].config(bg=self.colours["red"], fg="black")
            elif key in self.yellow_letters:
                self.keys_reference[key].config(bg=self.colours["yellow"], fg="black")  # yellow
            elif key in self.green_letters:
                self.keys_reference[key].config(bg=self.colours["green"], fg="black")
            else:  # default colour
                self.keys_reference[key].config(bg=self.colours["button background"][self.colourmode],
                                                fg=self.colours["foreground"][self.colourmode])

    def update_colours(self) -> None:
        self.colourmode = 1 if self.colourmode == 0 else 0  # toggle
        self.root.config(bg=self.colours["background"][self.colourmode])
        self.update_keyboard_colour()  # to not overwrite red/yellow/green
        for key in self.words_reference:
            if self.words_reference[key].cget("bg") not in (self.colours["red"], self.colours["yellow"], self.colours["green"]):
                self.words_reference[key].config(bg=self.colours["button background"][self.colourmode],
                                                 fg=self.colours["foreground"][self.colourmode])
        self.colourmode_button.config(bg=self.colours["button background"][self.colourmode],
                                      fg=self.colours["foreground"][self.colourmode])
        for frame in (self.keyboard_frame, self.word_frame):
            frame.config(bg=self.colours["background"][self.colourmode])
        self.feedback_label.config(bg=self.colours["background"][self.colourmode],
                                   fg=self.colours["foreground"][self.colourmode])
    
    def update_words(self) -> None:
        
        def all_green(letter) -> bool:
            # return true if all letters in self.guess and self.answer are in the same position
            for i in range(len(self.guess)):
                if self.guess[i] == letter and self.answer[i] != letter:
                    return False
                elif self.answer[i] == letter and self.guess[i] != letter:
                    return False
            return True
        
        def any_green(letter) -> bool:
            # return true if any letters in self.guess and self.answer are in the same position
            for i in range(len(self.guess)):
                if self.guess[i] == letter and self.answer[i] == letter:
                    return True
            return False
        # check if valid guess
        if len(self.guess) != 5:
            self.feedback_label.config(text="word must be 5 letters long")
            return
        elif self.guess not in self.valid_words:
            self.feedback_label.config(text="word not found")
            return
        elif self.guess in self.guessed_words:
            self.feedback_label.config(text="word already guessed")
            return
        # valid guess
        self.feedback_label.config(text="")
        self.guessed_words.add(self.guess)
        for i, letter in enumerate(self.guess):
            # edits word frame
            self.words_reference[(self.current_word, i)].config(text=letter)
            # apply colour to words based on letters
            if all_green(letter):
                self.green_letters.add(letter)
                self.yellow_letters.discard(letter)
                self.words_reference[(self.current_word, i)].config(bg=self.colours["green"], fg="black")
            elif any_green(letter):  # won't trigger if all_green
                # check if this letter is green
                self.yellow_letters.add(letter) if letter not in self.green_letters else None
                if letter == self.answer[i]:
                    self.words_reference[(self.current_word, i)].config(bg=self.colours["green"], fg="black")
                else:
                    if self.guess.count(letter) > self.answer.count(letter):
                        self.words_reference[(self.current_word, i)].config(bg=self.colours["red"], fg="black")
                    else:
                        self.words_reference[(self.current_word, i)].config(bg=self.colours["yellow"], fg="black")  # yellow
            elif self.guess.count(letter) > self.answer.count(letter):
                if self.guess[:i+1].count(letter) == self.answer.count(letter):
                    self.yellow_letters.add(letter) if letter not in self.green_letters else None
                    self.words_reference[(self.current_word, i)].config(bg=self.colours["yellow"], fg="black")
                else:
                    self.red_letters.add(letter)
                    self.words_reference[(self.current_word, i)].config(bg=self.colours["red"], fg="black")
            elif letter in self.answer and letter != self.answer[i]:
                self.yellow_letters.add(letter) if letter not in self.green_letters else None
                self.words_reference[(self.current_word, i)].config(bg=self.colours["yellow"], fg="black")  # yellow
            else:
                self.red_letters.add(letter)
                self.words_reference[(self.current_word, i)].config(bg=self.colours["red"], fg="black")
        # after evaluation of letters
        if self.current_word == self.max_guesses - 1 or self.guess == self.answer:
            self.feedback_label.config(text=f"the word was \"{self.answer}\"")
            self.root.after(2000, self.reset)
        self.update_keyboard_colour()
        self.guess = ""
        self.current_word += 1

    def reset(self) -> None:
        self.answer = random.choice(self.valid_words)
        print(self.answer)
        self.guess = ""
        self.current_word = 0
        self.red_letters = set()
        self.yellow_letters = set()
        self.green_letters = set()
        self.guessed_words = set()
        self.feedback_label.config(text="")
        for key in self.words_reference:
            self.words_reference[key].config(text="", bg=self.colours["button background"][self.colourmode])
        self.update_keyboard_colour()
    
    def quit_game(self) -> None:
        updated_settings = self.settings
        updated_settings["default colourmode"] = self.colourmode
        with open(r"game_files\settings.json", "w") as settings_file:
            json.dump(updated_settings, settings_file, indent=4)
        self.root.destroy()
    
    def mainloop(self) -> None:
        self.colourmode_button.pack(anchor="nw", padx=5, pady=5)
        self.keyboard_frame.pack(pady=5)
        self.feedback_label.pack(pady=5)
        self.word_frame.pack(pady=5)
        self.root.mainloop()


def main() -> None:
    GUI().mainloop()


if __name__ == "__main__":
    main()
