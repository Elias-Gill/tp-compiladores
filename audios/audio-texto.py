import whisper

model = whisper.load_model("medium") 
resultado = model.transcribe("prueba-texto1-negativo.m4a")

print(resultado["text"])
