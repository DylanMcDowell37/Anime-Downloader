import requests
import time
import re
import os
import ffmpeg
import rarfile
import fnmatch
import subprocess

def compress_video(video_full_path, output_file_name, target_size):
    # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe(video_full_path)
    # Video duration, in s.
    duration = float(probe['format']['duration'])
    # Audio bitrate, in bps.
    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), {}).get('bit_rate', '0'))
    # Target total bitrate, in bps.
    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    # Target audio bitrate, in bps
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate
    # Target video bitrate, in bps.
    video_bitrate = target_total_bitrate - audio_bitrate

    i = ffmpeg.input(video_full_path)
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run()
    
def search_for_folder_path():
    # Get the list of directories in the current working directory
    dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    # Sort the directories by creation time (newest first)
    dirs.sort(key=lambda x: os.path.getctime(x), reverse=True)
    # Return the newest directory
    if dirs:
        return os.path.abspath(dirs[0])

def search_for_file_path(folder_path):
    files = os.listdir(folder_path)

    # create a list of media file extensions to filter
    media_ext = ["*.mp4", "*.mkv", "*.avi", "*.wmv"]

    # filter the list of files to only include media files
    media_files = []
    for ext in media_ext:
        media_files.extend(fnmatch.filter(files, ext))

    # get the most recently modified media file
    latest_media = media_files[0]

    # return the name of the most recently modified media file
    return latest_media


def extract(dir_path):
    rar_files = [f for f in os.listdir(dir_path) if f.endswith('.rar')]
    rar_files.sort(key=lambda x: os.path.getmtime(os.path.join(dir_path, x)), reverse=True)
    with rarfile.RarFile(rar_files[0]) as rf:
    
        # Print the list of files in the archive
        print(rf.namelist())
        
        # Extract all files to a directory
        rf.extractall(dir_path)

url = input("Enter the URL of tv series: ")
dir = input("Enter Directory Name: ")
x = re.match(r'^(http:|)[/][/]www.([^/]+[.])*todaytvseries2.com', url)

try:
    if x:
    
        req = requests.get(url).content.decode('utf-8')
        seasons = re.findall(r'Download Season ([0-9]{1,})', req)
        seasons.sort()
        get_title = re.search(r'uk-article-title uk-badge1">(.*)</h1>', req).group(1)

        print("\nAvailable seasons to download in" + get_title)
        for i in seasons:
            print(get_title + "season"+ " " + i)

        user_input1 = input("\nEnter the season number that you want to download: ").zfill(2)
        if user_input1 == str("1") or str("01"):
            g = str(int(user_input1))
        else:
            g = str(int(user_input1) - 1)
        if g in seasons:
            a = re.findall(r'<div class="cell2">(S'+user_input1+'E[0-9]{1,})', req)
            print("\nAvailable episodes in " + user_input1 + "\n")
            print(a)
            dir_path = "/media"
            folder_path = "/media/"+dir+"/"
            for i in a:
                if i in req:
                    t = re.findall(r''+i+'</div><div class="cell[0-9]">[0-9]{1,} Mb</div><div class="cell[0-9]"><a href=[\'"]?([^\'" >]+)" class="hvr-icon-sink-away" target="_blank">.*</a></div>', req)[0]
                    os.system("sudo wget {}".format(t))
                    rarfolder = search_for_folder_path()
                    
                    file_variable = search_for_file_path(dir_path)
                    if file_variable:
                        print("Newest file: ", file_variable)
                        videoin = os.path.join(dir_path+"/"+file_variable)
                        videoout = os.path.join(folder_path+file_variable.replace('.ts', '.mp4'))
                        compress_video(videoin, videoout, 50 * 1000)
                        subprocess.call(['sudo', 'rm', '-r', rarfolder])
                        
                    else:
                        print("No directories found.")
                else:
                    print("Unknown Error")
            

        else:
            print("Season " + user_input1 + " not available")

    else:
        print("\nURL not related with todaytvseries2.com domain.")

except KeyboardInterrupt:
    print('\nProgramme Interrupted')
  
print("\nPress any key to exit")
time.sleep(1)