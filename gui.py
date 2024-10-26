import customtkinter as ctk
from tkinter import filedialog, scrolledtext, messagebox
from classifier import classify_images_with_tags
import threading
import os
# Initialize customtkinter
ctk.set_appearance_mode("dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # You can choose themes like "blue", "dark-blue", etc.


class ImageClassifierApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Enhanced Image Classifier with CLIP")
        self.geometry("800x600")

        # Font and color styling
        self.font_style = ("Helvetica", 14)
        self.label_font_style = ("Helvetica", 12, "bold")

        # Create frames for better organization
        self.create_frames()
        self.create_widgets()

    def create_frames(self):
        self.input_frame = ctk.CTkFrame(self, width=600, height=100)
        self.input_frame.pack(pady=10, padx=10, fill="x")

        self.output_frame = ctk.CTkFrame(self, width=600, height=100)
        self.output_frame.pack(pady=10, padx=10, fill="x")

        self.tag_frame = ctk.CTkFrame(self, width=600, height=100)
        self.tag_frame.pack(pady=10, padx=10, fill="x")

        self.log_frame = ctk.CTkFrame(self, width=600, height=200)
        self.log_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.progress_frame = ctk.CTkFrame(self, width=600, height=50)
        self.progress_frame.pack(pady=10, padx=10, fill="x")

    def create_widgets(self):
        # Input folder selection
        ctk.CTkLabel(self.input_frame, text="Select Input Folder:", font=self.label_font_style).pack(side="left",
                                                                                                     padx=10)
        ctk.CTkButton(self.input_frame, text="Browse", command=self.select_input_folder, width=150).pack(side="right",
                                                                                                         padx=10)

        # Checkbox for Recursive Search
        self.recursive_search = ctk.BooleanVar()
        self.recursive_checkbox = ctk.CTkCheckBox(
            self.input_frame,
            text="Recursive Search",
            variable=self.recursive_search,
            font=self.label_font_style
        )
        self.recursive_checkbox.pack(side="right", padx=10)

        # Output folder selection
        ctk.CTkLabel(self.output_frame, text="Select Output Folder:", font=self.label_font_style).pack(side="left",
                                                                                                       padx=10)
        ctk.CTkButton(self.output_frame, text="Browse", command=self.select_output_folder, width=150).pack(side="right",
                                                                                                           padx=10)

        # Tag input field with placeholder
        ctk.CTkLabel(self.tag_frame, text="Enter Tags (comma-separated):", font=self.label_font_style).pack(side="left",
                                                                                                            padx=10)
        self.tag_entry = ctk.CTkEntry(self.tag_frame, width=400, font=self.font_style,
                                      placeholder_text="e.g., dog, landscape, war")
        self.tag_entry.pack(side="right", padx=10)

        # Log display for classification results
        self.log_label = ctk.CTkLabel(self.log_frame, text="Classification Log:", font=self.label_font_style)
        self.log_label.pack(anchor="w", padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, width=80, height=10, font=self.font_style,
                                                  wrap="word")
        self.log_text.pack(padx=10, pady=5, fill="both", expand=True)

        # Progress bar and status label
        self.progress = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress.pack(side="left", padx=10, pady=10)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self.progress_frame, text="Ready", font=self.label_font_style)
        self.status_label.pack(side="right", padx=10)

        # Start classification button
        self.start_button = ctk.CTkButton(self, text="Start Classification", command=self.start_classification_thread,
                                          width=200, font=self.font_style)
        self.start_button.pack(pady=20)

    def select_input_folder(self):
        self.input_folder = filedialog.askdirectory()
        self.log_text.insert("end", f"Selected Input Folder: {self.input_folder}\n")

    def select_output_folder(self):
        self.output_folder = filedialog.askdirectory()
        self.log_text.insert("end", f"Selected Output Folder: {self.output_folder}\n")

    def start_classification_thread(self):
        # Start the classification in a separate thread to keep GUI responsive
        self.start_button.configure(state="disabled")  # Disable start button
        self.status_label.configure(text="Classification in Progress...")
        self.log_text.insert("end", "Classification started...\n")
        thread = threading.Thread(target=self.classify_images)
        thread.start()

    def classify_images(self):
        try:
            tags = [tag.strip() for tag in self.tag_entry.get().split(",")]
            if not tags:
                self.log_text.insert("end", "Please enter at least one tag.\n")
                self.start_button.configure(state="normal")
                self.status_label.configure(text="Ready")
                return

            # Check if input and output folders are set
            if not hasattr(self, 'input_folder') or not self.input_folder:
                raise ValueError("Input folder is not selected. Please select an input folder.")
            if not hasattr(self, 'output_folder') or not self.output_folder:
                raise ValueError("Output folder is not selected. Please select an output folder.")

            recursive = self.recursive_search.get()  # Check if recursive search is enabled

            # Count the total images
            if recursive:
                total_images = sum(len(files) for _, _, files in os.walk(self.input_folder)
                                   if any(f.lower().endswith(('.png', '.jpg', '.jpeg')) for f in files))
            else:
                total_images = len([f for f in os.listdir(self.input_folder)
                                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

            if total_images == 0:
                raise ValueError("No images found in the selected input folder.")

            self.processed_images = 0  # Track number of processed images

            # Start processing images with a callback to update the progress
            classify_images_with_tags(self.input_folder, self.output_folder, tags, self.log_text, recursive,
                                      total_images, self.update_progress)

            self.log_text.insert("end", "Classification complete.\n")
            self.status_label.configure(text="Classification Complete")
            #progress bar to 100%
            self.update_progress(1.0)

        except Exception as e:
            self.log_text.insert("end", f"Error occurred: {e}\n")
            self.log_text.see("end")
            messagebox.showerror("Error", f"An error occurred during classification:\n{e}")
        finally:
            self.start_button.configure(state="normal")
            self.status_label.configure(text="Ready")

    def update_progress(self, progress):
        """Update the progress bar based on the progress value (0 to 1)."""
        self.progress.set(progress)