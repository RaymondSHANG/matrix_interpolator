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