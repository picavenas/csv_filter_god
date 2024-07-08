import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Configuración de la página
st.set_page_config(page_title='CSV Filter G.O.D')

# Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Llama a la función para cargar el CSS personalizado
local_css("style.css")

def filter_users(data, filters):
    # Función para filtrar usuarios basado en los filtros seleccionados
    filtered_data = data.copy()
    for column, filter_info in filters.items():
        if filter_info['values'] and column in filtered_data.columns:
            filtered_data[column] = filtered_data[column].str.lower()
            filtered_data[column] = filtered_data[column].fillna("")
            
            if filter_info['type'] == 'is':
                filter_pattern = '|'.join([value.lower() for value in filter_info['values']])
                mask = filtered_data[column].str.contains(filter_pattern, regex=True)
            elif filter_info['type'] == 'is_not':
                filter_pattern = '|'.join([value.lower() for value in filter_info['values']])
                mask = ~filtered_data[column].str.contains(filter_pattern, regex=True)
            
            # Aplicar el filtro
            filtered_data = filtered_data[mask]
    
    return filtered_data

def plot_filtered_data(original_user_count, filtered_user_count):
    # Función para graficar el porcentaje de usuarios filtrados
    if original_user_count == 0:
        st.warning("No original users found. Unable to calculate percentage.")
        return
    
    percentage_filtered = (filtered_user_count / original_user_count) * 100
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar('Filtered Users', percentage_filtered, color='green', label=f'Percentage of Filtered Users: {percentage_filtered:.2f}%')
    ax.set_ylabel('Percentage of Total Users (%)')
    ax.set_ylim(0, 100)
    ax.set_title('Percentage of Filtered Users Relative to Total', color='green')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# Contenido de la aplicación
st.title('CSV Filter G.O.D')

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file is not None:
    st.session_state['uploaded'] = True
    data = pd.read_csv(uploaded_file)
    st.success("CSV file successfully uploaded!")
    st.write("Preview of the loaded data:", data.head())

    valid_columns = data.columns.tolist()
    selected_columns = st.multiselect("Select the columns to filter:", valid_columns)

    filters = {}
    for column in selected_columns:
        filter_type = st.radio(f"Filter type for '{column}':", ('is', 'is_not'))
        filter_input = st.text_area(f"Enter values for '{column}' separated by commas:")
        if filter_input:
            filter_values = [value.strip() for value in filter_input.split(',')]
            filters[column] = {'type': filter_type, 'values': filter_values}

    if st.button("Apply filters"):
        try:
            filtered_data = filter_users(data, filters)
            st.success("Data successfully filtered!")
            st.write("Preview of the filtered data:", filtered_data.head())

            original_user_count = data.shape[0]  # Total de filas en el archivo original
            filtered_user_count = filtered_data.shape[0]  # Total de filas en el archivo filtrado

            # Mostrar el número total de registros y registros filtrados
            st.write(f"Total records: {original_user_count}")
            st.write(f"Filtered records: {filtered_user_count}")

            plot_filtered_data(original_user_count, filtered_user_count)

            # Descargar archivos
            csv = filtered_data.to_csv(index=False)
            b64_csv = base64.b64encode(csv.encode()).decode()
            st.markdown(f'<a href="data:file/csv;base64,{b64_csv}" download="filtered_users.csv">Download CSV file</a>', unsafe_allow_html=True)

        except KeyError as e:
            st.error(f"KeyError: {e}. Please check your selected columns and try again.")

# Mostrar GIF solo si no se ha subido un archivo CSV
if 'uploaded' not in st.session_state:
    st.session_state['uploaded'] = False

if not st.session_state['uploaded']:
    gif_path = "kangaroo_animation.gif"  # Reemplaza con la ruta de tu archivo GIF
    try:
        st.image(gif_path, use_column_width=True)
    except Exception as e:
        st.error(f"Error displaying GIF: {e}")
