from pygtrans import Translate
from youtube_transcript_api import YouTubeTranscriptApi
proxy = {
            "http": "http://127.0.0.1:10809",
            "https": "http://127.0.0.1:10809"
        }

# 输入视频链接
url = 'https://www.youtube.com/watch?v=8bzsRpWb0t4'

# 从视频链接中提取视频ID
video_id = url.split('=')[-1]


def time_calculate(start, duration):
    # 计算
    (start_hour, remain) = divmod(start, 3600)
    (start_min, start_sec) = divmod(remain, 60)
    end = start + duration
    (end_hour, remain) = divmod(end, 3600)
    (end_min, end_sec) = divmod(remain, 60)

    start_hour = int(start_hour)
    start_min = int(start_min)
    start_sec = str(int(start_sec * 1000))
    end_hour = int(end_hour)
    end_min = int(end_min)
    end_sec = str(int(end_sec * 1000))

    if len(str(start_hour))<2:
        start_hour = "0" + str(start_hour)
    if len(str(start_min)) < 2:
        start_min = "0" + str(start_min)
    while len(start_sec) < 5:
        start_sec = "0" + start_sec
    str_list = list(start_sec)
    str_list.insert(2, ",")
    start_sec = ''.join(str_list)

    if len(str(end_hour)) < 2:
        end_hour = "0" + str(end_hour)
    if len(str(end_min)) < 2:
       end_min = "0" + str(end_min)
    while len(end_sec) < 5:
        end_sec = "0" + end_sec
    str_list = list(end_sec)
    str_list.insert(2, ",")
    end_sec = ''.join(str_list)

    time_string = "{}:{}:{} --> {}:{}:{}".format(start_hour, start_min, start_sec, end_hour, end_min, end_sec)
    return time_string


def save_srt(srt, fileName):
    count = 1
    for i in srt:
        with open("{}.srt".format(fileName), "a", encoding="utf-8") as f:
            f.write("{}\n".format(count))
            count += 1
            second_line = time_calculate(i["start"], i["duration"])
            f.write("{}\n".format(second_line))
            f.write("{}\n".format(i["text"]))
            f.write("\n")

# 获取视频的字幕信息
transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxy)
lauguague_code_list = []
for transcript in transcript_list:
    lauguague_code_list.append(transcript.language_code)
if "zh-Hans" in lauguague_code_list:
    srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy, languages=["zh-Hans"])
    save_srt(srt, fileName="test")
elif "zh-CN" in lauguague_code_list:
    srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy, languages=["zh-CN"])
    save_srt(srt, fileName="test")
elif "zh-HK" in lauguague_code_list:
    srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy, languages=["zh-HK"])
    save_srt(srt, fileName="test")
elif "zh-TW" in lauguague_code_list:
    srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy, languages=["zh-TW"])
    save_srt(srt, fileName="test")
# elif "en" in lauguague_code_list:
#     srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy, languages=["en"])
else:
    print("没有中文字幕，尝试机翻")
    srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy)
    # for i in srt_list:
    #     if i.is_translatable():
    #         srt = i.translate('zh-Hans').fentch()
    #         break
    client = Translate(proxies=proxy)
    count = 1
    for i in srt:
        with open("{}.srt".format("test"), "a", encoding="utf-8") as f:
            f.write("{}\n".format(count))
            count += 1
            second_line = time_calculate(i["start"], i["duration"])
            f.write("{}\n".format(second_line))
            translated = client.translate(i["text"], target="zh-CN").translatedText
            print("{} -- > {}".format(i["text"], translated))
            # i["text"] = translated
            f.write("{}\n".format(translated))
            f.write("\n")


