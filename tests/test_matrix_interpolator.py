import pytest
import numpy as np
import pandas as pd
import os
from src.matrix_interpolator import read_matrix, interpolate_matrix, write_matrix
from numpy.testing import assert_array_almost_equal


# Define paths for test files
TEST_INPUT_CSV = "mytest_data.csv"
TEST_OUTPUT_CSV = "interpolated_mytest_data.csv"
NON_EXISTENT_FILE = "non_existent.csv"
INVALID_CSV = "invalid.csv"
EMPTY_CSV = "empty.csv"

# --- Helper Functions for Tests ---
def read_csv_to_numpy(file_path):
    """Helper to read a CSV into a numpy array for comparison."""
    df = pd.read_csv(file_path, header=None, na_values=['nan'])
    return df.to_numpy()

# --- Fixtures ---
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Fixture to ensure test files are cleaned up after each test."""
    yield
    # Cleanup logic executed after the test runs
    if os.path.exists(TEST_INPUT_CSV):
        os.remove(TEST_INPUT_CSV)
    if os.path.exists(TEST_OUTPUT_CSV):
        os.remove(TEST_OUTPUT_CSV)
    if os.path.exists(INVALID_CSV):
        os.remove(INVALID_CSV)
    if os.path.exists(EMPTY_CSV):
        os.remove(EMPTY_CSV)

def create_csv_file(file_path, content):
    """Helper to create a CSV file with given content."""
    with open(file_path, 'w') as f:
        f.write(content)

# --- Unit Tests for read_matrix ---
def test_read_matrix_valid_csv():
    """Test reading a valid CSV with and without nan."""
    content = "1.0,2.0,nan\n4.0,5.0,6.0"
    create_csv_file(TEST_INPUT_CSV, content)
    matrix = read_matrix(TEST_INPUT_CSV)
    expected = pd.read_csv(TEST_INPUT_CSV, header=None, na_values=['nan']).to_numpy()
    assert np.array_equal(matrix, expected, equal_nan=True)


def test_read_matrix_non_existent_file():
    """Test reading from a file that does not exist."""
    with pytest.raises(FileNotFoundError):
        read_matrix(NON_EXISTENT_FILE)

def test_read_matrix_invalid_format():
    """Test reading a CSV with non-numeric data."""
    content = "a,2.0,3.0\n4.0,5.0,6.0"
    create_csv_file(INVALID_CSV, content)
    with pytest.raises(ValueError, match="Error reading or parsing CSV file"):
        read_matrix(INVALID_CSV)

def test_read_matrix_empty_csv():
    """Test reading an empty CSV file."""
    create_csv_file(EMPTY_CSV, "")
    with pytest.raises(ValueError, match="Error reading or parsing CSV file"):
        # pandas read_csv will raise an error for truly empty files
        read_matrix(EMPTY_CSV)

def test_read_matrix_empty_but_valid_csv():
    """Test reading a CSV with just newlines or empty cells."""
    content = "\n\n" # pandas might interpret this as 0x0 or error
    create_csv_file(EMPTY_CSV, content)
    with pytest.raises(ValueError): # Should ideally raise value error due to inability to parse to float matrix
        read_matrix(EMPTY_CSV)

# --- Unit Tests for interpolate_matrix ---
def test_interpolate_matrix_basic_interpolation():
    """Test a simple case with one nan."""
    matrix = np.array([[1.0, 2.0], [np.nan, 4.0]])
    interpolated = interpolate_matrix(matrix)
    # Neighbor of [1,0] is [0,0]=1.0 and [1,1]=4.0. Average = (1.0+4.0)/2 = 2.5
    # Corrected expected array: [0,1] should remain 2.0, not become 2.5
    expected = np.array([[1.0, 2.0], [2.5, 4.0]])
    # Use assert_array_almost_equal for float comparisons, no 'assert' keyword needed
    assert_array_almost_equal(interpolated, expected, decimal=2)

def test_interpolate_matrix_basic_interpolation():
    """Test a simple case with one nan."""
    matrix = np.array([[1.0, 2.0], [np.nan, 4.0]])
    interpolated = interpolate_matrix(matrix)
    print(interpolated)
    # Neighbor of [1,0] is [0,0]=1.0 and [1,1]=4.0. Average = (1.0+4.0)/2 = 2.5
    expected = np.array([[1.0, 2.0], [2.5, 4.0]]) # Corrected expected value for [1,0]
    # Use assert_array_almost_equal for float comparisons, no 'assert' keyword needed
    assert_array_almost_equal(interpolated, expected, decimal=6)

def test_interpolate_matrix_edge_cases():
    """Test interpolation at corners and edges."""
    matrix = np.array([
        [np.nan, 2.0, 3.0],
        [4.0, np.nan, 6.0],
        [7.0, 8.0, np.nan]
    ])
    interpolated = interpolate_matrix(matrix)
    # [0,0] nan: Neighbors [0,1]=2.0, [1,0]=4.0. Avg = (2.0+4.0)/2 = 3.0
    # [1,1] nan: Neighbors [0,1]=2.0, [1,0]=4.0, [1,2]=6.0, [2,1]=8.0. Avg = (2.0+4.0+6.0+8.0)/4 = 5.0
    # [2,2] nan: Neighbors [1,2]=6.0, [2,1]=8.0. Avg = (6.0+8.0)/2 = 7.0
    expected = np.array([
        [3.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 7.0]
    ])
    assert_array_almost_equal(interpolated, expected, decimal=6)

def test_interpolate_matrix_no_missing_values():
    """Test matrix with no NaNs."""
    matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
    interpolated = interpolate_matrix(matrix)
    # Use assert_array_almost_equal for float comparisons (even if exact), no 'assert' keyword needed
    assert_array_almost_equal(interpolated, matrix, decimal=6)

def test_interpolate_matrix_all_missing_values():
    """Test matrix where all values are NaNs."""
    matrix = np.array([[np.nan, np.nan], [np.nan, np.nan]])
    interpolated = interpolate_matrix(matrix)
    # If all values are NaN, global_mean becomes 0.0, so all should be 0.0
    expected = np.array([[0.0, 0.0], [0.0, 0.0]])
    # Use assert_array_almost_equal for float comparisons, no 'assert' keyword needed
    assert_array_almost_equal(interpolated, expected, decimal=6)

def test_interpolate_matrix_isolated_nan_with_no_valid_neighbors():
    """Test a nan surrounded by other NaNs, falling back to global mean."""
    matrix = np.array([
        [1.0, np.nan, 3.0],
        [np.nan, np.nan, np.nan],
        [7.0, np.nan, 9.0]
    ])
    # Global mean of non-NaNs: (1+3+7+9)/4 = 20/4 = 5.0
    interpolated = interpolate_matrix(matrix)
    expected = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ])
    # Use assert_array_almost_equal for float comparisons, no 'assert' keyword needed
    assert_array_almost_equal(interpolated, expected, decimal=6)

# --- Unit Tests for write_matrix ---
def test_write_matrix_valid_output():
    """Test writing a matrix to CSV."""
    matrix = np.array([[1.0, 2.5], [3.0, 4.0]])
    create_csv_file(TEST_INPUT_CSV, "dummy") # Create a dummy file for the fixture
    write_matrix(matrix, TEST_OUTPUT_CSV)
    # Read the output CSV back and compare
    # For direct string content comparison, np.array_equal is not suitable
    # We'll stick to direct content check or use np.testing.assert_array_almost_equal
    # if we re-read and convert to array for comparison.
    expected_content = "1.0,2.5\n3.0,4.0\n"
    with open(TEST_OUTPUT_CSV, 'r') as f:
        actual_content = f.read()
    assert actual_content == expected_content

def test_write_matrix_io_error():
    """Test writing to a protected or invalid path."""
    matrix = np.array([[1.0, 2.0]])
    # Simulate a permission error by trying to write to a directory name
    if os.path.exists("temp_dir_for_test"):
        os.rmdir("temp_dir_for_test")
    os.mkdir("temp_dir_for_test")
    invalid_path = os.path.join("temp_dir_for_test", "sub_dir", "file.csv") # Invalid path structure
    with pytest.raises(IOError, match="Error writing matrix to CSV file"):
        write_matrix(matrix, invalid_path)
    os.rmdir("temp_dir_for_test") # Clean up the created directory