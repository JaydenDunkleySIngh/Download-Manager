import os
import sys
import time
import logging
import shutil
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# The folder being monitored (Downloads) and the destination folders for different file types
folder_path = r'C:\Users\Ditto\Downloads'
destination_music = r'C:\personal projects\downloads folder\music'
destination_videos = r'C:\personal projects\downloads folder\video'
destination_documents = r'C:\personal projects\downloads folder\documents'
destination_images = r'C:\personal projects\downloads folder\image'

# Function to make a unique filename if one with the same name already exists in the destination
def makeUnique(file, destination):
    counter = 0
    for f in os.listdir(destination):
        if file.startswith(f):
            counter += 1
            
    # If duplicates are found, add a counter to the file name        
    if counter > 0:
     file = file.lower() + "_" + str(counter)
    logging.info(f"Renaming file to {file}")
    return file

# Function to move a file to the correct destination folder
def move(file, destination):    
    path = os.path.join(folder_path, file)
    logging.info(f"Attempting to move file {file} to {destination}")
    
    # Skip if the file doesn’t exist
    if not os.path.exists(path):
        return
    
    # Create a unique name if needed
    unique_name = makeUnique(file, destination)  
    new_path = os.path.join(destination, unique_name)
    logging.info(f"New path is {new_path}")
    
    # Small delay to ensure the file has finished downloading before moving
    time.sleep(2)
    
    # Skip moving empty or 0-byte files
    if os.path.getsize(path) <  1:
        logging.info(f"File {file} is too small to move, skipping. Size: {os.path.getsize(path)} bytes")
        return
    
    # Try moving the file 
    try:
        shutil.move(path, new_path)
        logging.info(f"Moved file {file} to {destination}")
    except Exception as e:
        print(f"Error moving file {file} to {destination}: {e}  ")

# Class that handles file system events 
class FileMover(FileSystemEventHandler):
    # This method runs every time a new file is created in downloads folder
    def on_created(self, event):
        logging.info("on_created fired for: %s", event.src_path)
        
        # Ignore directories — only handle files
        if event.is_directory:
            return
        
        # Loop through all files currently in the Downloads folder
        for file in os.listdir(folder_path):
                name = file.lower()
                destination = folder_path
                
                # Move the file based on its extension (file type)
                if name.endswith('.mp3') or name.endswith('.aac') or name.endswith('.wav'):
                    destination = destination_music
                    move(name, destination)
                elif name.endswith('.mp4') or name.endswith('.mov') or name.endswith('.avi'):
                    destination = destination_videos
                    move(name, destination)
                elif name.endswith('.pdf') or name.endswith('.docx') or name.endswith('.txt'):
                    destination = destination_documents
                    move(name, destination)
                elif name.endswith('.jpg') or name.endswith('.jpeg') or name.endswith('.png'):
                    destination = destination_images
                    move(name, destination)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = folder_path
    
    # Create an instance of the event handler
    event_handler = FileMover()
    
    # Create and start the watchdog observer
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    # Keep the script running indefinitely
    try:
        while True:
            time.sleep(1)
            
    # Stop the observer when the user interrupts (Ctrl + C)     
    except KeyboardInterrupt:
        
        observer.stop()
    observer.join()