# Package Measurement Conversion API

## Summary

This API converts encoded measurement strings into a list of total inflow values for each package. The encoding follows these rules:
- Lowercase alphabetical characters: "a" = 1, "b" = 2, … "z" = 26.
- For numbers higher than 26, multiple concatenated characters are added together.
- A package measurement cycle consists of a leading count followed by that many measurement values. If a package begins with a sequence of "z"s, these are processed as a chain to represent a number.

## Features

- **Conversion Endpoint:**  
  GET `/convert-measurements?input=<measurement_string>`  
  Example: `/convert-measurements?input=abbcc` returns `[2, 6]`.

- **History Endpoint:**  
  GET `/history` returns a JSON array of stored input sequences and their processed outputs in plaintext.

- **Custom Port Support:**  
  Run the application on a custom port by passing the port as a command-line argument. For example:
  ```
  python main_app.py 8888
  ```
  runs the API on port 8888.

- **Logging:**  
  Log statements provide runtime visibility of key application events.

## Prerequisites

- Python 3.8+
- pip

## Setup & Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/Package-Measurement-Conversion.git
    cd Package-Measurement-Conversion
    ```

2. **Create a Virtual Environment (Optional – Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate    # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies:**

    Make sure the following packages are installed:
    - FastAPI
    - uvicorn
    - logging (standard library)
    
    You can install FastAPI and uvicorn by running:
    
    ```bash
    pip install fastapi uvicorn
    ```

4. **Run the Application:**

    To launch on the default port (8080):
    
    ```bash
    python main_app.py
    ```
    
    Or, to launch on a custom port (e.g., 8888):
    
    ```bash
    python main_app.py 8888
    ```

## API Usage Examples

- **Convert Measurements:**

  **Request:**
  ```
  GET http://localhost:8080/convert-measurements?input=za_a_a_a_a_a_a_a_a_a_a_a_a_azaaa
  ```
  
  **Expected Response:**
  ```json
  {
      "processed": [40, 1],
      "sequence": "za_a_a_a_a_a_a_a_a_a_a_a_a_azaaa"
  }
  ```

- **Get History:**

  **Request:**
  ```
  GET http://localhost:8080/history
  ```

  **Expected Response:**
  ```json
  {
      "history": [
          {
              "id": 1,
              "sequence": "za_a_a_a_a_a_a_a_a_a_a_a_a_azaaa",
              "processed": [40, 1],
              "timestamp": "2025-04-23 08:27:32"
          },
          ...
      ]
  }
  ```

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push the branch: `git push origin feature/my-feature`
5. Open a pull request.

## License

This project is licensed under the MIT License.