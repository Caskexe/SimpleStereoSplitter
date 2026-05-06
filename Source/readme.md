Requirements:
 - pip install pydub tk
 - pip install pydub tkinterdnd2
 - ffmpeg must be installed for pydub to handle formats like
   mp3/ogg/flac

Compiling into an executable:
    pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." SimpleStereoSplitter.py
