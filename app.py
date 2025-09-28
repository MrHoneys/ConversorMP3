from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os
import threading
import urllib.parse
import traceback
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

app = Flask(__name__)

# Pasta onde os arquivos temporários serão armazenados
TEMP_DIR = 'downloads'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

LOG_FILE = 'log_erros.txt'
console = Console()

# Função para log de erros
def log_erro(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    console.print(f"[bold red]Erro:[/bold red] {msg}")

# Função para buscar informações do vídeo
def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'force_generic_extractor': True,
        'extractaudio': True,
        'audioquality': 1,
        'outtmpl': TEMP_DIR + '/%(id)s.%(ext)s',
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'Título não disponível')
            duration = info_dict.get('duration', 0)
            duration_minutes = duration // 60
            duration_seconds = duration % 60
            platform = "YouTube"
        return {
            'title': title,
            'duration': f'{duration_minutes:02}:{duration_seconds:02}',
            'platform': platform
        }
    except Exception as e:
        log_erro("Erro ao buscar informações do vídeo:\n" + traceback.format_exc())
        raise

# Função de progresso para o download usando Rich
def progresso_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percent = (downloaded_bytes / total_bytes) * 100 if total_bytes > 0 else 0
        console.print(f"[cyan]Baixando:[/cyan] {d.get('filename', 'arquivo')} [yellow]{percent:.2f}%[/yellow]", end='\r')

# Função para baixar a música
def baixar_musica(url, formato, progress_callback):
    try:
        if formato == "mp3":
            opcoes = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_callback],
                'noplaylist': True,
            }
        elif formato == "mp4":
            opcoes = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_callback],
                'noplaylist': True,
            }

        with yt_dlp.YoutubeDL(opcoes) as ydl:
            console.print(f"[green]Iniciando download:[/green] {url}")
            ydl.download([url])
            console.print(f"[bold green]Download concluído:[/bold green] {url}\n")
    except Exception as e:
        log_erro("Erro ao baixar vídeo/música:\n" + traceback.format_exc())

# Função para servir o arquivo para download
@app.route('/baixar_arquivo/<filename>')
def baixar_arquivo(filename):
    try:
        filename = urllib.parse.unquote(filename)
        return send_from_directory(TEMP_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"status": "erro", "message": "Arquivo não encontrado."})

# Função para excluir arquivos antigos
def limpar_arquivos():
    for file in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                console.print(f"[magenta]Arquivo excluído:[/magenta] {file}")
        except Exception as e:
            log_erro(f"Erro ao excluir {file}: {str(e)}")

# Rotas Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    url = request.form.get('url')
    if url:
        try:
            video_info = get_video_info(url)
            return jsonify(video_info)
        except:
            return jsonify({"error": "Erro ao buscar informações, verifique o log."})
    return jsonify({"error": "URL não fornecida"})

@app.route('/baixar', methods=['POST'])
def baixar():
    urls = request.form['urls'].splitlines()
    formato = request.form['formato']

    if not urls:
        return jsonify({"status": "erro", "message": "Nenhuma URL fornecida!"})

    threads = []
    for url in urls:
        if url.strip():
            thread = threading.Thread(target=baixar_musica, args=(url.strip(), formato, progresso_hook))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()

    files = os.listdir(TEMP_DIR)
    console.print("[bold green]Todos os downloads concluídos![/bold green]\n")
    return jsonify({"status": "sucesso", "message": "Músicas baixadas com sucesso!", "files": files})

@app.route('/limpar', methods=['POST'])
def limpar():
    limpar_arquivos()
    return jsonify({"status": "sucesso", "message": "Arquivos excluídos com sucesso!"})

if __name__ == '__main__':
    console.print("[bold blue]Iniciando servidor Flask...[/bold blue]\n")
    app.run(host='0.0.0.0', port=5000, debug=True)