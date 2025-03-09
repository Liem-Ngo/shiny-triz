import json

def read_csv_file(filename):
    """Read the CSV-like file and parse it into a matrix."""
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    # Skip the header row (line with semicolons)
    data_rows = lines[1:]
    
    # Parse each row, skipping the first column (which appears to be an index)
    matrix = []
    for row in data_rows:
        cells = row.split(';')[1:]  # Skip the first column
        parsed_row = []
        for cell in cells:
            if cell == "0" or cell == "":
                parsed_row.append([])
            else:
                parsed_row.append([int(num) for num in cell.split(',')])
        matrix.append(parsed_row)
    
    return matrix

def create_json_matrix(csv_matrix):
    """
    Transform the CSV matrix into the JSON format.
    Based on analysis, two operations are needed:
    1. Transpose the matrix (swap rows and columns)
    2. For each row r in the transposed matrix, apply a circular shift to the right by (r+1) positions
    """
    rows = len(csv_matrix)
    cols = max(len(row) for row in csv_matrix)
    
    # Step 1: Create a transposed matrix
    transposed = []
    for c in range(cols):
        new_row = []
        for r in range(rows):
            if c < len(csv_matrix[r]):
                new_row.append(csv_matrix[r][c])
            else:
                new_row.append([])  # Handle missing values at the end of rows
        transposed.append(new_row)
    
    # Step 2: Apply a circular shift to each row in the transposed matrix
    json_matrix = []
    for r in range(len(transposed)):
        shifted_row = [[] for _ in range(len(transposed[r]))]
        for c in range(len(transposed[r])):
            new_c = (c + r + 1) % len(transposed[r])
            shifted_row[new_c] = transposed[r][c]
        json_matrix.append(shifted_row)
    
    return json_matrix

def main():
    # Replace with your input and output file paths
    csv_file = "triz_39_1.csv"
    json_file = "output.json"
    
    # Read and parse the CSV file
    csv_matrix = read_csv_file(csv_file)
    
    # Transform to JSON format
    json_matrix = create_json_matrix(csv_matrix)
    
    # Write to JSON file
    with open(json_file, 'w') as file:
        json.dump(json_matrix, file, indent=4)
    
    print(f"Conversion complete. JSON file written to {json_file}")

if __name__ == "__main__":
    main()