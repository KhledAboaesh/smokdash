# backup_manager.py
# Handles automatic backup and recovery of data.

import os
import shutil
import datetime
import zipfile

class BackupManager:
    """Manages data backup and recovery."""

    def __init__(self, data_dir='data', backup_dir='backups'):
        """
        Initializes the BackupManager.

        Args:
            data_dir (str): The directory containing the data to be backed up.
            backup_dir (str): The directory where backups will be stored.
        """
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def backup(self):
        """
        Creates a compressed backup of the data directory.

        The backup is a zip file named with the current timestamp.
        """
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        backup_filename = f'backup-{timestamp}.zip'
        backup_path = os.path.join(self.backup_dir, backup_filename)

        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(self.data_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Arcname is the name of the file in the archive.
                        # This avoids storing the full 'data/' path in the zip.
                        arcname = os.path.relpath(file_path, self.data_dir)
                        zipf.write(file_path, arcname)
            print(f"Successfully created backup: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

    def restore(self, backup_path):
        """
        Restores data from a specified backup file.

        This will overwrite the current data in the data directory.

        Args:
            backup_path (str): The full path to the backup zip file.

        Returns:
            bool: True if restore was successful, False otherwise.
        """
        if not os.path.exists(backup_path):
            print(f"Backup file not found: {backup_path}")
            return False

        try:
            # Clear the current data directory
            if os.path.exists(self.data_dir):
                shutil.rmtree(self.data_dir)
            os.makedirs(self.data_dir)

            # Extract the backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.data_dir)
            
            print(f"Successfully restored data from: {backup_path}")
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    def get_backups(self):
        """

        Gets a list of available backup files, sorted by most recent first.

        Returns:
            list: A list of backup file paths.
        """
        try:
            backups = [os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir) if f.endswith('.zip')]
            # Sort by modification time, newest first
            backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return backups
        except Exception as e:
            print(f"Error getting backups: {e}")
            return []

if __name__ == '__main__':
    # Example Usage
    # This part is for testing and will not run when imported.
    
    # Create a dummy data directory and files for testing
    if not os.path.exists('data'):
        os.makedirs('data')
    with open('data/test1.json', 'w') as f:
        f.write('{"key": "value1"}')
    with open('data/test2.json', 'w') as f:
        f.write('{"key": "value2"}')
    
    print("--- Testing BackupManager ---")
    
    # Initialize the manager
    backup_manager = BackupManager(data_dir='data', backup_dir='backups')
    
    # 1. Create a backup
    print("\n1. Creating a backup...")
    backup_file = backup_manager.backup()
    
    # 2. List backups
    print("\n2. Listing available backups...")
    available_backups = backup_manager.get_backups()
    print(f"Found backups: {available_backups}")
    
    # 3. Restore from the backup
    if backup_file:
        print("\n3. Restoring from the created backup...")
        # First, modify the data to see if it gets overwritten
        with open('data/test1.json', 'w') as f:
            f.write('{"key": "modified"}')
        print("Modified 'data/test1.json'.")

        backup_manager.restore(backup_file)
        
        # Verify content of restored file
        with open('data/test1.json', 'r') as f:
            content = f.read()
            print(f"Content of 'data/test1.json' after restore: {content}")
            if 'value1' in content:
                print("Restore successful!")
            else:
                print("Restore failed!")

    # Clean up dummy files and directories
    shutil.rmtree('data')
    if os.path.exists('backups'):
        shutil.rmtree('backups')
    
    print("\n--- Test complete ---")
