
# ✅ 通用版 Whisper 批次轉錄與合併切段腳本（每段接近 10 秒）
import json
import os
import whisper
import glob
from pydub import AudioSegment


def main():
    """
    這個程式是用來把音檔切成大約10秒的段落，並且轉成16kHz的音訊檔。
    """
    # pararameters setting
    input_root = "data/raw"
    output_root = "data/processed"
    model_size = 'medium'
    merge_target_sec = 10  # 每段音訊的目標長度（秒）

    # creat model
    model = whisper.load_model(model_size)

    # === 🔁 逐一處理每位 speaker ===
    for speaker in os.listdir(input_root):
        # 首先檢查是否為資料夾
        speaker_dir = os.path.join(input_root, speaker)
        if not os.path.isdir(speaker_dir):
            print(f"{speaker} 不是資料夾")
            continue

        print(f"speaker: {speaker}")
        audio_files = glob.glob(os.path.join(speaker_dir, "*.m4a"))  # 尋找資料夾內所有是m4a的音訊檔, 會回傳一個list, 裡面都是音訊檔的路徑(ex:'data/raw/froggy/ep01.m4a')
        if not audio_files:  # 檢查是否有音訊檔
            print(f"{speaker} 無音訊檔")
            continue

        for path in audio_files:
            base = os.path.splitext(os.path.basename(path))[0]  # 取得檔名

            # 創資料夾
            segment_dir = os.path.join(output_root, speaker, "segments_merged", base)
            transcribe_dir = os.path.join(output_root, speaker, "transcribed_merged", f"{base}.json")
            os.makedirs(segment_dir, exist_ok=True)
            os.makedirs(os.path.dirname(transcribe_dir), exist_ok=True)

            # 把音檔轉成文字檔.json
            result = model.transcribe(path, language = 'zh', word_timestamps=False)
            original_segment = result['segments']

            # 合併語音片段（接近１０秒為一組）
            merged_segments = [] # 用來存放合併後的片段
            current_group = [] # 用來存放目前的片段組
            current_duration = 0.0  # 目前片段組的秒數

            for seg in original_segment:    # 每個seg都是一個dict，包含在original_segment裡
                seg_duration = seg['end'] - seg['start']  # 計算每個seg的時長
                current_group.append(seg)  # 把每個seg加入目前片段組
                current_duration += seg_duration  # 更新目前片段組的秒數

                if current_duration >= merge_target_sec:  # 如果目前片段組的秒數大於等於目標秒數(10.0)
                    merged_segments.append(current_group)
                    current_group = []  # 重組一個新的片段
                    current_duration = 0.0

            if current_group:  # 如果還有剩餘的片段組，則加入合併片段，因為有可能剩下的不到10秒
                merged_segments.append(current_group)
            
            audio = AudioSegment.from_file(path)  # 讀取音訊檔

            final_results = [] # 用來存放最終的結果(音訊片段會對應到的文字片段.json)
            for i, group in enumerate(merged_segments):
                start = int(group[0]['start']*1000)  # 把每個組成接近 10 秒的片段，從頭開始取時間
                end = int(group[-1]['end']*1000)  # 把每個組成接近 10 秒的片段，從最後一個取時間，兩個組成就是完整的時間
                clip = audio[start:end]  # 完整段落的音訊片段

                # 將clip匯出成16kHz的音訊檔
                file_name = f"{base}_merged_{i+1:03}.wav"
                output_path = os.path.join(segment_dir, file_name)
                clip.export(output_path, format='wav', parameters=['-ar', '16000'])  # 匯出音訊檔(路徑為outpur_path，wav格式)，並轉成16kHz，-ar是音訊取樣率(simple rate)的參數

                # 將文字片段也存成json檔
                full_text = ' '.join([s['text'] for s in group]) # s['text'] for s in group]所取出的文字組成文字list，然後再join起來
                final_results.append({
                    'file': file_name,
                    'start': group[0]['start'],
                    'end': group[-1]['end'],
                    'text': full_text
                })

            # 將最終結果寫入json檔
            with open(transcribe_dir, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, ensure_ascii=False, indent=2)
            
            print(f"合併分段完成，共輸出 {len(final_results)} 段語音：{segment_dir}")       


if __name__ == "__main__":
    main()