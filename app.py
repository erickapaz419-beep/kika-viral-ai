import os
import subprocess
from flask import Flask, render_template, request, send_from_directory
import imageio_ffmpeg
import yt_dlp

app = Flask(__name__)

PASTA_VIDEOS = os.path.join(os.getcwd(), "videos_limpos")
os.makedirs(PASTA_VIDEOS, exist_ok=True)


def limpar_metadados(arquivo_entrada, arquivo_saida):
  """Remove 100% dos metadados e rastros do arquivo de vídeo"""
  ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
  comando = [
      ffmpeg_exe,
      "-y",
      "-i",
      arquivo_entrada,
      "-map_metadata",
      "-1",
      "-c:v",
      "copy",
      "-c:a",
      "copy",
      arquivo_saida,
  ]
  subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@app.route("/", methods=["GET", "POST"])
def home():
  resultado = None
  erro = None
  link_inserido = ""

  if request.method == "POST":
    link_inserido = request.form.get("link_video", "").strip()

    if not link_inserido:
      erro = "Por favor, cole o link do vídeo."
    else:
      try:
        temp_video = os.path.join(PASTA_VIDEOS, "temp_bruto.mp4")
        video_final = os.path.join(PASTA_VIDEOS, "video_kika_limpo.mp4")

        for arq in [temp_video, video_final]:
          if os.path.exists(arq):
            os.remove(arq)

        # CONFIGURAÇÃO DE MÁXIMA QUALIDADE (FULL HD / MELHOR RESOLUÇÃO)
        opcoes = {
            "outtmpl": temp_video,
            "format": (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            ),
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(opcoes) as ydl:
          info = ydl.extract_info(link_inserido, download=True)
          titulo = info.get("title", "Vídeo de Achadinho")

        limpar_metadados(temp_video, video_final)
        if os.path.exists(temp_video):
          os.remove(temp_video)

        resultado = {"titulo": titulo, "arquivo": "video_kika_limpo.mp4"}

      except Exception as e:
        erro = (
            "Não foi possível baixar este link. Verifique se o vídeo é público"
            f" e válido. (Detalhe: {str(e)})"
        )

  return render_template(
      "index.html", resultado=resultado, erro=erro, link_video=link_inserido
  )


@app.route("/download/<nome_arquivo>")
def download(nome_arquivo):
  return send_from_directory(PASTA_VIDEOS, nome_arquivo, as_attachment=True)


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)