# Sistemas de Recomendación de Ofertas Laborales basado en CVs

Este proyecto evalúa distintos enfoques de sistemas de recomendación de ofertas laborales a partir de currículums (CVs). Su propósito es comparar el rendimiento de varios modelos de recomendación y ofrecer conclusiones sobre cuál es más adecuado y por qué.

## 🎯 Objetivo

El trabajo busca resolver una pregunta común en entornos prácticos y académicos:  
**¿Qué modelo utilizar para recomendar ofertas laborales basándose en un CV?**  
Para ello, se formula el problema como una tarea de ranking y se exploran diferentes técnicas, desde enfoques clásicos hasta modelos generativos.

## 📁 Estructura del repositorio

data/
├── raw/ → Datos en crudo (PDFs originales, ofertas)
├── interim/ → Datos preprocesados listos para usar en modelos

reports/ → Rankings finales y resultados por modelo

scripts/ → Scripts de preprocesado, métricas y notebooks de entrenamiento/evaluación


## 🧠 Tecnologías utilizadas

- Extracción y limpieza de texto: `pdfplumber`, `re`, `unicodedata`
- Modelado:
  - TF-IDF + SVM
  - Red neuronal propia (CNN + LSTM + MLP)
  - BETO (transformer en español)
  - SBERT (`hiiamsid/sentence_similarity_spanish_es`)
  - ChatGPT API (modelo `gpt-4o`)
- Evaluación: `scikit-learn`, `scipy`, `pandas`, `matplotlib`

## 🚀 Instrucciones de uso

> ⚠️ Este repositorio no está diseñado como un entorno reproducible completo. El desarrollo se realizó principalmente en Google Colab.

No se incluye un `requirements.txt`. Para explorar los modelos y evaluaciones, puede comenzarse por los notebooks en la carpeta `scripts/`.

## 📊 Evaluación y resultados

Los resultados se guardan en la carpeta `reports/` como archivos `rankings_test_<modelo>.csv`.

Se evalúan los rankings mediante las siguientes métricas:

- **NDCG@4**: Relevancia ponderada por posición
- **MAP@4**: Precisión acumulada
- **Overlap@4**: Coincidencia entre top-4 de distintos modelos
- **Kendall-τ / Spearman-ρ**: Correlación entre rankings completos

Para visualizar comparaciones y análisis, consulta `evaluation_notebook.ipynb`.

## 🔒 Protección de datos

> ⚠️ Por motivos de privacidad, **los CVs reales utilizados en la evaluación no están incluidos en este repositorio**.

Se han ignorado en `.gitignore` y se recomienda mantenerlos fuera del control de versiones.

## 👤 Autoría

- **Autor**: Pablo Téllez López  
- **Tutor**: Bernardo Ronquillo Japón  
- **Universidad**: Universidad Loyola Andalucía  

---