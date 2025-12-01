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


def ambil_format(video_url):
    ydl_opts = {
        "quiet": True,
        **extractor_settings
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

    formats = []

    for f in info.get("formats", []):
        if (
            f.get("filesize")
            and f.get("height")
            and f.get("vcodec") != "none"
            and f.get("ext") == "mp4"              # ⬅ hanya tampilkan MP4
        ):
            formats.append({
                "format_id": f["format_id"],
                "resolution": f["height"],
                "ext": f["ext"],
                "size": round(f["filesize"] / 1024 / 1024, 2)
            })

    formats.sort(key=lambda x: x["resolution"])
    return formats


def download(video_url, format_id):
    ydl_opts = {
        "format": format_id,
        "outtmpl": os.path.join(downloads_folder, "%(title)s.%(ext)s"),
        **extractor_settings
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def ambil_playlist(url):
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        **extractor_settings
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(url, download=False)

    return [f"https://www.youtube.com/watch?v={v['id']}" for v in data["entries"]]


print("Masukkan URL video / playlist YouTube:")
url = input("> ").strip()

print("\n📂 Mengambil data playlist...")
playlist = ambil_playlist(url)

if not playlist:
    print("❌ Playlist kosong.")
    exit()

first_video = playlist[0]
print(f"🔗 Video pertama: {first_video}")
print("🔍 Mengambil daftar kualitas...\n")

formats = ambil_format(first_video)

if not formats:
    print("❌ Tidak ada format MP4 ditemukan (mungkin kena SABR).")
    exit()

print("=== Pilih Kualitas Video (MP4 Saja) ===")
for i, f in enumerate(formats, 1):
    print(f"{i}. {f['resolution']}p ({f['ext']}, {f['size']} MB)")
print("=======================================")

choice = int(input("Pilih nomor kualitas: ")) - 1
format_id = formats[choice]["format_id"]

print("\n🚀 Mulai download semua video di playlist...\n")
print(f"📁 File akan disimpan di folder: {downloads_folder}\n")

for idx, video in enumerate(playlist, 1):
    print(f"[{idx}/{len(playlist)}] Downloading: {video}")
    download(video, format_id)

print("\n✅ Semua video selesai di-download!")
print(f"📂 Lokasi file: {downloads_folder}")
