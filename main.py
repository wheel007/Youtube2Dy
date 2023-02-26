import tkinter as tk
from pytube import YouTube
from tkinter import ttk
from pygtrans import Translate
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeDownloader:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader")
        # 需要科学上网，设置自己的代理
        self.proxy = {
            "http": "http://127.0.0.1:10809",
            "https": "https://127.0.0.1:10809"
        }

        self.download_subtitles_proxy = {
            "http": "http://127.0.0.1:10809",
            "https": "http://127.0.0.1:10809"
        }

        # 创建Label和Entry
        self.label = tk.Label(master, text="请输入YouTube视频链接:")
        self.label.grid(row=0, column=0, padx=5, pady=5)
        self.entry = tk.Entry(master, width=50)
        self.entry.grid(row=0, column=1, padx=5, pady=5)

        # 创建Button
        self.button = tk.Button(master, text="下载", command=self.download)
        self.button.grid(row=1, column=1, padx=5, pady=5)

        # 创建进度条
        # TODO 目前进度条不起作用，待调整
        self.progress = ttk.Progressbar(master, orient="horizontal", length=200, mode="determinate")
        self.progress.grid(row=2, column=1, padx=5, pady=5)

        # 创建下载字幕按钮
        self.button = tk.Button(master, text='下载字幕', command=self.download_subtitles)
        self.button.grid(row=3, column=1, padx=10, pady=5)

    def download(self):
        """
        youtube视频下载器
        :return:
        """
        url = self.entry.get()  # 获取用户输入的YouTube链接
        yt = YouTube(url, proxies=self.proxy)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by(
            'resolution').desc().first()  # 获取最高分辨率的MP4视频流

        def progress_callback(chunk, file_handle, bytes_remaining):
            # 计算下载进度并更新进度条
            percent = (1 - bytes_remaining / stream.filesize) * 100
            self.progress["value"] = percent
            self.master.update_idletasks()  # 刷新界面

        yt.register_on_progress_callback(progress_callback)
        filename = stream.download()  # 下载视频到本地
        # TODO 用控件显示
        print(f"视频下载完成，保存为{filename}")

    def time_calculate(self, start, duration):
        """
        读取字幕内容转化为srt文件的时间表示
        :param start: 开始时间
        :param duration: 持续时间
        :return: 返回格式化的字符串，如 00:00:00,000 --> 00:00:01,234
        """
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

        if len(str(start_hour)) < 2:
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

    def save_srt(self, srt, fileName):
        count = 1
        for i in srt:
            with open("{}.srt".format(fileName), "a", encoding="utf-8") as f:
                f.write("{}\n".format(count))
                count += 1
                second_line = self.time_calculate(i["start"], i["duration"])
                f.write("{}\n".format(second_line))
                f.write("{}\n".format(i["text"]))
                f.write("\n")

    def download_subtitles(self):
        """
        下载youtube视频字幕
        :return:
        """
        url = self.entry.get()  # 获取用户输入的YouTube链接
        yt = YouTube(url, proxies=self.proxy)
        video_id = url.split('=')[-1]
        # 获取中文字幕
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=self.download_subtitles_proxy)
        lauguague_code_list = []
        for transcript in transcript_list:
            lauguague_code_list.append(transcript.language_code)
        if "zh-Hans" in lauguague_code_list:
            srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=self.download_subtitles_proxy, languages=["zh-Hans"])
            self.save_srt(srt, fileName=yt.title)
        elif "zh-CN" in lauguague_code_list:
            srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=self.download_subtitles_proxy, languages=["zh-CN"])
            self.save_srt(srt, fileName=yt.title)
        elif "zh-HK" in lauguague_code_list:
            srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=self.download_subtitles_proxy, languages=["zh-HK"])
            self.save_srt(srt, fileName=yt.title)
        elif "zh-TW" in lauguague_code_list:
            srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=self.download_subtitles_proxy, languages=["zh-TW"])
            self.save_srt(srt, fileName=yt.title)
        # elif "en" in lauguague_code_list:
        #     srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy, languages=["en"])
        else:
            # TODO 控件显示
            print("没有中文字幕，尝试机翻")
            srt = YouTubeTranscriptApi.get_transcript(video_id, proxies=self.download_subtitles_proxy)
            client = Translate(proxies=self.download_subtitles_proxy)
            count = 1
            for i in srt:
                with open("{}.srt".format(yt.title), "a", encoding="utf-8") as f:
                    f.write("{}\n".format(count))
                    count += 1
                    second_line = self.time_calculate(i["start"], i["duration"])
                    f.write("{}\n".format(second_line))
                    translated = client.translate(i["text"], target="zh-CN").translatedText # 翻译
                    # TODO 控件显示
                    print("{} -- > {}".format(i["text"], translated))
                    f.write("{}\n".format(translated))
                    f.write("\n")

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    downloader = YouTubeDownloader(root)
    downloader.run()
