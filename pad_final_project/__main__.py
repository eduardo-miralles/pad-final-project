import subprocess
import os
import sys


def main():

    try:
        if os.path.exists("pad_final_project/streamlit_app.py"):
            # Case: Running from cloned repo
            app_path = "pad_final_project/streamlit_app.py"
        else:
            # Case: Running from installed package
            try:
                # Dynamically find the installed package path
                import pad_final_project
                app_path = os.path.join(os.path.dirname(pad_final_project.__file__), "streamlit_app.py")
            except ImportError:
                print("Could not locate the Streamlit app.")
                sys.exit(1)

        # Execute the Streamlit app using the resolved path
        bash_command = f"streamlit run {app_path}"
        # Execute the command and capture the output
        subprocess.run(
            bash_command, shell = True, check = True, text = True
        )
    except KeyboardInterrupt:
        pass
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Stderr: {e.stderr}")

if __name__ == "__main__":
    main()