#!/usr/bin/env python3
# convert_multilang.py
# GUI-утилита (GTK3) для конвертации видео/аудио с поддержкой RU/EN/DE/UK/BE,
# предпросмотром и паузой/возобновлением конвертации.
# Зависимости: python3, PyGObject (gtk3), ffmpeg, gstreamer (для предпросмотра).

import os
os.environ["GTK_THEME"] = "Mint-X"
os.environ["GTK_ICON_THEME"] = "Mint-X"
os.environ["XDG_DATA_DIRS"] = "/usr/share:/usr/local/share"
import sys
import json
import shlex
import threading
import subprocess
import shutil
import time
import signal

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
from gi.repository import Gtk, GObject, GLib, Gdk, Gst

LANGS = {
    "be": {
        "title": "Канвертар",
        "input": "Уваходны файл:",
        "browse": "Агляд",
        "profile": "Профіль:",
        "output": "Выхадны файл:",
        "output_dir": "Тэчка для выхадных файлаў:",
        "save": "Захаваць",
        "overwrite": "Перазапісаць, калі існуе",
        "convert": "Канвертаваць",
        "preset_mgr": "Параметры",
        "lang": "Мова",
        "log": "Журнал:",
        "pause": "Паўза",
        "resume": "Працягнуць",
        "clear_log": "Ачысціць журнал",
        "preview": "Папярэдні прагляд",
        "export": "Экспартаваць профілі",
        "import": "Імпартаваць профілі",
        "max_threads": "Макс. патокаў:",
        "select_output_dir": "Агляд",
        "ffmpeg_error": "FFmpeg не знойдзены. Калі ласка, усталюйце FFmpeg і пераканайцеся, што ён дададзены ў PATH.",
        "progress_window_title": "Прагрэс канвертацыі",
        "file": "Файл:",
        "status": "Стан:",
        "progress": "Прагрэс:",
        "no_conversion_needed": "Абраны ўваходны фармат {input_ext} ужо супадае з мэтавым фарматам {profile_name}. Канвертацыя не патрэбна.",
        "file_copied": "Файл скапіраваны без канвертацыі: {filename}.",
        "conversion_complete": "Канвертацыя завершана: {filename}.",
        "using_vlc": "Выкарыстоўваецца VLC для папярэдняга прагляду.",
        "vlc_not_found": "VLC не знойдзены. Прабую іншы гульняў...",
        "using_gstreamer": "Выкарыстоўваецца GStreamer для папярэдняга прагляду.",
        "gstreamer_not_available": "GStreamer не даступны.",
        "conversion_paused": "Канвертацыя прыпынена.",
        "conversion_resumed": "Канвертацыя працягнута.",
        "conversion_already_finished": "Канвертацыя ўжо завершана.",
        "process_not_found": "Працэс канвертацыі не існуе.",
        "resolution_error": "Памылка пры атрыманні разрознення: {error}",
        "file_not_found": "Файл не знойдзены: {filename}",
        "conversion_error": "Памылка канвертацыі: {error}",
        "gstreamer_error": "Памылка GStreamer: {error}",
        "playback_error": "Памылка адтворэння: {error}",
        "playback_finished": "Адтворэнне завершана.",
        "profile_not_selected": "Профіль не абраны.",
        "input_file_not_selected": "Уваходны файл не абраны.",
        "trim_enable": "Абрэзаць, калі патрэбна",
        "trim_start": "Пачатак (MM:SS или сек):",
        "trim_end": "Канец (MM:SS или сек):",
        "crf_label": "CRF (качество, 0-51):"
    },
    "de": {
        "title": "Konverter",
        "input": "Eingabedatei:",
        "browse": "Durchsuchen",
        "profile": "Profil:",
        "output": "Ausgabedatei:",
        "output_dir": "Ausgabeordner:",
        "save": "Speichern",
        "overwrite": "Überschreiben, falls vorhanden",
        "convert": "Konvertieren",
        "preset_mgr": "Profile",
        "lang": "Sprache",
        "log": "Protokoll:",
        "pause": "Pause",
        "resume": "Fortsetzen",
        "clear_log": "Protokoll löschen",
        "preview": "Vorschau",
        "export": "Profile exportieren",
        "import": "Profile importieren",
        "max_threads": "Max. Threads:",
        "select_output_dir": "Ausgabeordner auswählen",
        "ffmpeg_error": "FFmpeg nicht gefunden. Bitte installieren Sie FFmpeg und stellen Sie sicher, dass es im PATH ist.",
        "progress_window_title": "Konvertierungsfortschritt",
        "file": "Datei:",
        "status": "Status:",
        "progress": "Fortschritt:",
        "no_conversion_needed": "Das ausgewählte Eingabeformat {input_ext} stimmt bereits mit dem Zielformat {profile_name} überein. Konvertierung ist nicht erforderlich.",
        "file_copied": "Datei ohne Konvertierung kopiert: {filename}.",
        "conversion_complete": "Konvertierung abgeschlossen: {filename}.",
        "using_vlc": "VLC wird für die Vorschau verwendet.",
        "vlc_not_found": "VLC nicht gefunden. Versuche einen anderen Player...",
        "using_gstreamer": "GStreamer wird für die Vorschau verwendet.",
        "gstreamer_not_available": "GStreamer ist nicht verfügbar.",
        "conversion_paused": "Konvertierung pausiert.",
        "conversion_resumed": "Konvertierung fortgesetzt.",
        "conversion_already_finished": "Konvertierung bereits abgeschlossen.",
        "process_not_found": "Konvertierungsprozess existiert nicht.",
        "resolution_error": "Fehler beim Abrufen der Auflösung: {error}",
        "file_not_found": "Datei nicht gefunden: {filename}",
        "conversion_error": "Konvertierungsfehler: {error}",
        "gstreamer_error": "GStreamer-Fehler: {error}",
        "playback_error": "Wiedergabefehler: {error}",
        "playback_finished": "Wiedergabe abgeschlossen.",
        "profile_not_selected": "Profil nicht ausgewählt.",
        "input_file_not_selected": "Eingabedatei nicht ausgewählt.",
        "trim_enable": "Trimmen, falls erforderlich",
        "trim_start": "Start (MM:SS oder sek):",
        "trim_end": "Ende (MM:SS oder sek):",
        "crf_label": "CRF (Qualität, 0-51):"
    },
    "en": {
        "title": "Converter",
        "input": "Input file:",
        "browse": "Browse",
        "profile": "Profile:",
        "output": "Output file:",
        "output_dir": "Output folder:",
        "save": "Save",
        "overwrite": "Overwrite if exists",
        "convert": "Convert",
        "preset_mgr": "Presets",
        "lang": "Language",
        "log": "Log:",
        "pause": "Pause",
        "resume": "Resume",
        "clear_log": "Clear Log",
        "preview": "Preview",
        "export": "Export Profiles",
        "import": "Import Profiles",
        "max_threads": "Max threads:",
        "select_output_dir": "Select Output Folder",
        "ffmpeg_error": "FFmpeg not found. Please install FFmpeg and ensure it is in PATH.",
        "progress_window_title": "Conversion Progress",
        "file": "File:",
        "status": "Status:",
        "progress": "Progress:",
        "no_conversion_needed": "Selected input format {input_ext} already matches the target format {profile_name}. Conversion is not required.",
        "file_copied": "File copied without conversion: {filename}.",
        "conversion_complete": "Conversion completed: {filename}.",
        "using_vlc": "Using VLC for preview.",
        "vlc_not_found": "VLC not found. Trying another player...",
        "using_gstreamer": "Using GStreamer for preview.",
        "gstreamer_not_available": "GStreamer is not available.",
        "conversion_paused": "Conversion paused.",
        "conversion_resumed": "Conversion resumed.",
        "conversion_already_finished": "Conversion already completed.",
        "process_not_found": "Conversion process does not exist.",
        "resolution_error": "Error getting resolution: {error}",
        "file_not_found": "File not found: {filename}",
        "conversion_error": "Conversion error: {error}",
        "gstreamer_error": "GStreamer error: {error}",
        "playback_error": "Playback error: {error}",
        "playback_finished": "Playback finished.",
        "profile_not_selected": "Profile not selected.",
        "input_file_not_selected": "Input file not selected.",
        "trim_enable": "Trim if required",
        "trim_start": "Start (MM:SS or sec):",
        "trim_end": "End (MM:SS or sec):",
        "crf_label": "CRF (quality, 0-51):"
    },
    "ru": {
        "title": "Конвертер",
        "input": "Входной файл:",
        "browse": "Обзор",
        "profile": "Профиль:",
        "output": "Выходной файл:",
        "output_dir": "Каталог для выходных файлов:",
        "save": "Сохранить",
        "overwrite": "Перезаписать, если существует",
        "convert": "Конвертировать",
        "preset_mgr": "Профили",
        "lang": "Язык",
        "log": "Лог:",
        "pause": "Пауза",
        "resume": "Возобновить",
        "clear_log": "Очистить лог",
        "preview": "Предпросмотр",
        "export": "Экспортировать профили",
        "import": "Импортировать профили",
        "max_threads": "Макс. потоков:",
        "select_output_dir": "Обзор",
        "ffmpeg_error": "FFmpeg не найден. Пожалуйста, установите FFmpeg и убедитесь, что он добавлен в PATH.",
        "progress_window_title": "Прогресс конвертации",
        "file": "Файл:",
        "status": "Статус:",
        "progress": "Прогресс:",
        "no_conversion_needed": "Выбранный входной формат {input_ext} уже совпадает с выбранным для конвертации форматом {profile_name}. Конвертация не требуется.",
        "file_copied": "Файл скопирован без конвертации: {filename}.",
        "conversion_complete": "Конвертация завершена: {filename}.",
        "using_vlc": "Используется VLC для предпросмотра.",
        "vlc_not_found": "VLC не найден. Пробуем другой плеер...",
        "using_gstreamer": "Используется GStreamer для предпросмотра.",
        "gstreamer_not_available": "GStreamer не доступен.",
        "conversion_paused": "Конвертация приостановлена.",
        "conversion_resumed": "Конвертация возобновлена.",
        "conversion_already_finished": "Конвертация уже завершена.",
        "process_not_found": "Процесс конвертации не существует.",
        "resolution_error": "Ошибка при получении разрешения: {error}",
        "file_not_found": "Файл не найден: {filename}",
        "conversion_error": "Ошибка конвертации: {error}",
        "gstreamer_error": "Ошибка GStreamer: {error}",
        "playback_error": "Ошибка воспроизведения: {error}",
        "playback_finished": "Воспроизведение завершено.",
        "profile_not_selected": "Профиль не выбран.",
        "input_file_not_selected": "Входной файл не выбран.",
        "trim_enable": "Обрезать, если требуется",
        "trim_start": "Начало (MM:SS или сек):",
        "trim_end": "Конец (MM:SS или сек):",
        "crf_label": "CRF (качество, 0-51):"
    },
    "uk": {
        "title": "Конвертер",
        "input": "Вхідний файл:",
        "browse": "Огляд",
        "profile": "Профіль:",
        "output": "Вихідний файл:",
        "output_dir": "Тека для вихідних файлів:",
        "save": "Зберегти",
        "overwrite": "Перезаписати, якщо існує",
        "convert": "Конвертувати",
        "preset_mgr": "Профілі",
        "lang": "Мова",
        "log": "Журнал:",
        "pause": "Пауза",
        "resume": "Продовжити",
        "clear_log": "Очистити журнал",
        "preview": "Попередній перегляд",
        "export": "Експортувати профілі",
        "import": "Імпортувати профілі",
        "max_threads": "Макс. потоків:",
        "select_output_dir": "Огляд",
        "ffmpeg_error": "FFmpeg не знайдено. Будь ласка, встановіть FFmpeg і переконайтеся, що він доданий до PATH.",
        "progress_window_title": "Прогрес конвертації",
        "file": "Файл:",
        "status": "Стан:",
        "progress": "Прогрес:",
        "no_conversion_needed": "Обраний вхідний формат {input_ext} вже збігається з цільовим форматом {profile_name}. Конвертація не потрібна.",
        "file_copied": "Файл скопійовано без конвертації: {filename}.",
        "conversion_complete": "Конвертація завершена: {filename}.",
        "using_vlc": "Використовується VLC для попереднього перегляду.",
        "vlc_not_found": "VLC не знайдено. Спробую інший програвач...",
        "using_gstreamer": "Використовується GStreamer для попереднього перегляду.",
        "gstreamer_not_available": "GStreamer недоступний.",
        "conversion_paused": "Конвертація призупинена.",
        "conversion_resumed": "Конвертацію відновлено.",
        "conversion_already_finished": "Конвертація вже завершена.",
        "process_not_found": "Процес конвертації не існує.",
        "resolution_error": "Помилка при отриманні роздільної здатності: {error}",
        "file_not_found": "Файл не знайдено: {filename}",
        "conversion_error": "Помилка конвертації: {error}",
        "gstreamer_error": "Помилка GStreamer: {error}",
        "playback_error": "Помилка відтворення: {error}",
        "playback_finished": "Відтворення завершено.",
        "profile_not_selected": "Профіль не обрано.",
        "input_file_not_selected": "Вхідний файл не обрано.",
        "trim_enable": "Обрізати, якщо потрібно",
        "trim_start": "Початок (MM:SS або сек):",
        "trim_end": "Кінець (MM:SS або сек):",
        "crf_label": "CRF (якість, 0-51):"
    }
}

