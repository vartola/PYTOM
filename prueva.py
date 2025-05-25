import os, io, base64
from flask import Flask, request, render_template_string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Configuración inicial de Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crea la carpeta si no existe

# Ruta principal del servidor
@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    error = None

    if request.method == 'POST':
        try:
            # Recuperar archivo y parámetros del formulario
            file = request.files.get('excel_file')
            column = request.form.get('column')
            mean_input = request.form.get('mean')
            std_input = request.form.get('std')

            # Validaciones básicas
            if not file or file.filename == '':
                error = "No se ha subido ningún archivo."
                return render_template_string(HTML_TEMPLATE, error=error)

            if not column:
                error = "Debes indicar el nombre de la columna a analizar."
                return render_template_string(HTML_TEMPLATE, error=error)

            # Leer archivo Excel
            df = pd.read_excel(file)
            if column not in df.columns:
                error = f"La columna '{column}' no existe en el archivo."
                return render_template_string(HTML_TEMPLATE, error=error)

            # Convertir la columna a datos numéricos
            data = pd.to_numeric(df[column], errors='coerce').dropna()
            if data.empty:
                error = f"La columna '{column}' no contiene datos numéricos válidos."
                return render_template_string(HTML_TEMPLATE, error=error)

            # Calcular estadísticas de los datos
            mu = data.mean()
            sigma = data.std()

            # Usar los parámetros ingresados o por defecto
            ref_mu = float(mean_input) if mean_input else mu
            ref_sigma = float(std_input) if std_input else sigma
            if ref_sigma <= 0:
                error = "La desviación estándar de referencia debe ser mayor que cero."
                return render_template_string(HTML_TEMPLATE, error=error)

            # Crear gráfico
            plt.figure(figsize=(10, 6))
            plt.hist(data, bins=30, density=True, alpha=0.5, label='Datos', color='skyblue')

            # Intervalo x
            x = np.linspace(data.min(), data.max(), 100)

            # Curva normal de los datos
            plt.plot(x, norm.pdf(x, mu, sigma), 'k-', lw=2, label=f'Datos (μ={mu:.2f}, σ={sigma:.2f})')

            # Curva normal de referencia
            plt.plot(x, norm.pdf(x, ref_mu, ref_sigma), 'r--', lw=2, label=f'Referencia (μ={ref_mu:.2f}, σ={ref_sigma:.2f})')

            plt.title('Distribución de Datos vs Curva Normal de Referencia')
            plt.xlabel(column)
            plt.ylabel('Densidad')
            plt.legend()
            plt.grid(True)

            # Guardar imagen en memoria y convertir a base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plot_url = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()

        except Exception as e:
            error = f"Ocurrió un error al procesar los datos: {e}"

    # Renderizar HTML con imagen o error
    return render_template_string(HTML_TEMPLATE, plot_url=plot_url, error=error)

# Iniciar la app
if __name__ == '__main__':
    app.run(debug=True)

