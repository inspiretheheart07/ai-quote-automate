from moviepy.editor import AudioFileClip, ImageClip
import subprocess


def create_video_with_music(image_path, music_file):
    audio_clip = AudioFileClip(music_file).subclip(0, 55)
    image_clip = ImageClip(image_path, duration=55)
    image_clip = image_clip.set_audio(audio_clip)
    video_path = 'output_video.mp4'
    image_clip.write_videofile(video_path, fps=24,codec='libx264', audio_codec='aac')
    convert_to_reels()
    return video_path



def convert_to_reels(aspect_ratio='16:9', duration=59):
    """
    Convert a video to Instagram compatible format using FFmpeg.
    
    Parameters:
    - input_video_path: Path to the input video file (e.g., 'input.mp4')
    - output_video_path: Path where the converted video will be saved (e.g., 'output.mp4')
    - aspect_ratio: Aspect ratio to convert to ('16:9' for Feed, '9:16' for Reels)
    - duration: Duration of the video to be kept (Instagram allows 3-60 seconds for posts)
    """
    
    # Prepare the aspect ratio settings
    if aspect_ratio == '16:9':
        scale_params = "scale=iw*min(1280/iw\,720/ih):ih*min(1280/iw\,720/ih),pad=1280:720:(1280-iw)/2:(720-ih)/2"
        aspect_param = '16:9'
    elif aspect_ratio == '9:16':
        scale_params = "scale=iw*min(1080/iw\,1920/ih):ih*min(1080/iw\,1920/ih),pad=1080:1920:(1080-iw)/2:(1920-ih)/2"
        aspect_param = '9:16'
    else:
        raise ValueError("Unsupported aspect ratio. Use '16:9' or '9:16'.")
    
    # FFmpeg command to convert the video
    command = [
        'ffmpeg', 
        '-i', 'output_video.mp4',  # input video file
        '-c:v', 'libx264',  # video codec H.264
        '-aspect', aspect_param,  # aspect ratio (16:9 or 9:16)
        '-crf', '18',  # quality setting
        '-vf', scale_params,  # scale and pad the video to match aspect ratio
        '-fpsmax', '30',  # set the maximum FPS
        '-preset', 'ultrafast',  # encoding speed setting (ultrafast for speed)
        '-c:a', 'aac',  # audio codec (AAC)
        '-b:a', '128k',  # audio bitrate
        '-ac', '1',  # mono audio (you can change to '2' for stereo if needed)
        '-pix_fmt', 'yuv420p',  # pixel format
        '-movflags', '+faststart',  # enable faststart for streaming
        '-t', str(duration),  # duration in seconds
        '-y', 'output_video_converted.mp4'  # output video file
    ]
    
    # Run the FFmpeg command
    subprocess.run(command)
    
    print(f"Video successfully converted and saved as {'output_video_converted.mp4'}")
