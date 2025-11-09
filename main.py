import yt_dlp
import os
import re

# 🔧 Pemetaan tinggi (height) ke resolusi standar YouTube
RESOLUTION_MAP = {
    range(0, 180): "144p",
    range(180, 270): "240p",
    range(270, 400): "360p",
    range(400, 550): "480p",
    range(550, 800): "720p",
    range(800, 1200): "1080p",
    range(1200, 1600): "1440p",
    range(1600, 2300): "2160p (4K)",
}

def normalize_resolution(height):
    """Konversi height ke resolusi standar YouTube"""
    for r, label in RESOLUTION_MAP.items():
        if height in r:
            return label
    return f"{height}p"

def list_video_qualities(url):
    """Ambil daftar resolusi video yang benar-benar tersedia"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'skip_unavailable_fragments': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])

    video_formats = []
    for f in formats:
        if f.get('height') and f.get('vcodec') != 'none':
            resolution = normalize_resolution(f['height'])
            ext = f['ext']
            size = f.get('filesize') or f.get('filesize_approx')
            if not size:
                continue
            size_mb = round(size / 1024 / 1024, 2)
            if not any(v['resolution'] == resolution for v in video_formats):
                video_formats.append({
                    'format_id': f['format_id'],
                    'resolution': resolution,
                    'ext': ext,
                    'size': size_mb
                })
    return video_formats

def hook_function(d):
    if d['status'] == 'downloading':
        print(f"📥 Mengunduh: {d['_percent_str']} ({d.get('_speed_str', '')})")
    elif d['status'] == 'finished':
        print(f"✅ Selesai! Disimpan sebagai: {d['filename']}")

def get_unique_filename(folder, title, ext):
    """Jika file sudah ada, tambahkan (1), (2), dst"""
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
    base = os.path.join(folder, safe_title)
    filename = f"{base}.{ext}"
    counter = 1
    while os.path.exists(filename):
        filename = f"{base} ({counter}).{ext}"
        counter += 1
    return filename

def download_video(url, format_id):
    """Unduh video dengan format tertentu dan simpan ke folder Downloads"""
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(downloads_folder, exist_ok=True)

    # Ambil info judul agar bisa buat nama unik
    ydl_temp = yt_dlp.YoutubeDL({'quiet': True})
    info = ydl_temp.extract_info(url, download=False)
    title = info.get('title', 'video')

    # Tentukan nama file unik
    filename = get_unique_filename(downloads_folder, title, 'mp4')

    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': filename,
        'noplaylist': True,
        'progress_hooks': [hook_function],
        'quiet': False,
        'no_warnings': True,
        'overwrites': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == '__main__':
    url = input("Masukkan URL video YouTube: ").strip()
    print("\n🔍 Mengambil daftar kualitas video...\n")
    video_formats = list_video_qualities(url)

    if not video_formats:
        print("❌ Tidak ada kualitas video yang bisa ditampilkan.")
    else:
        print("=== Pilih Kualitas Video ===")
        for i, v in enumerate(video_formats, 1):
            print(f"{i}. {v['resolution']} ({v['ext']}, {v['size']} MB)")
        print("=============================")

        choice = input("Pilih nomor kualitas video: ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(video_formats):
                format_id = video_formats[index]['format_id']
                print(f"\n🎬 Mengunduh video dalam kualitas {video_formats[index]['resolution']}...\n")
                download_video(url, format_id)
            else:
                print("❌ Nomor pilihan tidak valid.")
        except ValueError:
            print("❌ Masukkan angka yang benar.")
