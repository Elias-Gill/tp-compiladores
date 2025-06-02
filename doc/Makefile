# Configuración
MAIN = main
OUT_DIR = out

# Compilación principal
all: dirs compile move_pdf

# Crear directorio de salida
dirs:
	mkdir -p $(OUT_DIR)

# Compilar (LaTeX + BibTeX + LaTeX x2)
compile:
	pdflatex -output-directory=$(OUT_DIR) $(MAIN).tex
	#
	# ----- Si usas BibTeX: -------
	# cp $(OUT_DIR)/$(MAIN).aux .  # Copia temporalmente el .aux al directorio raíz
	# bibtex $(MAIN)               # Ejecuta BibTeX
	#
	# mv $(MAIN).bbl $(MAIN).blg $(OUT_DIR)/  # Mueve los archivos de BibTeX a out/
	# rm $(MAIN).aux               # Limpia el .aux temporal
	#
	# Recompila para resolver referencias
	# pdflatex -output-directory=$(OUT_DIR) $(MAIN).tex
	# pdflatex -output-directory=$(OUT_DIR) $(MAIN).tex

# Mover el PDF al directorio raíz (opcional)
move_pdf:
	cp $(OUT_DIR)/$(MAIN).pdf ./informe.pdf

# Limpiar archivos temporales
clean:
	rm -rf $(OUT_DIR)
	rm -f $(MAIN).pdf
