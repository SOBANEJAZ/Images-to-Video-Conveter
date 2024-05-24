from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
import moviepy.editor as mp
import os
import shutil

def check_and_reset_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # If folder exists, delete all files inside it
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
    else:
        # If folder doesn't exist, create it
        try:
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created successfully.")
        except OSError as e:
            print(f"Failed to create directory '{folder_path}': {e}")

def add_audio_to_video(video_path, audio_path, output_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)

def delete_folder(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"Folder '{folder_path}' deleted successfully.")
        except Exception as e:
            print(f"Failed to delete folder '{folder_path}': {e}")

def process_folders(folder_path):
    all_clips = []
    for folder_name in os.listdir(folder_path):
        folder_full_path = os.path.join(folder_path, folder_name)
        if os.path.isdir(folder_full_path):
            print(f"Processing folder: {folder_full_path}")
            without_audio_folder = os.path.join(folder_full_path, "without_audio")
            with_audio_folder = os.path.join(folder_full_path, "with_audio")
            check_and_reset_folder(without_audio_folder)
            check_and_reset_folder(with_audio_folder)
            for file_name in os.listdir(folder_full_path):
                file_full_path = os.path.join(folder_full_path, file_name)
                if file_name.endswith(".webp"):
                    audio_file = os.path.join(folder_full_path, file_name.split('.')[0] + ".mp3")
                    if os.path.exists(audio_file):
                        audio_duration = mp.AudioFileClip(audio_file).duration
                        size = (1920, 1080)
                        slide = mp.ImageClip(file_full_path).set_fps(25).set_duration(audio_duration).resize(size)
                        slide = slide.resize(lambda t: 1 + 0.04 * t)  # Zoom-in effect
                        slide = slide.set_position(('center', 'center'))
                        slide = mp.CompositeVideoClip([slide], size=size)
                        without_audio_output = os.path.join(without_audio_folder, file_name.split('.')[0] + ".mp4")
                        slide.write_videofile(without_audio_output)
                        with_audio_output = os.path.join(with_audio_folder, file_name.split('.')[0] + ".mp4")
                        add_audio_to_video(without_audio_output, audio_file, with_audio_output)
                        all_clips.append(VideoFileClip(with_audio_output))
                    else:
                        print(f"No audio file found for {file_name}")
    
    # Concatenate all video clips
    if all_clips:
        final_clip = concatenate_videoclips(all_clips)
        final_output_path = os.path.join(folder_path, "final_output.mp4")
        final_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac")
    
    # Delete the with_audio and without_audio folders
    for folder_name in os.listdir(folder_path):
        folder_full_path = os.path.join(folder_path, folder_name)
        if os.path.isdir(folder_full_path):
            without_audio_folder = os.path.join(folder_full_path, "without_audio")
            with_audio_folder = os.path.join(folder_full_path, "with_audio")
            delete_folder(without_audio_folder)
            delete_folder(with_audio_folder)

if __name__ == "__main__":
    process_folders("files")
