import pandas as pd
import numpy as np
import argparse
import os

def read_matrix(file_path: str) -> np.ndarray:
    """
    Reads a CSV file into a NumPy array, treating 'nan' as actual NaN values.

    Args:
        file_path (str): The path to the input CSV file.

    Returns:
        np.ndarray: A 2D NumPy array representing the matrix, with 'nan' converted to np.nan.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the CSV cannot be parsed into a numeric matrix.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    try:
        # Read CSV, specifying 'nan' as a missing value indicator.
        # dtype=float ensures that all parsed values are numeric.
        df = pd.read_csv(file_path, header=None, na_values=['nan'], dtype=float)
        return df.to_numpy()
    except Exception as e:
        raise ValueError(f"Error reading or parsing CSV file {file_path}: {e}")

def _get_non_diagonal_neighbors(matrix: np.ndarray, r: int, c: int) -> list:
    """
    Collects the non-diagonal (up, down, left, right) neighbors of a cell
    in a 2D matrix.

    Args:
        matrix (np.ndarray): The 2D NumPy array.
        r (int): The row index of the current cell.
        c (int): The column index of the current cell.

    Returns:
        list: A list of values of the non-diagonal neighbors.
    """
    neighbors = []
    rows, cols = matrix.shape

    # Check up
    if r > 0:
        neighbors.append(matrix[r - 1, c])
    # Check down
    if r < rows - 1:
        neighbors.append(matrix[r + 1, c])
    # Check left
    if c > 0:
        neighbors.append(matrix[r, c - 1])
    # Check right
    if c < cols - 1:
        neighbors.append(matrix[r, c + 1])

    return neighbors

def interpolate_matrix(matrix: np.ndarray) -> np.ndarray:
    """
    Interpolates missing values (np.nan) in a 2D NumPy matrix.
    Missing values are replaced by the average of their non-diagonal neighbors.
    If a missing value has no valid non-diagonal neighbors, it is replaced
    by the mean of all non-missing values in the entire matrix. If the entire
    matrix is missing, all values are set to 0.0.

    Args:
        matrix (np.ndarray): The input 2D NumPy array, possibly containing np.nan.

    Returns:
        np.ndarray: A new 2D NumPy array with all missing values interpolated.
    """
    # Create a copy to avoid modifying the original matrix
    interpolated_matrix = np.copy(matrix)
    rows, cols = interpolated_matrix.shape

    # Calculate the mean of all non-missing values in the matrix.
    # This will be used as a fallback for isolated NaNs.
    # If the entire matrix is NaN, this will be NaN, so we handle that case.
    global_mean = np.nanmean(interpolated_matrix)
    if np.isnan(global_mean):
        global_mean = 0.0 # Fallback if the entire matrix is NaN

    # Iterate through each cell in the matrix
    for r in range(rows):
        for c in range(cols):
            if np.isnan(interpolated_matrix[r, c]):
                # Collect non-diagonal neighbors using the new helper function
                neighbors = _get_non_diagonal_neighbors(matrix, r, c)
                
                # Filter out NaN values from neighbors
                valid_neighbors = [n for n in neighbors if not np.isnan(n)]

                if valid_neighbors:
                    # Calculate the average of valid non-diagonal neighbors
                    interpolated_matrix[r, c] = np.mean(valid_neighbors)
                else:
                    # If no valid non-diagonal neighbors, use the global mean
                    interpolated_matrix[r, c] = global_mean
    return interpolated_matrix

def write_matrix(matrix: np.ndarray, file_path: str):
    """
    Writes a NumPy array to a CSV file.

    Args:
        matrix (np.ndarray): The 2D NumPy array to write.
        file_path (str): The path to the output CSV file.
    """
    try:
        # Convert NumPy array back to DataFrame for easy CSV writing
        df = pd.DataFrame(matrix)
        # Write to CSV without header and index, and with desired float format
        # Values that are non-missing in the input should be preserved in the output without change.
        df.to_csv(file_path, header=False, index=False)
    except Exception as e:
        raise IOError(f"Error writing matrix to CSV file {file_path}: {e}")


def main():
    """
    Main function to parse arguments and run the interpolation process.
    """
    parser = argparse.ArgumentParser(
        description="Interpolate missing values in a CSV matrix."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input CSV file containing the matrix."
    )
    # The --output flag. If present, it expects a value (default nargs=1).
    parser.add_argument(
        "--output",
        type=str,
        help="Path to the output CSV file for the interpolated matrix. "
             "If provided, this overrides any positional output filename."
    )

    # Optional positional argument for the output filename.
    # This will capture any argument that isn't a flag or a flag's value.
    parser.add_argument(
        "output_file",
        nargs='?', # Allows 0 or 1 positional argument
        help="Optional positional argument for the output CSV file name. "
             "If provided, and --output flag is not used, this will be the output."
    )

    args = parser.parse_args()

    input_file_path = args.input
    output_file_path = None

    # Determine the output file path based on precedence:
    # 1. Explicit --output flag
    # 2. Positional argument (output_file)
    # 3. Derived from input file name
    if args.output: # Check if --output flag was provided with a value
        output_file_path = args.output
    elif args.output_file: # Check if a positional argument was given
        output_file_path = args.output_file
    else:
        # Construct the derived output filename using the chosen input_file_path
        base_name = os.path.splitext(input_file_path)[0]
        output_file_path = f"{base_name}_interpolated.csv"

    try:
        print(f"Reading matrix from: {input_file_path}")
        input_matrix = read_matrix(input_file_path)
        print("Input matrix read successfully.")

        print("Interpolating missing values...")
        interpolated_matrix = interpolate_matrix(input_matrix)
        print("Interpolation complete.")

        print(f"Writing interpolated matrix to: {output_file_path}")
        write_matrix(interpolated_matrix, output_file_path)
        print("Output matrix written successfully.")

    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()