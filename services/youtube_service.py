import yt_dlp
import os


class YouTubeService:
    def __init__(self, download_root='downloads', cookie_path='cookies/cookies.txt'):
        self.download_root = download_root
        self.cookie_path = cookie_path
        self.quality_map = {
            'high': 'best[height>=1080]',
            'medium': 'best[height<=720]',
            'low': 'best[height<=360]',
        }
        self.quality_order = ['high', 'medium', 'low']

    def get_available_qualities(self, link):
        """بررسی کیفیت‌های قابل دانلود برای لینک"""
        ydl_opts = {
            'cookiefile': self.cookie_path,
            'quiet': True,
            'no_warnings': True,
        }
        try:
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
                return list(qualities)
        except Exception as e:
            print(f"⚠️ خطا هنگام گرفتن کیفیت‌ها: {e}")
            return []

    def get_best_available_quality(self, requested, available):
        """برمی‌گردونه بهترین کیفیت قابل دسترسی، اگر کیفیت درخواستی موجود نبود"""
        if requested in available:
            return requested
        for q in self.quality_order:
            if q in available:
                return q
        return None  # هیچ کیفیتی موجود نبود

    def download(self, link, user_id, quality='medium'):
        output_dir = os.path.join(self.download_root, str(user_id))
        os.makedirs(output_dir, exist_ok=True)

        available = self.get_available_qualities(link)
        if not available:
            print("🚫 هیچ کیفیتی برای این لینک یافت نشد.")
            return None

        selected_quality = self.get_best_available_quality(quality, available)
        if not selected_quality:
            print("🚫 هیچ کیفیت سازگاری برای دانلود پیدا نشد.")
            return None

        format_str = self.quality_map.get(selected_quality, 'best')

        ydl_opts = {
            'format': format_str,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'cookiefile': self.cookie_path,
            'continuedl': True,
            'socket_timeout': 30,
            'retries': 10,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                if not info:
                    print("🚫 اطلاعاتی برای فایل دریافت نشد.")
                    return None

                filename = ydl.prepare_filename(info)
                return filename
        except Exception as e:
            print(f"🚫 خطا در دانلود: {e}")
            return None
