import os
import sys
import shutil
import hashlib
import time

class FolderSynchronizer:
    def __init__(self, source_folder, replica_folder, log_file, sync_interval):
        self.source_folder = source_folder
        self.replica_folder = replica_folder
        self.log_file = log_file
        self.sync_interval = sync_interval

    def synchronize_folders(self):
        '''
        :return: None. Create Replica folder if not available already.
        '''
        if not os.path.exists(self.replica_folder):
            os.makedirs(self.replica_folder)
            self.log_event(f"Created {self.replica_folder} folder")

        #Continuosly runs script and at regular interval of time calls sync_directories method
        while True:
            self.sync_directories(self.source_folder, self.replica_folder)
            time.sleep(self.sync_interval)

    def sync_directories(self, source_dir, replica_dir):
        '''
        :param source_dir: Source folder path
        :param replica_dir: Destination Folder Path
        :return: None. Adds/Updates files/Directories from source folders which are not present/updated to Replica folder
        '''
        for file in os.listdir(source_dir):
            source_path = os.path.join(source_dir, file)
            replica_path = os.path.join(replica_dir, file)
            if os.path.isfile(source_path):
                if not os.path.exists(replica_path) or self.get_file_checksum(source_path) != self.get_file_checksum(replica_path):
                    shutil.copy2(source_path, replica_path)
                    self.log_event(f'Copied: {source_path} to {replica_path}')
            elif os.path.isdir(source_path):
                if not os.path.exists(replica_path):
                    os.makedirs(replica_path)
                    self.log_event(f'Created directory: {replica_path}')
                self.sync_directories(source_path, replica_path)

        self.remove_extra_items(source_dir, replica_dir)

    def remove_extra_items(self, source_dir, replica_dir):
        '''
        :param source_dir: Source Folder path
        :param replica_dir: Replica Folder path
        :return: None. Deletes files/Directories in Replica folder which are not available on Source Folder
        '''
        for replica_item in os.listdir(replica_dir):
            replica_item_path = os.path.join(replica_dir, replica_item)
            source_item_path = os.path.join(source_dir, replica_item)
            if not os.path.exists(source_item_path):
                if os.path.isfile(replica_item_path):
                    os.remove(replica_item_path)
                    self.log_event(f'Removed file: {replica_item_path}')
                elif os.path.isdir(replica_item_path):
                    shutil.rmtree(replica_item_path)
                    self.log_event(f'Removed directory: {replica_item_path}')

    def get_file_checksum(self, file_path):
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def log_event(self, event):
        with open(self.log_file, 'a') as f:
            f.write(event + '\n')
        print(event)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage: python sync_folders.py <source_folder> <replica_folder> <sync_interval> <log_file>')
        sys.exit(1)

    source_folder = sys.argv[1]
    replica_folder = sys.argv[2]
    sync_interval = int(sys.argv[3])
    log_file = sys.argv[4]

    synchronizer = FolderSynchronizer(source_folder, replica_folder, log_file, sync_interval)
    synchronizer.synchronize_folders()

###Command to Run in Terminal --> python synchronization.py Source Replica 20 output.log
