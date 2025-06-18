import pytest
import numpy as np
import pandas as pd
import os
from src.matrix_interpolator import read_matrix, interpolate_matrix


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
    expected = np.array([[1.0, 2.0], [2.5, 4.0]])
    assert np.array_equal(interpolated, expected)