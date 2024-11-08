# Conversor MP3

Uma aplicação simples para conversão de áudio para o formato MP3. Basta inserir o link do áudio ou vídeo desejado, e o conversor fará o download e conversão automaticamente, totalmente grátis!

## Funcionalidades

- **Conversão rápida e gratuita** para o formato MP3.
- **Interface Web** intuitiva para fácil uso, criada com Flask.
- **Conversão de alta qualidade** com a biblioteca FFmpeg.
  
## Tecnologias Utilizadas

- **Python**: Linguagem principal do projeto para lidar com a lógica de conversão e integração do backend.
- **Flask**: Framework web utilizado para criar a interface e endpoints HTTP.
- **FFmpeg**: Biblioteca poderosa para processamento e conversão de áudio e vídeo.

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/MrHoneys/ConversorMP3.git
   cd conversor-mp3 ```
2. Crie um ambiente virtual e instale as dependências:

```bash
python3 -m venv venv
source venv/bin/activate   # No Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```
3. Certifique-se de que o FFmpeg está instalado e acessível no PATH. Para instalar o FFmpeg:
```bash
No Linux: sudo apt install ffmpeg
```

No Windows: Baixe o executável do [site oficial do FFmpeg](https://www.ffmpeg.org/)


Uso
----
Inicie o servidor Flask:

python app.py

Acesse http://127.0.0.1:5000 no seu navegador.

Insira o link do vídeo/áudio desejado e inicie a conversão para MP3.

Contribuições
--------------
Contribuições são bem-vindas! Sinta-se à vontade para abrir pull requests com melhorias ou correções. 
Também é possível relatar problemas na aba Issues para ajudar a melhorar o projeto.

Licença
-------
Este projeto está licenciado sob a licença MIT - consulte o arquivo LICENSE para mais detalhes.


**Imagem**
![1](https://github.com/user-attachments/assets/44ab46e3-9810-4e98-8867-6fa1b33fe7f0)
![02](https://github.com/user-attachments/assets/ab91ddaa-cae8-4b74-b4fd-7542cd0bac84)
