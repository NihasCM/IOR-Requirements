from flask import Flask, jsonify, send_from_directory, request
import pandas as pd

app = Flask(__name__)

# Define file paths for switching
file_paths = {
    "file1": "C:/Users/Nihas/Desktop/data/test file.xlsx",
    "file2": "C:/Users/Nihas/Desktop/data/Arista-KZ-Short-MPL 2025.02.14.xlsx"
}

# Define sheet names for each file
sheet_names = {
    "file1": "Sheet",  # Sheet name for file1
    "file2": "KZ list "  # Sheet name for file2 (with trailing space)
}

# Function to load data from the selected file
def load_data(file_key):
    if file_key not in file_paths:
        return None

    file_path = file_paths[file_key]
    if file_key == "file1":
        data = pd.read_excel(file_path, sheet_name=sheet_names["file1"])
    elif file_key == "file2":
        data = pd.read_excel(file_path, sheet_name=sheet_names["file2"])

    # Normalize column names
    data.columns = data.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # Replace NaN values with "No Data Found"
    data.fillna("No Data Found", inplace=True)  # Replacing NaN values with a string

    return data

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/data', methods=['GET'])
def get_data():
    return "<tr><td colspan='6' class='text-center p-4'>General data is not displayed. Please use the search functionality.</td></tr>"

@app.route('/global_search', methods=['GET'])
def global_search():
    part_number = request.args.get('part_number', '').strip()  # Normalize input
    selected_file = request.args.get('selected_file', 'file1')  # Get selected file


    data = load_data(selected_file)  # Load data based on selected file


    if data is None or not part_number:

        return "<tr><td colspan='6' class='text-center p-4'>No results found</td></tr>"

    required_columns = ['Model#', 'Part Number', 'Weight', 'COO', 'Description', 'OEM Name']
    filtered_data = data[data['Part Number'] == part_number][required_columns].copy()
    filtered_data.columns = ['Model#', 'Part Number', 'Net Weight (kgs)', 'COO', 'Product Description (RU)', 'OEM Name']


    if filtered_data.empty:

        return "<tr><td colspan='6' class='text-center p-4'>No results found</td></tr>"  # No results message

    filtered_data.fillna("No Data Found", inplace=True)

    tbody_content = filtered_data.to_html(index=False, header=False).split('<tbody>')[1].split('</tbody>')[0]


    return tbody_content


@app.route('/compliance', methods=['GET'])
def get_compliance_data():
    part_number = request.args.get('part_number', '').strip()  # Normalize input
    compliance_columns = ['HS code (KZ)', 'ECCN']

    file_key = request.args.get('file', 'file1')
    data = load_data(file_key)

    if data is None:
        return "<tr><td colspan='6' class='text-center p-4'>No data found</td></tr>"

    if part_number:
        compliance_data = data[data['Part Number'] == part_number][[*compliance_columns, 'Part Number']].copy()
    else:
        compliance_data = data[[*compliance_columns, 'Part Number']].copy()  # Return all data if no part number is provided

    compliance_data.fillna("No Data Found", inplace=True)

    if compliance_data.empty:
        return "<tr><td colspan='6' class='text-center p-4'>No results found</td></tr>"  # No results message

    html_data = compliance_data.to_html(index=False, header=False)
    tbody_content = html_data.split('<tbody>')[1].split('</tbody>')[0]
    return tbody_content

@app.route('/licenses', methods=['GET'])
def get_licenses_data():
    part_number = request.args.get('part_number', '').strip()  # Normalize input
    licenses_columns = ['MIC License','MIC conclusion', 'ISP License (IMPORT)', 'ISP license (EXPORT)', 'OIP', 'DoC / CoC', 'CNS Conclusion', 'Encryption Notification','ISP conclusion (IMPORT)','ISP conclusion (EXPORT)','Shipping approval by PN']

    file_key = request.args.get('file', 'file1')
    data = load_data(file_key)

    if data is None:
        return "<tr><td colspan='6' class='text-center p-4'>No data found</td></tr>"

    if part_number:
        licenses_data = data[data['Part Number'] == part_number][[*licenses_columns, 'Part Number']].copy()
    else:
        licenses_data = data[[*licenses_columns, 'Part Number']].copy()  # Return all data if no part number is provided

    licenses_data.fillna("No Data Found", inplace=True)

    if licenses_data.empty:
        return "<tr><td colspan='6' class='text-center p-4'>No results found</td></tr>"  # No results message

    html_data = licenses_data.to_html(index=False, header=False)
    tbody_content = html_data.split('<tbody>')[1].split('</tbody>')[0]
    return tbody_content

if __name__ == '__main__':
    app.run(debug=True)
