import os
import argparse
import subprocess

def download_wav(speaker, url):
    # 組成目標資料夾路徑
    target_dir = os.path.expanduser(f"~/Desktop/hall_of_fame/data/raw/{speaker}")
    os.makedirs(target_dir, exist_ok=True)

    # 建立 yt-dlp 指令
    cmd = [
        "yt-dlp",
        "-x",  # 提取音訊
        "--audio-format", "wav",
        "-o", f"{target_dir}/%(title)s.%(ext)s",  # 輸出格式
        url
    ]

    print(f"📥 下載音訊中，講者：{speaker}...")
    subprocess.run(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="下載 YouTube 音訊為 .wav 檔並儲存至講者資料夾")
    parser.add_argument("--speaker", required=True, help="講者資料夾名稱，例如：simpson")
    parser.add_argument("--url", required=True, help="YouTube 影片連結")

    args = parser.parse_args()
    download_wav(args.speaker, args.url)
