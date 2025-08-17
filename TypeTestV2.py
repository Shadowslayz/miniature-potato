import time
import threading
import openai
import tkinter as tk
from tkinter import messagebox
from fuzzywuzzy import fuzz

client = openai.Client(api_key="")

start_time = None
running = False

class TypingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Test")
        self.root.geometry("600x400")

        self.time_limit = 30  
        self.sentence_length = 10  
        self.sentence = ""
        self.start_time = None
        self.running = False

        # UI Elements
        self.label_instruction = tk.Label(root, text="Enter timer duration (seconds) and sentence length (words):", font=("Arial", 12))
        self.label_instruction.pack(pady=5)

        self.entry_time = tk.Entry(root, font=("Arial", 12), width=10)
        self.entry_time.insert(0, "10")
        self.entry_time.pack(pady=5)

        self.entry_sentence_length = tk.Entry(root, font=("Arial", 12), width=10)
        self.entry_sentence_length.insert(0, "5")
        self.entry_sentence_length.pack(pady=5)

        self.button_generate = tk.Button(root, text="Generate Sentence", command=self.generate_sentence, font=("Arial", 12))
        self.button_generate.pack(pady=10)

        self.label_sentence = tk.Label(root, text="", font=("Arial", 12), wraplength=500)
        self.label_sentence.pack(pady=10)

        self.entry_text = tk.Entry(root, font=("Arial", 12), width=50, state="disabled")
        self.entry_text.pack(pady=5)
        self.entry_text.bind("<Return>", self.finish_test_on_enter) 

        self.label_timer = tk.Label(root, text="", font=("Arial", 12))
        self.label_timer.pack(pady=5)

        self.label_wpm = tk.Label(root, text="WPM: 0", font=("Arial", 12))
        self.label_wpm.pack(pady=5)

        self.label_accuracy = tk.Label(root, text="Accuracy: 0%", font=("Arial", 12))
        self.label_accuracy.pack(pady=5)

        self.button_start = tk.Button(root, text="Start Test", command=self.start_test, font=("Arial", 12), state="disabled")
        self.button_start.pack(pady=10)

    def generate_sentence(self):
        """Fetches a sentence using OpenAI's API."""
        self.time_limit = int(self.entry_time.get())
        self.sentence_length = int(self.entry_sentence_length.get())

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate a string of a specified number of random words. No more no less."},
                {"role": "user", "content": f"Generate a sentence with {self.sentence_length} words."}
            ]
        )
        self.sentence = response.choices[0].message.content.strip()
        self.label_sentence.config(text=self.sentence)
        self.button_start.config(state="normal")

    def start_test(self):
        """Starts the typing test."""
        self.start_time = time.time()
        self.running = True
        self.entry_text.config(state="normal")
        self.entry_text.focus_set()
        
        threading.Thread(target=self.update_timer).start()
        threading.Thread(target=self.update_wpm).start()
        threading.Thread(target=self.update_accuracy).start()
        threading.Thread(target=self.auto_save_progress).start()

    def update_timer(self):
        """Updates the countdown timer."""
        while self.running:
            elapsed_time = time.time() - self.start_time
            remaining_time = max(0, self.time_limit - int(elapsed_time))
            self.label_timer.config(text=f"Time Left: {remaining_time} sec")

            if remaining_time <= 0:
                self.finish_test()
                break

            time.sleep(1)

    def update_wpm(self):
        """Calculates real-time WPM."""
        while self.running:
            elapsed_time = time.time() - self.start_time
            typed_words = len(self.entry_text.get().split())
            wpm = (typed_words / elapsed_time) * 60 if elapsed_time > 0 else 0
            self.label_wpm.config(text=f"WPM: {wpm:.2f}")
            time.sleep(2)

    def update_accuracy(self):
        """Calculates real-time typing accuracy using FuzzyWuzzy."""
        while self.running:
            typed_sentence = self.entry_text.get()  # Fetch the latest typed text dynamically
            accuracy = self.calculate_accuracy(self.sentence, typed_sentence)
            self.label_accuracy.config(text=f"Accuracy: {accuracy:.2f}%")
            time.sleep(2)

    def auto_save_progress(self):
        """Saves user progress every 5 seconds."""
        while self.running:
            with open("typing_progress.txt", "w") as file:
                file.write(self.entry_text.get())
            time.sleep(5)

    def finish_test_on_enter(self, event):
        """Handles submission when Enter is pressed."""
        self.finish_test()

    def finish_test(self):
        """Stops the timer and displays results."""
        self.running = False  
        typed_sentence = self.entry_text.get()  # Get final input from the box
        elapsed_time = time.time() - self.start_time

        typed_words = len(typed_sentence.split())
        typed_chars = len(typed_sentence)
        final_wpm = (typed_words / elapsed_time) * 60 if elapsed_time > 0 else 0
        final_cps = typed_chars / elapsed_time if elapsed_time > 0 else 0
        accuracy = self.calculate_accuracy(self.sentence, typed_sentence)

        messagebox.showinfo("Test Completed", 
            f"Typed Sentence:\n{typed_sentence}\n\n"
            f"Characters Typed: {typed_chars}\n"
            f"Words Typed: {typed_words}\n"
            f"Typing Speed: {final_wpm:.2f} WPM\n"
            f"Characters per Second: {final_cps:.2f} CPS\n"
            f"Accuracy: {accuracy:.2f}%\n"
            f"Total Time Taken: {elapsed_time:.2f} sec"
        )

        self.entry_text.delete(0, tk.END)  # Clears the text box after clicking OK

    def calculate_accuracy(self, original, typed):
        """Uses FuzzyWuzzy for sentence comparison accuracy."""
        original = original.strip()
        typed = typed.strip()
        accuracy = fuzz.ratio(original, typed)  # Compare similarity using FuzzyWuzzy
        return accuracy

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTestApp(root)
    root.mainloop()