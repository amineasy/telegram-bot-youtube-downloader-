import yt_dlp
import os


class YouTubeService:
    def __init__(self, download_root='downloads'):
        self.download_root = download_root
        # مپ کیفیت‌ها
        self.quality_map = {
            'high': 'best[height>=1080]',
            'medium': 'best[height<=720]',
            'low': 'best[height<=360]',
        }

    def get_available_qualities(self, link):
        """کیفیت‌های موجود برای لینک رو برمیگردونه (لیستی از کیفیت‌های پشتیبانی شده)"""
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            formats = info.get('formats', [])
            qualities = set()

            for f in formats:
                height = f.get('height')
                if height:
                    if height >= 1080:
                        qualities.add('high')
                    elif height >= 720:
                        qualities.add('medium')
                    elif height >= 360:
                        qualities.add('low')

            # برمیگردونه فقط کیفیت‌های موجود (مجموعه به لیست)
            return list(qualities)

    def download(self, link, user_id, quality='medium'):
        """دانلود ویدیو با کیفیت مشخص برای یک کاربر"""
        # مسیر پوشه کاربر
        output_dir = os.path.join(self.download_root, str(user_id))
        os.makedirs(output_dir, exist_ok=True)

        format_str = self.quality_map.get(quality, 'best')
        ydl_opts = {
            'format': format_str,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            return filename  # مسیر کامل فایل دانلود شده
