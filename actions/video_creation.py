from moviepy.editor import AudioFileClip, ImageClip

def create_video_with_music(image_path, music_file):
    audio_clip = AudioFileClip(music_file).subclip(0, 55)
    image_clip = ImageClip(image_path, duration=55)
    image_clip = image_clip.set_audio(audio_clip)
    video_path = 'output_video.mp4'
    image_clip.write_videofile(video_path, fps=24,codec='libx264', audio_codec='aac')
    return video_path
