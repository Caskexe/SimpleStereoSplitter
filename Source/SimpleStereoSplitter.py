import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from pydub import AudioSegment
import os
import threading

class SimpleStereoSplitter:
	def __init__(self, root):
		self.root = root
		self.root.title("SimpleStereoSplitter")
		self.root.geometry("600x400")

		# --- Dark theme colours ---
		self.bg = "#1e1e1e"
		self.fg = "#e0e0e0"
		self.btn_bg = "#2a2a2a"
		self.accent = "#3a3a3a"

		self.root.configure(bg=self.bg)

		self.files = []

		# --- Menu bar ---
		menu_bar = tk.Menu(root, bg=self.bg, fg=self.fg, tearoff=0)
		help_menu = tk.Menu(menu_bar, tearoff=0, bg=self.bg, fg=self.fg)
		help_menu.add_command(label="About", command=self.show_about)
		menu_bar.add_cascade(label="Help", menu=help_menu)
		root.config(menu=menu_bar)

		# Instructions
		self.label = tk.Label(root, text="Drag and drop audio files here or click 'Add Files'", bg=self.bg, fg=self.fg)
		self.label.pack(pady=10)
		
		# Listbox
		self.listbox = tk.Listbox(root, width=80, height=10, bg=self.accent, fg=self.fg, selectbackground="#555")
		self.listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
		
		# Buttons
		btn_frame = tk.Frame(root, bg=self.bg)
		btn_frame.pack(pady=5)

		self.add_button = tk.Button(btn_frame, text="Add Files", command=self.add_files, bg=self.btn_bg, fg=self.fg)
		self.add_button.grid(row=0, column=0, padx=5)

		self.remove_button = tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected, bg=self.btn_bg, fg=self.fg)
		self.remove_button.grid(row=0, column=1, padx=5)

		self.clear_button = tk.Button(btn_frame, text="Clear List", command=self.clear_list, bg=self.btn_bg, fg=self.fg)
		self.clear_button.grid(row=0, column=2, padx=5)

		# Suffix
		self.suffix_label = tk.Label(root, text="Choose suffix style:", bg=self.bg, fg=self.fg)
		self.suffix_label.pack(pady=5)

		self.suffix_options = ["_L and _R", ".L and .R", "LEFT and RIGHT", "Left and Right", "[L] and [R]"]
		self.suffix_var = tk.StringVar(value=self.suffix_options[0])
		self.suffix_dropdown = ttk.Combobox(root, textvariable=self.suffix_var, values=self.suffix_options, state="readonly")
		self.suffix_dropdown.pack(pady=5)

		# Output folder
		folder_frame = tk.Frame(root, bg=self.bg)
		folder_frame.pack(pady=5)

		self.output_label = tk.Label(folder_frame, text="Output folder: (default same as input)", bg=self.bg, fg=self.fg)
		self.output_label.pack(side=tk.LEFT)

		self.folder_button = tk.Button(folder_frame, text="Choose Folder", command=self.choose_folder, bg=self.btn_bg, fg=self.fg)
		self.folder_button.pack(side=tk.LEFT, padx=5)

		self.output_folder = None

		# Split button
		self.split_button = tk.Button(root, text="Split Stereo Files", command=self.start_split_thread, bg=self.btn_bg, fg=self.fg)
		self.split_button.pack(pady=10)

		# Progress bar (ttk style tweak)
		style = ttk.Style()
		style.theme_use('default')
		style.configure("TProgressbar", troughcolor=self.accent, background="#4caf50")

		self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
		self.progress.pack(pady=5)

		# Drag & Drop
		self.root.drop_target_register(DND_FILES)
		self.root.dnd_bind('<<Drop>>', self.drop_files)

	# --- About dialog ---
	def show_about(self):
		messagebox.showinfo("About", "A tool by CASK.exe. Version 0.1 (beta) -- https://github.com/Caskexe/SimpleStereoSplitter")

	def add_files(self):
		filenames = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.ogg")])
		for f in filenames:
			if f not in self.files:
				self.files.append(f)
				self.listbox.insert(tk.END, f)

	def remove_selected(self):
		selected = list(self.listbox.curselection())
		for index in reversed(selected):
			self.files.pop(index)
			self.listbox.delete(index)

	def clear_list(self):
		self.files.clear()
		self.listbox.delete(0, tk.END)

	def drop_files(self, event):
		files = self.root.tk.splitlist(event.data)
		for f in files:
			if os.path.isfile(f) and f not in self.files:
				self.files.append(f)
				self.listbox.insert(tk.END, f)

	def choose_folder(self):
		folder = filedialog.askdirectory()
		if folder:
			self.output_folder = folder
			self.output_label.config(text=f"Output folder: {folder}")

	def start_split_thread(self):
		thread = threading.Thread(target=self.split_files)
		thread.start()

	def split_files(self):
		if not self.files:
			messagebox.showwarning("No files", "Please add at least one stereo audio file.")
			return
		
		suffix_choice = self.suffix_var.get()
		suffix_map = {
			"_L and _R": ("_L", "_R"),
			".L and .R": (".L", ".R"),
			"LEFT and RIGHT": (" LEFT", " RIGHT"),
			"Left and Right": (" Left", " Right"),
			"[L] and [R]": (" [L]", " [R]")
		}
		left_suffix, right_suffix = suffix_map[suffix_choice]

		total_files = len(self.files)
		self.progress['value'] = 0
		self.progress['maximum'] = total_files

		for idx, file_path in enumerate(self.files, start=1):
			try:
				audio = AudioSegment.from_file(file_path)

				if audio.channels != 2:
					messagebox.showwarning("Not stereo", f"{os.path.basename(file_path)} is not stereo.")
					continue
				
				left, right = audio.split_to_mono()

				base, ext = os.path.splitext(file_path)
				folder = self.output_folder if self.output_folder else os.path.dirname(file_path)

				left.export(os.path.join(folder, f"{os.path.basename(base)}{left_suffix}{ext}"), format=ext[1:])
				right.export(os.path.join(folder, f"{os.path.basename(base)}{right_suffix}{ext}"), format=ext[1:])
			
			except Exception as e:
				messagebox.showerror("Error", f"Failed to process {file_path}:\n{e}")
				continue
			
			finally:
				self.progress['value'] = idx
				self.root.update_idletasks()

		messagebox.showinfo("Done", "Stereo files split successfully")
		self.listbox.delete(0, tk.END)
		self.files.clear()
		self.progress['value'] = 0


if __name__ == "__main__":
	root = TkinterDnD.Tk()
	app = SimpleStereoSplitter(root)
	root.mainloop()