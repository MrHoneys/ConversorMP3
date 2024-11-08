from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os
import threading
import urllib.parse

app = Flask(__name__)

# Pasta onde os arquivos temporários serão armazenados
TEMP_DIR = 'downloads'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Função para buscar informações do vídeo (nome da música, duração, plataforma)
def get_video_info(url):
    # Usando yt-dlp para pegar informações do vídeo
    ydl_opts = {
        'quiet': True,
        'force_generic_extractor': True,
        'extractaudio': True,
        'audioquality': 1,
        'outtmpl': TEMP_DIR + '/%(id)s.%(ext)s'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get('title', 'Título não disponível')
        duration = info_dict.get('duration', 0)
        duration_minutes = duration // 60
        duration_seconds = duration % 60
        platform = "YouTube"  # No caso, sempre será o YouTube

    return {
        'title': title,
        'duration': f'{duration_minutes:02}:{duration_seconds:02}',
        'platform': platform
    }

# Função para baixar a música e salvar no servidor
def baixar_musica(url, formato, progress_callback):
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
        }
    elif formato == "mp4":
        opcoes = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_callback],
        }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        print(f"Baixando: {url}")
        ydl.download([url])

# Função de progresso para o download
def progresso_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percent = (downloaded_bytes / total_bytes) * 100 if total_bytes > 0 else 0
        print(f"Baixando: {percent:.2f}%")

# Função para servir o arquivo para download
@app.route('/baixar_arquivo/<filename>')
def baixar_arquivo(filename):
    try:
        # Decodifica a URL para garantir que os espaços e caracteres especiais sejam tratados corretamente
        filename = urllib.parse.unquote(filename)
        return send_from_directory(TEMP_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"status": "erro", "message": "Arquivo não encontrado."})

# Função para excluir arquivos antigos após o download
def limpar_arquivos():
    for file in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Arquivo excluído: {file}")
        except Exception as e:
            print(f"Erro ao excluir {file}: {str(e)}")

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para buscar informações da música
@app.route('/buscar', methods=['POST'])
def buscar():
    url = request.form.get('url')
    if url:
        video_info = get_video_info(url)
        return jsonify(video_info)
    return jsonify({"error": "URL não fornecida"})

# Rota para baixar a música
@app.route('/baixar', methods=['POST'])
def baixar():
    urls = request.form['urls']
    formato = request.form['formato']  # Formato escolhido pelo usuário
    urls = urls.splitlines()  # Divide as URLs separadas por linha

    if not urls:
        return jsonify({"status": "erro", "message": "Nenhuma URL fornecida!"})

    # Criar uma thread para cada download para processar as URLs em paralelo
    threads = []
    for url in urls:
        if url.strip():  # Ignora URLs vazias
            thread = threading.Thread(target=baixar_musica, args=(url.strip(), formato, progresso_hook))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()  # Aguarda o término de todos os downloads

    # Retornar a lista de links para o cliente baixar
    files = os.listdir(TEMP_DIR)

    return jsonify({"status": "sucesso", "message": "Músicas baixadas com sucesso!", "files": files})

# Endpoint para limpar arquivos manualmente (quando o usuário clicar no botão "Limpar")
@app.route('/limpar', methods=['POST'])
def limpar():
    limpar_arquivos()  # Limpa os arquivos da pasta TEMP_DIR
    return jsonify({"status": "sucesso", "message": "Arquivos excluídos com sucesso!"})

# Iniciar a aplicação Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