EXTENDED_PROFILES = {
    "3GP (176x144)": {"vcodec": "h263", "acodec": "aac", "width": 176, "height": 144, "video_bitrate": "128k", "audio_bitrate": "64k", "container": "3gp"},
    "3GP (320x240)": {"vcodec": "h263", "acodec": "aac", "width": 320, "height": 240, "video_bitrate": "384k", "audio_bitrate": "96k", "container": "3gp"},
    "3GP (640x480)": {"vcodec": "mpeg4", "acodec": "aac", "width": 640, "height": 480, "video_bitrate": "768k", "audio_bitrate": "128k", "container": "3gp"},
    "PSP (MP4, H.264, 480x272)": {"vcodec": "libx264", "acodec": "aac", "width": 480, "height": 272, "video_bitrate": "800k", "audio_bitrate": "128k", "pix_fmt": "yuv420p", "container": "mp4"},
    "PSP (AVI, XviD, 480x272)": {"vcodec": "libxvid", "acodec": "mp3", "width": 480, "height": 272, "video_bitrate": "800k", "audio_bitrate": "128k", "container": "avi"},
    "MP4 360p (H.264)": {"vcodec": "libx264", "acodec": "aac", "width": 640, "height": 360, "video_bitrate": "800k", "audio_bitrate": "128k", "container": "mp4", "crf": 23},
    "MP4 480p (H.264)": {"vcodec": "libx264", "acodec": "aac", "width": 854, "height": 480, "video_bitrate": "1200k", "audio_bitrate": "128k", "container": "mp4", "crf": 23},
    "MP4 720p (H.264)": {"vcodec": "libx264", "acodec": "aac", "width": 1280, "height": 720, "video_bitrate": "2500k", "audio_bitrate": "128k", "container": "mp4", "crf": 23},
    "MP4 1080p (H.264)": {"vcodec": "libx264", "acodec": "aac", "width": 1920, "height": 1080, "video_bitrate": "5000k", "audio_bitrate": "192k", "container": "mp4", "crf": 23},
    "MP4 4K (H.264)": {"vcodec": "libx264", "acodec": "aac", "width": 3840, "height": 2160, "video_bitrate": "15000k", "audio_bitrate": "192k", "container": "mp4", "crf": 23},
    "HEVC 360p": {"vcodec": "libx265", "acodec": "aac", "width": 640, "height": 360, "video_bitrate": "600k", "audio_bitrate": "128k", "container": "mp4", "crf": 28},
    "HEVC 480p": {"vcodec": "libx265", "acodec": "aac", "width": 854, "height": 480, "video_bitrate": "1000k", "audio_bitrate": "128k", "container": "mp4", "crf": 28},
    "HEVC 720p": {"vcodec": "libx265", "acodec": "aac", "width": 1280, "height": 720, "video_bitrate": "1800k", "audio_bitrate": "128k", "container": "mp4", "crf": 28},
    "HEVC 1080p": {"vcodec": "libx265", "acodec": "aac", "width": 1920, "height": 1080, "video_bitrate": "4000k", "audio_bitrate": "192k", "container": "mp4", "crf": 28},
    "HEVC 4K": {"vcodec": "libx265", "acodec": "aac", "width": 3840, "height": 2160, "video_bitrate": "10000k", "audio_bitrate": "192k", "container": "mp4", "crf": 28},
    "WebM VP8 360p": {"vcodec": "libvpx", "acodec": "libvorbis", "width": 640, "height": 360, "video_bitrate": "500k", "audio_bitrate": "96k", "container": "webm"},
    "WebM VP8 480p": {"vcodec": "libvpx", "acodec": "libvorbis", "width": 854, "height": 480, "video_bitrate": "1000k", "audio_bitrate": "96k", "container": "webm"},
    "WebM VP9 720p": {"vcodec": "libvpx-vp9", "acodec": "libopus", "width": 1280, "height": 720, "video_bitrate": "1500k", "audio_bitrate": "96k", "container": "webm"},
    "WebM VP9 1080p": {"vcodec": "libvpx-vp9", "acodec": "libopus", "width": 1920, "height": 1080, "video_bitrate": "3000k", "audio_bitrate": "128k", "container": "webm"},
    "AVI: DivX, 640x480": {"vcodec": "mpeg4", "acodec": "mp3", "width": 640, "height": 480, "video_bitrate": "1200k", "audio_bitrate": "128k", "container": "avi"},
    "AVI: DivX, 720x480": {"vcodec": "mpeg4", "acodec": "mp3", "width": 720, "height": 480, "video_bitrate": "1500k", "audio_bitrate": "128k", "container": "avi"},
    "AVI: DivX, 1080p": {"vcodec": "mpeg4", "acodec": "mp3", "width": 1920, "height": 1080, "video_bitrate": "8000k", "audio_bitrate": "192k", "container": "avi"},
    "MKV H.264 360p": {"vcodec": "libx264", "acodec": "aac", "width": 640, "height": 360, "video_bitrate": "800k", "audio_bitrate": "128k", "container": "mkv", "crf": 23},
    "MKV H.264 720p": {"vcodec": "libx264", "acodec": "aac", "width": 1280, "height": 720, "video_bitrate": "2500k", "audio_bitrate": "128k", "container": "mkv", "crf": 23},
    "MKV H.265 1080p": {"vcodec": "libx265", "acodec": "aac", "width": 1920, "height": 1080, "video_bitrate": "4000k", "audio_bitrate": "192k", "container": "mkv", "crf": 28},
    "MKV H.265 4K": {"vcodec": "libx265", "acodec": "aac", "width": 3840, "height": 2160, "video_bitrate": "10000k", "audio_bitrate": "192k", "container": "mkv", "crf": 28},
    "Apple iPhone (H.264, 480x320)": {"vcodec": "libx264", "acodec": "aac", "width": 480, "height": 320, "video_bitrate": "800k", "audio_bitrate": "128k", "container": "mp4", "movflags": "+faststart", "crf": 23},
    "Apple iPhone (H.264, 640x480)": {"vcodec": "libx264", "acodec": "aac", "width": 640, "height": 480, "video_bitrate": "1000k", "audio_bitrate": "128k", "container": "mp4", "movflags": "+faststart", "crf": 23},
    "Apple iPad (H.264, 1280x720)": {"vcodec": "libx264", "acodec": "aac", "width": 1280, "height": 720, "video_bitrate": "2500k", "audio_bitrate": "128k", "container": "mp4", "movflags": "+faststart", "crf": 23},
    "Apple iPad (H.264, 1920x1080)": {"vcodec": "libx264", "acodec": "aac", "width": 1920, "height": 1080, "video_bitrate": "5000k", "audio_bitrate": "192k", "container": "mp4", "movflags": "+faststart", "crf": 23},
    "Android 360p (H.264)": {"vcodec": "libx264", "acodec": "aac", "width": 640, "height": 360, "video_bitrate": "800k", "audio_bitrate": "128k", "container": "mp4", "crf": 23},
    "Android 480p (H.264)": {"vcodec": "libx264", "acodec": "aac", "width": 854, "height": 480, "video_bitrate": "1200k", "audio_bitrate": "128k", "container": "mp4", "crf": 23},
    "Android 720p (H.264)": {"vcodec": "libx264", "acodec": "aac", "width": 1280, "height": 720, "video_bitrate": "2500k", "audio_bitrate": "128k", "container": "mp4", "crf": 23},
    "Android 1080p (H.264)": {"vcodec": "libx264", "acodec": "aac", "width": 1920, "height": 1080, "video_bitrate": "5000k", "audio_bitrate": "192k", "container": "mp4", "crf": 23},
    "MPEG-1": {"vcodec": "mpeg1video", "acodec": "mp2", "width": 720, "height": 576, "video_bitrate": "1500k", "audio_bitrate": "224k", "container": "mpeg"},
    "MPEG-2 DVD": {"vcodec": "mpeg2video", "acodec": "mp2", "width": 720, "height": 576, "video_bitrate": "5000k", "audio_bitrate": "192k", "container": "mpeg"},
    "MPEG-2 SVCD": {"vcodec": "mpeg2video", "acodec": "mp2", "width": 480, "height": 576, "video_bitrate": "2500k", "audio_bitrate": "192k", "container": "mpeg"},
    "MPEG-2 VCD": {"vcodec": "mpeg2video", "acodec": "mp2", "width": 352, "height": 288, "video_bitrate": "1150k", "audio_bitrate": "224k", "container": "mpeg"},
    "FLV (Flash Video, 480p)": {"vcodec": "flv", "acodec": "mp3", "width": 854, "height": 480, "video_bitrate": "800k", "audio_bitrate": "128k", "container": "flv"},
    "FLV (Flash Video, 720p)": {"vcodec": "flv", "acodec": "mp3", "width": 1280, "height": 720, "video_bitrate": "1500k", "audio_bitrate": "128k", "container": "flv"},
    "GIF Animation (320x240)": {"vcodec": "gif", "acodec": "none", "width": 320, "height": 240, "fps": 10, "container": "gif"},
    "GIF Animation (640x480)": {"vcodec": "gif", "acodec": "none", "width": 640, "height": 480, "fps": 10, "container": "gif"},
    "AAC Audio": {"vcodec": None, "acodec": "aac", "audio_bitrate": "192k", "container": "m4a"},
    "AC3 Audio": {"vcodec": None, "acodec": "ac3", "audio_bitrate": "192k", "container": "ac3"},
    "AIFF Audio": {"vcodec": None, "acodec": "pcm_s16le", "container": "aiff"},
    "AMR Audio": {"vcodec": None, "acodec": "libopencore_amrnb", "audio_bitrate": "12k", "container": "amr"},
    "FLAC Audio": {"vcodec": None, "acodec": "flac", "container": "flac"},
    "MP3 Audio": {"vcodec": None, "acodec": "libmp3lame", "audio_bitrate": "192k", "container": "mp3"},
    "OGG Audio": {"vcodec": None, "acodec": "libvorbis", "audio_bitrate": "192k", "container": "ogg"},
    "WAV Audio": {"vcodec": None, "acodec": "pcm_s16le", "container": "wav"},
    "DTS Audio": {"vcodec": None, "acodec": "dca", "audio_bitrate": "768k", "container": "dts"},
    "E-AC3 Audio": {"vcodec": None, "acodec": "eac3", "audio_bitrate": "256k", "container": "ec3"},
    "ASF (WMV, 640x480)": {"vcodec": "wmv2", "acodec": "wmav2", "width": 640, "height": 480, "video_bitrate": "1000k", "audio_bitrate": "128k", "container": "asf"},
    "RAW Video (YUV420)": {"vcodec": "rawvideo", "acodec": "none", "pix_fmt": "yuv420p", "container": "yuv"},
    "AV1 720p (WebM)": {
        "vcodec": "libaom-av1",
        "acodec": "libopus",
        "width": 1280,
        "height": 720,
        "video_bitrate": "2000k",
        "audio_bitrate": "128k",
        "container": "webm",
        "cpu_used": "4",
        "threads": "4"
    },
    "AV1 720p (MKV, Макс. качество, медленно)": {
        "vcodec": "libaom-av1",
        "acodec": "libopus",
        "width": 1280,
        "height": 720,
        "video_bitrate": "2000k",
        "audio_bitrate": "128k",
        "container": "mkv",
        "cpu_used": "1",
        "threads": "2"
    },
    "AV1 1080p (WebM)": {
        "vcodec": "libaom-av1",
        "acodec": "libopus",
        "width": 1920,
        "height": 1080,
        "video_bitrate": "4000k",
        "audio_bitrate": "192k",
        "container": "webm",
        "cpu_used": "4",
        "threads": "4"
    },
    "AV1 1080p (MKV, Макс. качество, медленно)": {
        "vcodec": "libaom-av1",
        "acodec": "libopus",
        "width": 1920,
        "height": 1080,
        "video_bitrate": "4000k",
        "audio_bitrate": "192k",
        "container": "mkv",
        "cpu_used": "1",
        "threads": "2"
    },
    "TikTok (9:16)": {"vcodec": "libx264", "acodec": "aac", "width": 720, "height": 1280, "video_bitrate": "2500k", "audio_bitrate": "128k", "container": "mp4", "movflags": "+faststart", "crf": 23},
    "Instagram (1:1)": {"vcodec": "libx264", "acodec": "aac", "width": 1080, "height": 1080, "video_bitrate": "4000k", "audio_bitrate": "192k", "container": "mp4", "movflags": "+faststart", "crf": 23},
    "Opus Audio": {"vcodec": None, "acodec": "libopus", "audio_bitrate": "128k", "container": "opus"},
    "Apple ProRes 422 (1280x720)": {
        "vcodec": "prores_ks",
        "acodec": "pcm_s16le",
        "width": 1280,
        "height": 720,
        "video_bitrate": "50M",
        "audio_bitrate": "1536k",
        "container": "mov",
        "pix_fmt": "yuv422p10le"
    },
    "Apple ProRes 4444 (1920x1080)": {
        "vcodec": "prores_ks",
        "acodec": "pcm_s16le",
        "width": 1920,
        "height": 1080,
        "video_bitrate": "100M",
        "audio_bitrate": "1536k",
        "container": "mov",
        "pix_fmt": "yuv444p10le"
    },
    "H.264 NVENC (1080p)": {
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "width": 1920,
        "height": 1080,
        "video_bitrate": "5000k",
        "audio_bitrate": "192k",
        "container": "mp4",
        "preset": "slow",
        "profile": "high"
    },
    "H.265 NVENC (1080p)": {
        "vcodec": "hevc_nvenc",
        "acodec": "aac",
        "width": 1920,
        "height": 1080,
        "video_bitrate": "4000k",
        "audio_bitrate": "192k",
        "container": "mp4",
        "preset": "slow",
        "profile": "main10"
    },
    "H.264 QuickSync (1080p)": {
        "vcodec": "h264_qsv",
        "acodec": "aac",
        "width": 1920,
        "height": 1080,
        "video_bitrate": "5000k",
        "audio_bitrate": "192k",
        "container": "mp4",
        "preset": "quality"
    },
    "MOV (H.264, 720p)": {"vcodec": "libx264", "acodec": "aac", "width": 1280, "height": 720, "video_bitrate": "2500k", "audio_bitrate": "192k", "container": "mov", "movflags": "+faststart", "crf": 23},
    "MOV (H.264, 1080p)": {"vcodec": "libx264", "acodec": "aac", "width": 1920, "height": 1080, "video_bitrate": "5000k", "audio_bitrate": "192k", "container": "mov", "movflags": "+faststart", "crf": 23},
    "MOV (ProRes 422, 720p)": {"vcodec": "prores_ks", "acodec": "pcm_s16le", "width": 1280, "height": 720, "video_bitrate": "50M", "audio_bitrate": "1536k", "container": "mov", "pix_fmt": "yuv422p10le"},
    "MOV (H.265, 1080p)": {"vcodec": "libx265", "acodec": "aac", "width": 1920, "height": 1080, "video_bitrate": "5000k", "audio_bitrate": "192k", "container": "mov", "crf": 28, "movflags": "+faststart"},
    "MPEG-TS (H.264, 1080p)": {"vcodec": "libx264", "acodec": "aac", "width": 1920, "height": 1080, "video_bitrate": "6000k", "audio_bitrate": "192k", "container": "ts", "crf": 23},
    "FLAC (24-bit, 96kHz)": {"vcodec": None, "acodec": "flac", "audio_bitrate": "2304k", "container": "flac", "sample_fmt": "s32", "ar": 96000},
    "GIF (720p, 15 FPS)": {"vcodec": "gif", "acodec": "none", "width": 1280, "height": 720, "fps": 15, "container": "gif"},
    "DNxHD (1080p)": {"vcodec": "dnxhd", "acodec": "pcm_s16le", "width": 1920, "height": 1080, "video_bitrate": "120M", "audio_bitrate": "1536k", "container": "mov"},
    "MP3 (320 kbps)": {"vcodec": None, "acodec": "libmp3lame", "audio_bitrate": "320k", "container": "mp3", "qscale:a": 0},
}

