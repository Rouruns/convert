# convert
Многоязычный конвертер видео/аудио с поддержкой предпросмотра, паузы и возобновления конвертации.

Этот инструмент позволяет конвертировать видео и аудио файлы в различные форматы с использованием **FFmpeg**. Поддерживаются функции:
- Конвертация в популярные форматы (MP4, MKV, WebM, AVI, 3GP и др.).
- Предпросмотр видео перед конвертацией (через VLC или GStreamer).
- Пауза и возобновление процесса конвертации.
- Обрезка видео по времени.
- Поддержка нескольких языков интерфейса (Английский, Белорусский, Немецкий, Русский, Украинский).
- Экспорт и импорт пользовательских профилей.

Поддерживаемые форматы

 Видео
   Формат                     | Кодек видео          | Кодек аудио  | Разрешение       |
 |----------------------------|----------------------|--------------|------------------|
 | 3GP (176x144)              | H.263                | AAC          | 176x144          |
 | 3GP (320x240)              | H.263                | AAC          | 320x240          |
 | MP4 (360p)                 | H.264                | AAC          | 640x360          |
 | MP4 (480p)                 | H.264                | AAC          | 854x480          |
 | MP4 (720p)                 | H.264                | AAC          | 1280x720         |
 | MP4 (1080p)                | H.264                | AAC          | 1920x1080        |
 | MP4 (4K)                   | H.264                | AAC          | 3840x2160        |
 | WebM (VP8/VP9)             | VP8/VP9              | Vorbis/Opus  | 640x360, 1280x720, 1920x1080 |
 | AVI (DivX)                 | MPEG4                | MP3          | 640x480, 720x480, 1920x1080 |
 | MKV (H.264/H.265)          | H.264/H.265          | AAC          | 640x360, 1280x720, 1920x1080, 3840x2160 |
 | Apple ProRes               | ProRes               | PCM          | 1280x720, 1920x1080 |
 | GIF                        | GIF                  | -            | 320x240, 640x480  |
 | MPEG-1/MPEG-2              | MPEG1/MPEG2          | MP2          | 352x288, 720x576  |

 Аудио
 | Формат
 |--------------|
 | MP3 
 | AAC
 | FLAC
 | OGG
 | WAV
 | AC3
 | Opus


#Требования

- **Python 3.6+**
- **PyGObject** (для GTK3)
- **FFmpeg** (для конвертации)
- **GStreamer** (для предпросмотра)
- **VLC** (опционально, для предпросмотра)

## Зависимости:

 python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 ffmpeg gstreamer1.0-plugins-good vlc

### Установка

#### Linux (Debian/Ubuntu)

   sudo apt update
   sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 ffmpeg gstreamer1.0-plugins-good vlc

##### Запуск:

python3 convert_multilang.py

###### Использование

Выберите входной файл.
Выберите профиль конвертации.
Укажите выходной файл или папку.
Нажмите "Конвертировать".
Используйте "Пауза" и "Возобновить", чтобы управлять процессом.
Для предпросмотра нажмите "Предпросмотр".

####### Настройки

Язык интерфейса: можно изменить в выпадающем списке.
Максимальное количество потоков: настройте для ускорения конвертации.
Обрезка видео: укажите начало и конец (в секундах или формате MM:SS).
Экспорт/импорт профилей: сохраните свои настройки для повторного использования.

######## Контакты

Email: dierman77@macaw.me
GitHub: Rouruns

######### Лицензия
Данный проект распространяется по лицензии в соответствии с [Custom Free Non-Commercial License](LICENSE).


------------------------------------------------------------------------------------------------------

En

# Video/Audio Converter with Preview

Multilingual video/audio converter with preview, pause, and resume support.

![Screenshot](screenshot.png)

---

## Description

This tool allows you to convert video and audio files into various formats using **FFmpeg**. Features include:
- Conversion to popular formats (MP4, MKV, WebM, AVI, 3GP, etc.).
- Video preview before conversion (via VLC or GStreamer).
- Pause and resume conversion process.
- Video trimming by time.
- Multilingual interface support (Belarusian, German, English, Russian, Ukrainian,).
- Export and import custom profiles.

---

## Supported Formats

### Video
   Format                     | Video Codec          | Audio Codec  | Resolution       |
 |----------------------------|----------------------|--------------|------------------|
 | 3GP (176x144)              | H.263                | AAC          | 176x144          |
 | 3GP (320x240)              | H.263                | AAC          | 320x240          |
 | MP4 (360p)                 | H.264                | AAC          | 640x360          |
 | MP4 (480p)                 | H.264                | AAC          | 854x480          |
 | MP4 (720p)                 | H.264                | AAC          | 1280x720         |
 | MP4 (1080p)                | H.264                | AAC          | 1920x1080        |
 | MP4 (4K)                   | H.264                | AAC          | 3840x2160        |
 | WebM (VP8/VP9)             | VP8/VP9              | Vorbis/Opus  | 640x360, 1280x720, 1920x1080 |
 | AVI (DivX)                 | MPEG4                | MP3          | 640x480, 720x480, 1920x1080 |
 | MKV (H.264/H.265)          | H.264/H.265          | AAC          | 640x360, 1280x720, 1920x1080, 3840x2160 |
 | Apple ProRes               | ProRes               | PCM          | 1280x720, 1920x1080 |
 | GIF                        | GIF                  | -            | 320x240, 640x480  |
 | MPEG-1/MPEG-2              | MPEG1/MPEG2          | MP2          | 352x288, 720x576  |

### Audio
 | Format 
 |---------
 | MP3
 | AAC
 | FLAC
 | OGG
 | WAV
 | AC3
 | Opus

---

### Requirements

- **Python 3.6+**
- **PyGObject** (for GTK3)
- **FFmpeg** (for conversion)
- **GStreamer** (for preview)
- **VLC** (optional, for preview)

---

#### Dependencies

python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 ffmpeg gstreamer1.0-plugins-good vlc


##### Installation
Linux (Debian/Ubuntu)

sudo apt update
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 ffmpeg gstreamer1.0-plugins-good vlc


###### Run:

python3 convert_multilang.py

####### Clone the repository:

git clone https://github.com/Rouruns/video-converter.git
cd video-converter


######## Usage

Select an input file.
Choose a conversion profile.
Specify the output file or folder.
Click "Convert".
Use "Pause" and "Resume" to control the process.
For preview, click "Preview".

######### Settings

Interface language: Change in the dropdown menu.
Maximum threads: Adjust for faster conversion.
Video trimming: Specify start and end (in seconds or MM:SS format).
Export/import profiles: Save your settings for reuse.

########## License
This project is licensed under the [Custom Free Non-Commercial License](LICENSE).

########### Contact

Email: dierman77@macaw.me
GitHub: Rouruns
