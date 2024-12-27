# Final Project: Python for Data Analysis

## Table of Contents
- [Overview](#Overview)
- [Installation](#Installation)
- [Usage](#Usage)
- [Tests](#Tests)
- [Contributors](#Contributors)

## Overview
The goal of this project is computing the Bollinger Bands of a specified cryptocurrency pair and use that information to automate buy and sell signals. Data containing prices and volumes along time is obtanied via Krakenex API.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/eduardo-miralles/pad-final-project.git
   ```
2. Install poetry:
   ```bash
   sudo apt install python3-poetry
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```
4. To use poetry's virtual environment with the required dependencies, run:
   ```bash
   poetry shell
   ```

## Usage
1. To start the application run:
   ```bash
   python -m pad_final_project
   ```
   and make sure you have a browser installed.
2. To terminate the app, type `ctrl + C` on the command line.

## Tests
Run tests with the following command:
```bash
pytest --cov
```

## Contributors
- Eduardo Miralles [emirallesiz@alumni.unav.es](mailto:emirallesiz@alumni.unav.es)