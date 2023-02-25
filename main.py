import tkinter as tk
from pytube import YouTube
from tkinter import ttk
from googletrans import Translator
import pysrt


class YouTubeDownloader:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader")

        self.proxy = {
            "http": "http://127.0.0.1:10809",
            "https": "https://127.0.0.1:10809"
        }

        self.requests_get_proxy = {"http": "http://127.0.0.1:10809", "https": "http://127.0.0.1:10809"}

        # 创建Label和Entry
        self.label = tk.Label(master, text="请输入YouTube视频链接:")
        self.label.grid(row=0, column=0, padx=5, pady=5)
        self.entry = tk.Entry(master, width=50)
        self.entry.grid(row=0, column=1, padx=5, pady=5)

        # 创建Button
        self.button = tk.Button(master, text="下载", command=self.download)
        self.button.grid(row=1, column=1, padx=5, pady=5)

        # 创建进度条
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
        print(f"视频下载完成，保存为{filename}")

    def translate_subtitles(self, input_file, output_file):
        """
        翻译字幕
        :return:
        """

        # 输入要翻译成的目标语言
        target_lang = 'zh-cn'

        # 创建Translator对象
        translator = Translator(service_urls=['translate.google.cn'])

        # 打开输入文件
        subs = pysrt.open(input_file)
        print('subs:'+subs)

        # 循环遍历每一个字幕并翻译
        for sub in subs:
            # 只翻译非中文字幕
            if not sub.text.isalpha() and not sub.text.isdigit() and not sub.text.isascii():
                # 翻译字幕
                print(sub.text)
                translation = translator.translate(sub.text, dest=target_lang)
                # 将翻译后的文本保存到字幕对象中
                sub.text = translation.text
                print(sub.text)

        # 将翻译后的字幕保存到输出文件
        subs.save(output_file, encoding='utf-8')

        print("字幕翻译完成！")

    def download_subtitles(self):
        """
        下载youtube视频字幕
        :return:
        """
        url = self.entry.get()
        # 创建YouTube对象
        yt = YouTube(url, proxies=self.proxy)

        # 获取视频的所有字幕
        subtitles = yt.captions

        # 查找中文字幕并下载
        caption = None
        for subtitle in subtitles:
            if subtitle.code == 'zh-Hans':
                caption = subtitles.get_by_language_code(subtitle.code)
                break

        # 如果没有中文字幕则选择英文字幕
        if not caption:
            for subtitle in subtitles:
                if subtitle.code == 'en':
                    caption = subtitles.get_by_language_code(subtitle.code)
                    break

        # 如果中英文字幕都没有则选第一个可用字幕
        if not caption:
            for subtitle in subtitles:
                caption = subtitles.get_by_language_code(subtitle.code)
                break

        # 下载字幕
        if caption:

            subtitle_text = caption.generate_srt_captions()
            fileName = f"{yt.title}.srt"
            with open(fileName, "w", encoding="utf-8") as f:
                f.write(subtitle_text)
            print("字幕已下载完成！")
            # self.translate_subtitles(fileName, fileName)
        else:
            print("字幕不存在！")

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    downloader = YouTubeDownloader(root)
    downloader.run()
