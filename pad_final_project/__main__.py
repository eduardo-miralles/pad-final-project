import subprocess


def main():
    bash_command = "streamlit run pad_final_project/streamlit_app.py"

    try:
        # Execute the command and capture the output
        subprocess.run(
            bash_command, shell=True, check=True, text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Stderr: {e.stderr}")

if __name__ == "__main__":
    main()