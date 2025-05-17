import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import threading
import yt_dlp

class YouTubeDownloader:
    def __init__(self):
        # Set up the main window
        self.window = ctk.CTk()
        self.window.title("YouTube Video Downloader")
        self.window.geometry("800x600")
        self.window.configure(fg_color="#1a1a1a")
        
        # Set the theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create the main frame
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="YouTube Video Downloader",
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(pady=20)
        
        # URL Entry
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.url_frame.pack(fill="x", pady=10)
        
        self.url_label = ctk.CTkLabel(
            self.url_frame,
            text="Enter YouTube URL:",
            font=("Helvetica", 14)
        )
        self.url_label.pack(side="left", padx=5)
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            width=400,
            height=35,
            font=("Helvetica", 12)
        )
        self.url_entry.pack(side="left", padx=5)
        
        # Download Button
        self.download_button = ctk.CTkButton(
            self.main_frame,
            text="Download",
            command=self.start_download,
            width=200,
            height=40,
            font=("Helvetica", 14, "bold")
        )
        self.download_button.pack(pady=20)
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Helvetica", 12)
        )
        self.status_label.pack(pady=10)
        
        # Video Info Frame
        self.info_frame = ctk.CTkFrame(self.main_frame, fg_color="#2d2d2d")
        self.info_frame.pack(fill="x", pady=20, padx=20)
        
        self.title_info = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=("Helvetica", 14, "bold"),
            wraplength=700
        )
        self.title_info.pack(pady=5)
        
        self.author_info = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=("Helvetica", 12)
        )
        self.author_info.pack(pady=5)
        
        self.views_info = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=("Helvetica", 12)
        )
        self.views_info.pack(pady=5)

    def ytdlp_progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                percentage = downloaded_bytes / total_bytes
                self.progress_bar.set(percentage)
                self.status_label.configure(text=f"Downloading... {int(percentage * 100)}%")
                self.window.update()
        elif d['status'] == 'finished':
            self.progress_bar.set(1)
            self.status_label.configure(text="Download completed successfully!")
            self.window.update()

    def download_video(self, url):
        try:
            # Get video info first
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            self.title_info.configure(text=f"Title: {info.get('title', 'N/A')}")
            self.author_info.configure(text=f"Uploader: {info.get('uploader', 'N/A')}")
            self.views_info.configure(text=f"Views: {info.get('view_count', 'N/A'):,}")
            # Prepare download folder
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
            ydl_opts = {
                'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
                'progress_hooks': [self.ytdlp_progress_hook],
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", "Video downloaded successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress_bar.set(0)
            self.download_button.configure(state="normal")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        self.download_button.configure(state="disabled")
        self.status_label.configure(text="Starting download...")
        self.progress_bar.set(0)
        
        # Start download in a separate thread
        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True
        thread.start()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run() 