CONVERT_DIR = os.path.expanduser("~/.Convert")
PREFS_PATH = os.path.join(CONVERT_DIR, "convert_prefs.json")
LOG_PATH = os.path.join(CONVERT_DIR, "convert_log.txt")

def ensure_convert_dir():
    if not os.path.exists(CONVERT_DIR):
        os.makedirs(CONVERT_DIR, exist_ok=True)

def load_prefs():
    prefs = {"lang": "ru", "output_dir": os.path.expanduser("~"), "max_threads": 2, "trim_enabled": False}
    try:
        if os.path.exists(PREFS_PATH):
            with open(PREFS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                prefs.update(data)
    except Exception as e:
        current_lang = prefs.get("lang", "ru")
        print(LANGS.get(current_lang, {}).get("conversion_error", "Ошибка конвертации: {error}").format(error=e))
    return prefs

def save_prefs(p):
    try:
        with open(PREFS_PATH, "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
    except Exception as e:
        current_lang = p.get("lang", "ru")
        print(LANGS.get(current_lang, {}).get("conversion_error", "Ошибка конвертации: {error}").format(error=e))

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_video_resolution(input_file):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", input_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        resolution = result.stdout.strip()
        if resolution:
            width, height = map(int, resolution.split("x"))
            return width, height
    except Exception as e:
        current_lang = load_prefs().get("lang", "ru")
        print(LANGS.get(current_lang, {}).get("resolution_error", "Ошибка при получении разрешения: {error}").format(error=e))
    return None, None

class ProgressWindow(Gtk.Window):
    def __init__(self, parent, filename):
        super().__init__(title=LANGS[parent.lang]["progress_window_title"], transient_for=parent, type_hint=Gdk.WindowTypeHint.DIALOG)
        self.set_default_size(400, 150)
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        self.filename = filename
        self.parent = parent

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        lbl_file = Gtk.Label(label=f"{LANGS[self.parent.lang]['file']} {os.path.basename(self.filename)}")
        self.lbl_status = Gtk.Label(label=f"{LANGS[self.parent.lang]['status']} {LANGS[self.parent.lang]['progress']} 0%")
        self.progress = Gtk.ProgressBar()
        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.connect("clicked", self.on_cancel)

        vbox.pack_start(lbl_file, False, False, 0)
        vbox.pack_start(self.lbl_status, False, False, 0)
        vbox.pack_start(self.progress, True, True, 0)
        vbox.pack_start(btn_cancel, False, False, 0)

    def update_progress(self, percent):
        GLib.idle_add(self.progress.set_fraction, percent / 100.0)
        GLib.idle_add(self.lbl_status.set_text, f"{LANGS[self.parent.lang]['status']} {LANGS[self.parent.lang]['progress']} {percent}%")

    def on_cancel(self, button):
        self.destroy()

class ConverterWindow(Gtk.Window):
    def __init__(self):
        self.prefs = load_prefs()
        self.profiles = EXTENDED_PROFILES
        self.lang = self.prefs.get("lang", "ru")
        self.output_dir = self.prefs.get("output_dir", os.path.expanduser("~"))
        self.max_threads = self.prefs.get("max_threads", 2)
        self.trim_enabled = self.prefs.get("trim_enabled", False)
        self._stop = False
        self._ffmpeg_process = None
        self._conversion_completed = False
        super().__init__(title=LANGS[self.lang]["title"])
        self.set_default_size(750, 500)

        Gst.init(None)

        if not check_ffmpeg():
            self.show_ffmpeg_error()
            return

        grid = Gtk.Grid(column_spacing=6, row_spacing=6, margin=6)
        self.add(grid)

        L = LANGS[self.lang]

        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_lang = Gtk.Label(label=L["lang"], xalign=0)
        self.lang_combo = Gtk.ComboBoxText()
        languages = ["be", "de", "en", "ru", "uk"]
        for lang in languages:
            self.lang_combo.append_text(lang)
        self.lang_combo.set_active(languages.index(self.lang) if self.lang in languages else 0)
        self.lang_combo.connect("changed", self.on_lang_changed)
        lang_box.pack_start(lbl_lang, False, False, 0)
        lang_box.pack_start(self.lang_combo, False, False, 0)
        grid.attach(lang_box, 0, 0, 2, 1)

        lbl_in = Gtk.Label(label=L["input"], xalign=0)
        self.entry_in = Gtk.Entry()
        btn_browse = Gtk.Button(label=L["browse"])
        btn_browse.connect("clicked", self.on_browse)

        lbl_out = Gtk.Label(label=L["output"], xalign=0)
        self.entry_out = Gtk.Entry()

        lbl_out_dir = Gtk.Label(label=L["output_dir"], xalign=0)
        self.entry_out_dir = Gtk.Entry(text=self.output_dir)
        btn_out_dir = Gtk.Button(label=L["select_output_dir"])
        btn_out_dir.connect("clicked", self.on_browse_out_dir)

        lbl_profile = Gtk.Label(label=L["profile"], xalign=0)
        self.combo = Gtk.ComboBoxText()
        self.update_profile_combo()
        self.combo.connect("changed", self.on_profile_changed)

        self.check_overwrite = Gtk.CheckButton(label=L["overwrite"])
        self.check_trim = Gtk.CheckButton(label=L["trim_enable"])
        self.check_trim.set_active(self.trim_enabled)
        self.check_trim.connect("toggled", self.on_trim_toggled)

        lbl_trim_start = Gtk.Label(label=L["trim_start"], xalign=0)
        self.entry_trim_start = Gtk.Entry()
        self.entry_trim_start.set_text("0")
        self.entry_trim_start.set_sensitive(self.trim_enabled)

        lbl_trim_end = Gtk.Label(label=L["trim_end"], xalign=0)
        self.entry_trim_end = Gtk.Entry()
        self.entry_trim_end.set_sensitive(self.trim_enabled)

        btn_convert = Gtk.Button(label=L["convert"])
        btn_convert.connect("clicked", self.on_convert)
        btn_preview = Gtk.Button(label=L["preview"])
        btn_preview.connect("clicked", self.on_preview)
        btn_pause = Gtk.Button(label=L["pause"])
        btn_pause.connect("clicked", self.on_pause)
        btn_resume = Gtk.Button(label=L["resume"])
        btn_resume.connect("clicked", self.on_resume)

        lbl_log = Gtk.Label(label=L["log"], xalign=0)
        self.progress = Gtk.ProgressBar()
        self.logview = Gtk.TextView()
        self.logview.set_editable(False)
        self.logview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.logbuf = self.logview.get_buffer()
        self.logbuf.create_tag("error", foreground="red")
        self.logbuf.create_tag("success", foreground="green")
        self.logbuf.create_tag("warning", foreground="orange")
        scroller_log = Gtk.ScrolledWindow()
        scroller_log.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller_log.set_size_request(350, 150)
        scroller_log.add(self.logview)
        btn_clear_log = Gtk.Button(label=L["clear_log"])
        btn_clear_log.connect("clicked", lambda b: self.logbuf.set_text(""))

        btn_preset = Gtk.Button(label=L["preset_mgr"])
        btn_preset.connect("clicked", self.on_presets)
        btn_export = Gtk.Button(label=L["export"])
        btn_export.connect("clicked", self.on_export_profiles)
        btn_import = Gtk.Button(label=L["import"])
        btn_import.connect("clicked", self.on_import_profiles)

        lbl_threads = Gtk.Label(label=L["max_threads"], xalign=0)
        adjustment = Gtk.Adjustment(
            value=self.max_threads,
            lower=1,
            upper=8,
            step_increment=1,
            page_increment=1,
            page_size=0
        )
        self.spin_threads = Gtk.SpinButton()
        self.spin_threads.set_adjustment(adjustment)
        self.spin_threads.set_numeric(True)
        self.spin_threads.connect("value-changed", self.on_threads_changed)

        left_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        left_grid = Gtk.Grid(column_spacing=6, row_spacing=6)
        left_grid.attach(lbl_in, 0, 0, 1, 1)
        left_grid.attach(self.entry_in, 1, 0, 4, 1)
        left_grid.attach(btn_browse, 5, 0, 1, 1)
        left_grid.attach(lbl_out, 0, 1, 1, 1)
        left_grid.attach(self.entry_out, 1, 1, 4, 1)
        left_grid.attach(lbl_out_dir, 0, 2, 1, 1)
        left_grid.attach(self.entry_out_dir, 1, 2, 4, 1)
        left_grid.attach(btn_out_dir, 5, 2, 1, 1)
        left_grid.attach(lbl_profile, 0, 3, 1, 1)
        left_grid.attach(self.combo, 1, 3, 3, 1)
        left_grid.attach(self.check_overwrite, 1, 4, 3, 1)
        left_grid.attach(self.check_trim, 1, 5, 3, 1)
        left_grid.attach(lbl_trim_start, 0, 6, 1, 1)
        left_grid.attach(self.entry_trim_start, 1, 6, 1, 1)
        left_grid.attach(lbl_trim_end, 0, 7, 1, 1)
        left_grid.attach(self.entry_trim_end, 1, 7, 1, 1)
        left_grid.attach(btn_convert, 4, 8, 1, 1)
        left_grid.attach(btn_preview, 5, 8, 1, 1)
        left_grid.attach(btn_pause, 4, 9, 1, 1)
        left_grid.attach(btn_resume, 5, 9, 1, 1)
        left_vbox.pack_start(left_grid, False, False, 0)

        left_h = Gtk.Box(spacing=6)
        left_h.pack_start(btn_preset, False, False, 0)
        left_h.pack_start(btn_export, False, False, 0)
        left_h.pack_start(btn_import, False, False, 0)
        left_h.pack_start(lbl_threads, False, False, 0)
        left_h.pack_start(self.spin_threads, False, False, 0)
        left_vbox.pack_start(left_h, False, False, 0)

        right_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        right_vbox.pack_start(lbl_log, False, False, 0)
        right_vbox.pack_start(scroller_log, True, True, 0)
        right_vbox.pack_start(btn_clear_log, False, False, 0)

        grid.attach(left_vbox, 0, 1, 1, 1)
        grid.attach(right_vbox, 1, 1, 1, 1)

        target = Gtk.TargetEntry.new("text/uri-list", 0, 0)
        self.entry_in.drag_dest_set(Gtk.DestDefaults.ALL, [target], Gdk.DragAction.COPY)
        self.entry_in.connect("drag-data-received", self.on_drag_data_received_input)

        self.connect("destroy", self.on_window_destroy)

        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("=== Converter Log ===\n")

    def append_log(self, text, tag=None):
        end = self.logbuf.get_end_iter()
        if tag:
            self.logbuf.insert_with_tags(end, text + "\n", self.logbuf.get_tag_table().lookup(tag))
        else:
            self.logbuf.insert(end, text + "\n")

        mark = self.logbuf.create_mark("end", end, left_gravity=False)
        self.logview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        self.logbuf.delete_mark(mark)

        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def on_trim_toggled(self, button):
        self.trim_enabled = button.get_active()
        self.entry_trim_start.set_sensitive(self.trim_enabled)
        self.entry_trim_end.set_sensitive(self.trim_enabled)
        self.prefs["trim_enabled"] = self.trim_enabled
        save_prefs(self.prefs)

    def on_window_destroy(self, *args):
        self.prefs["lang"] = self.lang
        self.prefs["output_dir"] = self.output_dir
        self.prefs["max_threads"] = self.max_threads
        self.prefs["trim_enabled"] = self.trim_enabled
        save_prefs(self.prefs)

    def update_output_path(self):
        infile = self.entry_in.get_text().strip()
        if not infile:
            return
        base = os.path.basename(infile)
        base = os.path.splitext(base)[0]
        prof = self.combo.get_active_text()
        if prof:
            ext = self.profiles[prof].get("container", "mkv")
            outfile = os.path.join(self.output_dir, f"{base}_converted.{ext}")
            self.entry_out.set_text(outfile)

    def update_profile_combo(self):
        self.combo.remove_all()
        for k in sorted(self.profiles.keys()):
            self.combo.append_text(k)
        if self.combo.get_model():
            self.combo.set_active(0)

    def on_profile_changed(self, combo):
        self.update_output_path()

    def show_ffmpeg_error(self):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=LANGS[self.lang]["ffmpeg_error"]
        )
        dialog.run()
        dialog.destroy()
        Gtk.main_quit()

    def on_browse(self, button):
        dlg = Gtk.FileChooserDialog(title=LANGS[self.lang]["browse"], parent=self, action=Gtk.FileChooserAction.OPEN)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if dlg.run() == Gtk.ResponseType.OK:
            self.entry_in.set_text(dlg.get_filename())
            self.update_output_path()
        dlg.destroy()

    def on_browse_out_dir(self, button):
        dlg = Gtk.FileChooserDialog(title=LANGS[self.lang]["select_output_dir"], parent=self, action=Gtk.FileChooserAction.SELECT_FOLDER)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if dlg.run() == Gtk.ResponseType.OK:
            self.output_dir = dlg.get_filename()
            self.entry_out_dir.set_text(self.output_dir)
            self.update_output_path()
            self.prefs["output_dir"] = self.output_dir
            save_prefs(self.prefs)
        dlg.destroy()

    def on_presets(self, button):
        dlg = PresetDialog(self, self.profiles, self.lang)
        resp = dlg.run()
        if resp == Gtk.ResponseType.OK:
            self.profiles = dlg.get_profiles()
            self.update_profile_combo()
            self.prefs["profiles"] = self.profiles
            save_prefs(self.prefs)
        dlg.destroy()

    def on_export_profiles(self, button):
        dlg = Gtk.FileChooserDialog(title=LANGS[self.lang]["export"], parent=self, action=Gtk.FileChooserAction.SAVE)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        if dlg.run() == Gtk.ResponseType.OK:
            path = dlg.get_filename()
            if not path.endswith(".json"):
                path += ".json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.profiles, f, ensure_ascii=False, indent=2)
            self.append_log(LANGS[self.lang]["export"] + ": " + path, "success")
        dlg.destroy()

    def on_import_profiles(self, button):
        dlg = Gtk.FileChooserDialog(title=LANGS[self.lang]["import"], parent=self, action=Gtk.FileChooserAction.OPEN)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if dlg.run() == Gtk.ResponseType.OK:
            path = dlg.get_filename()
            try:
                with open(path, "r", encoding="utf-8") as f:
                    imported_profiles = json.load(f)
                self.profiles.update(imported_profiles)
                self.update_profile_combo()
                self.prefs["profiles"] = self.profiles
                save_prefs(self.prefs)
                self.append_log(LANGS[self.lang]["import"] + ": " + path, "success")
            except Exception as e:
                self.append_log(LANGS[self.lang]["conversion_error"].format(error=e), "error")
        dlg.destroy()

    def on_lang_changed(self, combo):
        new_lang = combo.get_active_text()
        if new_lang == self.lang:
            return
        self.lang = new_lang
        self.prefs["lang"] = self.lang
        save_prefs(self.prefs)
        Gtk.main_quit()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def on_threads_changed(self, spin):
        new_threads = self.spin_threads.get_value_as_int()
        self.max_threads = new_threads
        self.prefs["max_threads"] = self.max_threads
        save_prefs(self.prefs)
        self.append_log(LANGS[self.lang]["max_threads"] + ": " + str(self.max_threads))

    def on_convert(self, button):
        infile = self.entry_in.get_text().strip()
        outfile = self.entry_out.get_text().strip()
        prof_name = self.combo.get_active_text()
        if not prof_name:
            self.append_log(LANGS[self.lang]["profile_not_selected"], "error")
            return
        prof = self.profiles[prof_name]
        if not infile or not os.path.isfile(infile):
            self.append_log(LANGS[self.lang]["input_file_not_selected"], "error")
            return
        self._conversion_completed = False
        threading.Thread(target=self.run_ffmpeg, args=(infile, outfile, prof, None), daemon=True).start()

    def run_ffmpeg(self, infile, outfile, prof, queue_idx):
        try:
            input_ext = os.path.splitext(infile)[1][1:].lower()
            container = prof.get("container", "mkv")

            input_width, input_height = get_video_resolution(infile)
            target_width = prof.get("width", 0)
            target_height = prof.get("height", 0)

            if input_ext == container and input_width == target_width and input_height == target_height:
                self.append_log(
                    LANGS[self.lang]["no_conversion_needed"].format(input_ext=input_ext, profile_name=container),
                    "warning"
                )
                return

            args = ["ffmpeg", "-y" if self.check_overwrite.get_active() else "-n", "-i", infile]

            if self.trim_enabled:
                trim_start = self.entry_trim_start.get_text().strip()
                trim_end = self.entry_trim_end.get_text().strip()

                def parse_time(time_str):
                    if not time_str:
                        return None
                    if ':' in time_str:
                        try:
                            minutes, seconds = map(float, time_str.split(':'))
                            return minutes * 60 + seconds
                        except:
                            return None
                    else:
                        try:
                            return float(time_str)
                        except:
                            return None

                start_seconds = parse_time(trim_start)
                end_seconds = parse_time(trim_end)

                if start_seconds is not None and start_seconds > 0:
                    args += ["-ss", str(start_seconds)]
                if end_seconds is not None and end_seconds > 0:
                    args += ["-to", str(end_seconds)]

            if prof.get("vcodec") and prof["vcodec"] != "copy":
                args += ["-c:v", prof["vcodec"]]
                if "video_bitrate" in prof:
                    args += ["-b:v", prof["video_bitrate"]]
                if "width" in prof and "height" in prof:
                    if prof.get("container") == "mp4" and target_width == 720 and target_height == 1280:
                        args += [
                            "-vf",
                            f"scale=-1:{prof['height']}:force_original_aspect_ratio=increase,crop={prof['width']}:{prof['height']}:ceil((in_w-out_w)/2):0"
                        ]
                    elif prof.get("container") == "mp4" and target_width == 1080 and target_height == 1080:
                        args += [
                            "-vf",
                            "scale='if(gt(a,1),1080,-1)':'if(gt(a,1),-1,1080)',pad=1080:1080:(ow-iw)/2:(oh-ih)/2:color=black"
                        ]
                    else:
                        args += [
                            "-vf",
                            f"scale={prof['width']}:{prof['height']}"
                        ]
                if prof.get("pix_fmt"):
                    args += ["-pix_fmt", prof["pix_fmt"]]
                if prof["vcodec"] == "libaom-av1":
                    if "cpu_used" in prof:
                        args += ["-cpu-used", prof["cpu_used"]]
                    if "threads" in prof:
                        args += ["-threads", prof["threads"]]
                if prof["vcodec"] in ("libx264", "libx265", "h264_nvenc", "hevc_nvenc", "h264_qsv"):
                    if "preset" in prof:
                        args += ["-preset", prof["preset"]]
                    if "profile" in prof:
                        args += ["-profile:v", prof["profile"]]
                    if "crf" in prof:
                        args += ["-crf", str(prof["crf"])]
                if prof["vcodec"].startswith("libvpx"):
                    args += ["-crf", str(prof.get("crf", 30)), "-b:v", "0"]
                if prof.get("fps"):
                    args += ["-r", str(prof["fps"])]
            else:
                if prof.get("vcodec") is None:
                    args += ["-vn"]
                else:
                    args += ["-c:v", "copy"]

            if prof.get("acodec") and prof["acodec"] != "copy":
                args += ["-c:a", prof["acodec"]]
                if prof.get("audio_bitrate"):
                    args += ["-b:a", prof["audio_bitrate"]]
                if prof["acodec"] == "dca":
                    args += ["-strict", "-2"]
                if prof["acodec"] == "libopencore_amrnb":
                    args += ["-ar", "8000", "-ac", "1"]
            else:
                args += ["-c:a", "copy"]

            if prof.get("movflags"):
                args += ["-movflags", prof["movflags"]]

            if container:
                outpath = os.path.splitext(outfile)[0] + f".{container}"
            else:
                outpath = outfile
            cmd = args + [outpath]
            GLib.idle_add(self.append_log, LANGS[self.lang]["convert"] + ": " + " ".join(shlex.quote(p) for p in cmd))

            self._ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                preexec_fn=os.setsid
            )

            while True:
                if self._stop:
                    self._ffmpeg_process.send_signal(signal.SIGSTOP)
                    GLib.idle_add(self.append_log, LANGS[self.lang]["conversion_paused"])
                    while self._stop:
                        time.sleep(0.1)
                    self._ffmpeg_process.send_signal(signal.SIGCONT)
                    GLib.idle_add(self.append_log, LANGS[self.lang]["conversion_resumed"])

                line = self._ffmpeg_process.stderr.readline()
                if not line and self._ffmpeg_process.poll() is not None:
                    break
                if line:
                    if "time=" in line:
                        try:
                            time_str = line.split("time=")[1].split()[0]
                            h, m, s = time_str.split(":")
                            total_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                            if "Duration" in line:
                                duration_str = line.split("Duration: ")[1].split(",")[0]
                                h, m, s = duration_str.split(":")
                                duration = int(h) * 3600 + int(m) * 60 + float(s)
                                progress = total_seconds / duration
                        except Exception as e:
                            pass
                    GLib.idle_add(self.append_log, line.rstrip())

            self._ffmpeg_process.wait()
            if self._ffmpeg_process.returncode == 0 and not self._conversion_completed:
                self._conversion_completed = True
                GLib.idle_add(
                    self.append_log,
                    LANGS[self.lang]["conversion_complete"].format(filename=os.path.basename(outpath)),
                    "success"
                )
            elif self._ffmpeg_process.returncode != 0:
                GLib.idle_add(self.append_log, LANGS[self.lang]["conversion_error"].format(error=self._ffmpeg_process.returncode), "error")

        except Exception as e:
            GLib.idle_add(self.append_log, LANGS[self.lang]["conversion_error"].format(error=e), "error")

    def on_preview(self, button):
        infile = self.entry_in.get_text().strip()
        if not infile or not os.path.isfile(infile):
            self.append_log(LANGS[self.lang]["input_file_not_selected"], "error")
            return

        infile = os.path.abspath(infile)
        self.append_log(LANGS[self.lang]["preview"] + ": " + os.path.basename(infile))

        if self.try_vlc_preview(infile):
            return

        if self.try_gstreamer_preview(infile):
            return

        self.append_log(LANGS[self.lang]["gstreamer_not_available"], "error")

    def try_vlc_preview(self, infile):
        try:
            result = subprocess.run(["which", "vlc"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                self.append_log(LANGS[self.lang]["using_vlc"])
                subprocess.Popen(["vlc", infile])
                return True
            else:
                self.append_log(LANGS[self.lang]["vlc_not_found"], "warning")
                return False
        except Exception as e:
            self.append_log(LANGS[self.lang]["conversion_error"].format(error=e), "error")
            return False

    def try_gstreamer_preview(self, infile):
        try:
            if hasattr(self, 'playbin'):
                self.playbin.set_state(Gst.State.NULL)

            self.playbin = Gst.ElementFactory.make("playbin", "player")
            if not self.playbin:
                self.append_log(LANGS[self.lang]["gstreamer_not_available"], "warning")
                return False

            self.playbin.set_property("uri", f"file://{infile}")

            bus = self.playbin.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_gst_message)

            self.playbin.set_state(Gst.State.PLAYING)
            self.append_log(LANGS[self.lang]["using_gstreamer"])
            return True
        except Exception as e:
            self.append_log(LANGS[self.lang]["gstreamer_error"].format(error=e), "error")
            return False

    def on_gst_message(self, bus, message):
        if message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            error_message = err.message
            if "Output window was closed" not in error_message and "Internal data stream error" not in error_message:
                self.append_log(LANGS[self.lang]["playback_error"].format(error=error_message), "error")
            self.playbin.set_state(Gst.State.NULL)
        elif message.type == Gst.MessageType.EOS:
            self.append_log(LANGS[self.lang]["playback_finished"])
            self.playbin.set_state(Gst.State.NULL)

    def on_pause(self, button):
        if self._ffmpeg_process and self._ffmpeg_process.poll() is None:
            self._stop = True
            self._ffmpeg_process.send_signal(signal.SIGSTOP)
            self.append_log(LANGS[self.lang]["conversion_paused"])
        else:
            self.append_log(LANGS[self.lang]["process_not_found"], "warning")

    def on_resume(self, button):
        if self._ffmpeg_process and self._ffmpeg_process.poll() is None:
            self._stop = False
            self._ffmpeg_process.send_signal(signal.SIGCONT)
            self.append_log(LANGS[self.lang]["conversion_resumed"])
        elif self._conversion_completed:
            self.append_log(LANGS[self.lang]["conversion_already_finished"], "warning")
        else:
            self.append_log(LANGS[self.lang]["process_not_found"], "warning")

    def on_drag_data_received_input(self, widget, drag_context, x, y, data, info, time):
        uris = data.get_uris()
        for u in uris:
            path = GLib.filename_from_uri(u)[0]
            if os.path.isfile(path):
                self.entry_in.set_text(path)
                self.update_output_path()
        drag_context.finish(True, False, time)

class PresetDialog(Gtk.Dialog):
    def __init__(self, parent, profiles, lang):
        super().__init__(title=LANGS[lang]["preset_mgr"], transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_default_size(600, 500)
        self.profiles = profiles
        if not self.profiles:
            self.profiles = EXTENDED_PROFILES
        self.lang = lang

        box = self.get_content_area()
        if box is None:
            raise RuntimeError("Failed to get content area")

        self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView(model=self.liststore)
        renderer = Gtk.CellRendererText()
        col_name = Gtk.TreeViewColumn("Название", renderer, text=0)
        self.treeview.append_column(col_name)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.treeview)
        box.pack_start(scrolled_window, True, True, 0)

        for name in sorted(self.profiles.keys()):
            self.liststore.append([name])

        button_box = Gtk.Box(spacing=6)
        btn_add = Gtk.Button(label="Добавить")
        btn_add.connect("clicked", self.on_add_preset)
        btn_edit = Gtk.Button(label="Редактировать")
        btn_edit.connect("clicked", self.on_edit_preset)
        btn_remove = Gtk.Button(label="Удалить")
        btn_remove.connect("clicked", self.on_remove_preset)

        button_box.pack_start(btn_add, True, True, 0)
        button_box.pack_start(btn_edit, True, True, 0)
        button_box.pack_start(btn_remove, True, True, 0)
        box.pack_start(button_box, False, False, 0)

        self.show_all()

    def on_add_preset(self, button):
        dialog = Gtk.Dialog(title="Добавить параметры", transient_for=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)

        box = dialog.get_content_area()
        grid = Gtk.Grid(column_spacing=6, row_spacing=6)

        lbl_name = Gtk.Label(label="Название:")
        entry_name = Gtk.Entry()

        grid.attach(lbl_name, 0, 0, 1, 1)
        grid.attach(entry_name, 1, 0, 1, 1)

        box.pack_start(grid, True, True, 0)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = entry_name.get_text().strip()
            if name:
                self.profiles[name] = EXTENDED_PROFILES.get(name, EXTENDED_PROFILES["MP4 720p (H.264)"])
                self.liststore.append([name])

        dialog.destroy()

    def on_edit_preset(self, button):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter is None:
            return

        name = model.get_value(iter, 0)
        params = self.profiles[name]

        dialog = Gtk.Dialog(title=f"Редактировать параметры: {name}", transient_for=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)

        box = dialog.get_content_area()
        grid = Gtk.Grid(column_spacing=6, row_spacing=6)

        lbl_vcodec = Gtk.Label(label="Видеокодек:")
        entry_vcodec = Gtk.Entry(text=params.get("vcodec", ""))
        lbl_acodec = Gtk.Label(label="Аудиокодек:")
        entry_acodec = Gtk.Entry(text=params.get("acodec", ""))
        lbl_width = Gtk.Label(label="Ширина:")
        entry_width = Gtk.Entry(text=str(params.get("width", "")))
        lbl_height = Gtk.Label(label="Высота:")
        entry_height = Gtk.Entry(text=str(params.get("height", "")))
        lbl_video_bitrate = Gtk.Label(label="Видеобитрейт:")
        entry_video_bitrate = Gtk.Entry(text=params.get("video_bitrate", ""))
        lbl_audio_bitrate = Gtk.Label(label="Аудиобитрейт:")
        entry_audio_bitrate = Gtk.Entry(text=params.get("audio_bitrate", ""))
        lbl_pix_fmt = Gtk.Label(label="Формат пикселей:")
        entry_pix_fmt = Gtk.Entry(text=params.get("pix_fmt", ""))
        lbl_container = Gtk.Label(label="Контейнер:")
        entry_container = Gtk.Entry(text=params.get("container", ""))
        lbl_crf = Gtk.Label(label="CRF (качество, 0-51):")
        entry_crf = Gtk.Entry(text=str(params.get("crf", 23)))
        lbl_preset = Gtk.Label(label="Пресет:")
        entry_preset = Gtk.Entry(text=params.get("preset", "medium"))
        lbl_profile = Gtk.Label(label="Профиль:")
        entry_profile = Gtk.Entry(text=params.get("profile", ""))

        grid.attach(lbl_vcodec, 0, 0, 1, 1)
        grid.attach(entry_vcodec, 1, 0, 1, 1)
        grid.attach(lbl_acodec, 0, 1, 1, 1)
        grid.attach(entry_acodec, 1, 1, 1, 1)
        grid.attach(lbl_width, 0, 2, 1, 1)
        grid.attach(entry_width, 1, 2, 1, 1)
        grid.attach(lbl_height, 0, 3, 1, 1)
        grid.attach(entry_height, 1, 3, 1, 1)
        grid.attach(lbl_video_bitrate, 0, 4, 1, 1)
        grid.attach(entry_video_bitrate, 1, 4, 1, 1)
        grid.attach(lbl_audio_bitrate, 0, 5, 1, 1)
        grid.attach(entry_audio_bitrate, 1, 5, 1, 1)
        grid.attach(lbl_pix_fmt, 0, 6, 1, 1)
        grid.attach(entry_pix_fmt, 1, 6, 1, 1)
        grid.attach(lbl_container, 0, 7, 1, 1)
        grid.attach(entry_container, 1, 7, 1, 1)
        grid.attach(lbl_crf, 0, 8, 1, 1)
        grid.attach(entry_crf, 1, 8, 1, 1)
        grid.attach(lbl_preset, 0, 9, 1, 1)
        grid.attach(entry_preset, 1, 9, 1, 1)
        grid.attach(lbl_profile, 0, 10, 1, 1)
        grid.attach(entry_profile, 1, 10, 1, 1)

        box.pack_start(grid, True, True, 0)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            params["vcodec"] = entry_vcodec.get_text().strip()
            params["acodec"] = entry_acodec.get_text().strip()
            params["width"] = int(entry_width.get_text().strip()) if entry_width.get_text().strip() else None
            params["height"] = int(entry_height.get_text().strip()) if entry_height.get_text().strip() else None
            params["video_bitrate"] = entry_video_bitrate.get_text().strip()
            params["audio_bitrate"] = entry_audio_bitrate.get_text().strip()
            params["pix_fmt"] = entry_pix_fmt.get_text().strip()
            params["container"] = entry_container.get_text().strip()
            params["crf"] = int(entry_crf.get_text().strip()) if entry_crf.get_text().strip() else 23
            params["preset"] = entry_preset.get_text().strip()
            params["profile"] = entry_profile.get_text().strip()

        dialog.destroy()

    def on_remove_preset(self, button):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter is not None:
            name = model.get_value(iter, 0)
            del self.profiles[name]
            model.remove(iter)

    def get_profiles(self):
        return self.profiles

def main():
    ensure_convert_dir()
    win = ConverterWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
