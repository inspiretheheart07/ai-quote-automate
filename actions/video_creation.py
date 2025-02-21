from moviepy.editor import AudioFileClip, ImageClip
import ffmpeg


def create_video_with_music(image_path, music_file):
    audio_clip = AudioFileClip(music_file).subclip(0, 55)
    image_clip = ImageClip(image_path, duration=55)
    image_clip = image_clip.set_audio(audio_clip)
    video_path = 'output_video.mp4'
    image_clip.write_videofile(video_path, fps=24,codec='libx264', audio_codec='aac')
    convert_to_reels()
    return video_path



def convert_to_reels():
    # Convert the video using FFmpeg
    ffmpeg.input('output_video.mp4').output(
        'output_video_converted.mp4', 
        vcodec='libx264',      # Use H.264 video codec (recommended for Instagram)
        acodec='aac',          # Use AAC audio codec
        audio_bitrate='128k',  # Audio bitrate 128kbps
        ar='48000',            # Audio sample rate 48kHz
        ac=2,                  # Audio channels (stereo)
        vf='scale=1080:1920',  # Resize video to 1080x1920 (portrait aspect ratio 9:16)
        r=30,                  # Frame rate 30 FPS (within 23-60 FPS range)
        video_bitrate='25000k', # Video bitrate 25Mbps
        strict='experimental',  # For AAC codec compatibility
        movflags='faststart'   # Optimize file for streaming (moov atom at front)
    ).run()

