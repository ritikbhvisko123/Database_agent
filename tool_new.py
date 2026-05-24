    @mcp.tool()
    def open_local_media_file(file_path: str) -> str:
        """Open a local image, video, or audio file using the default Windows system application.
        
        Provide the absolute, full path to the file (e.g., 'C:\\Users\\Username\\Videos\\edit_clip.mp4').
        """
        import os
        import platform

        # Clear any accidental enclosing quotes the LLM or user might pass
        clean_path = file_path.strip("'\"")

        # Basic validation: Check if the file exists on your local drive
        if not os.path.exists(clean_path):
            return f"Error: The system could not find the file at path: '{clean_path}'. Please check the path and try again."

        # Verify the file isn't a directory
        if os.path.isdir(clean_path):
            return f"Error: The path '{clean_path}' is a folder directory, not a specific media file."

        try:
            # Check for Windows system environment
            if platform.system() == "Windows":
                # os.startfile acts exactly like double-clicking the file in Windows File Explorer
                os.startfile(clean_path)
                return f"Successfully sent open signal. Windows is opening the file: '{os.path.basename(clean_path)}'"
            
            # Fallbacks for macOS and Linux just in case you switch environments later
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open '{clean_path}'")
                return f"Successfully opened file on macOS: '{os.path.basename(clean_path)}'"
            else:  # Linux distributions
                os.system(f"xdg-open '{clean_path}'")
                return f"Successfully opened file on Linux: '{os.path.basename(clean_path)}'"

        except Exception as e:
            return f"An operational error occurred while trying to open the file: {str(e)}"