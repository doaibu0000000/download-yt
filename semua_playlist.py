import os
import yt_dlp

# ======================
# Folder Download
# ======================
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(downloads_folder, exist_ok=True)

# ======================
# bypass SABR
# ======================
extractor_settings = {
    "extractor_args": {
        "youtube": {
            "player_client": ["android_vr"],
            "js_engine": "node"
        }
    }
}

# Prioritas resolusi tinggi ke rendah
FALLBACK_LIST = [1080, 720, 480, 360, 240, 144]


def ambil_format(video_url):
    """Ambil semua format mp4 dengan apakah progressive atau tidak (video+audio)."""
    ydl_opts = {"quiet": True, **extractor_settings}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

    formats = []

    for f in info.get("formats", []):
        if f.get("height") and f.get("ext") == "mp4":
            formats.append({
                "resolution": f["height"],
                "itag": f.get("format_id"),
                "progressive": (f.get("acodec") != "none"),  # video+audio dalam 1 file?
            })

    return formats


def pilih_resolusi(formats):
    """Pilih resolusi terbaik berdasarkan fallback list."""
    available = {f["resolution"] for f in formats}

    for res in FALLBACK_LIST:
        if res in available:
            return res
    return None


def download(video_url, resolution, formats):
    """Download dengan audio, progressive atau dash."""
    # Cek apakah ada progressive MP4 untuk resolusi itu
    progressive_formats = [
        f["itag"] for f in formats
        if f["resolution"] == resolution and f["progressive"]
    ]

    if progressive_formats:
        # Video langsung ada audio → download 1 file
        format_selector = progressive_formats[0]
    else:
        # DASH → video & audio terpisah → merge otomatis
        format_selector = f"bestvideo[height={resolution}][ext=mp4]+bestaudio[ext=m4a]"

    ydl_opts = {
        "format": format_selector,
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(downloads_folder, "%(title)s.%(ext)s"),
        **extractor_settings
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def ambil_playlist(url):
    """Ambil semua video URL dari playlist."""
    ydl_opts = {"extract_flat": True, "quiet": True, **extractor_settings}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(url, download=False)

    return [f"https://www.youtube.com/watch?v={v['id']}" for v in data["entries"]]


# =======================
# Program Utama
# =======================
print("Masukkan URL video / playlist YouTube:")
url = input("> ").strip()

print("\n📂 Mengambil data playlist...")
playlist = ambil_playlist(url)

if not playlist:
    print("❌ Playlist kosong.")
    exit()

print("\n🚀 Mulai download semua video...\n")
print(f"📁 Lokasi file: {downloads_folder}\n")

for idx, video in enumerate(playlist, 1):
    print(f"\n[{idx}/{len(playlist)}] Mengecek format video...")

    formats = ambil_format(video)

    if not formats:
        print("❌ Tidak ada format MP4.")
        continue

    res = pilih_resolusi(formats)

    if not res:
        print("❌ Tidak ada resolusi tersedia.")
        continue

    print(f"📥 Download {res}p dengan audio...")
    download(video, res, formats)

print("\n✅ Semua video selesai di-download!")
print(f"📂 Disimpan di: {downloads_folder}")

