import math
import os
import shutil
import subprocess

from folder import Folder


class Drive:
    def __init__(self, driveInfo: str):
        # Extract the drive ID from a string that looks like:
        # 0:    Microsoft Basic Data Berry's HD5     *2.0 TB     disk12
        self.id = driveInfo.split()[-1]
        self.name = [value.strip() for value in driveInfo.split('  ') if value != ''][1]

    def __str__(self):
        return self.name

    @staticmethod
    def format_bytes(b: int) -> str:
        index = math.floor(math.log(b, 1000))
        return str(round(b / (1000 ** index), 1)) + ['B', 'KB', 'MB', 'GB', 'TB'][index]

    def get_mount_point(self) -> str | None:
        result = subprocess.run(['diskutil', 'info', self.id], capture_output=True, text=True)
        lines = result.stdout.split('\n')

        for line in lines:
            if 'Mount Point' in line:
                return line.split(': ')[1].strip()

        print(f'Failed to get mount point for drive: {self.name}')
        return None

    def list_folders(self) -> list[Folder]:
        mount_point = self.get_mount_point()
        if mount_point is None:
            return []

        folders = []
        for folder in os.listdir(mount_point):
            folder_path = os.path.join(mount_point, folder)
            if os.path.isdir(folder_path) and not folder.startswith('.'):
                try:
                    subfolders = []
                    for subfolder in os.listdir(folder_path):
                        subfolder_path = os.path.join(folder_path, subfolder)
                        if os.path.isdir(subfolder_path) and not subfolder.startswith('.'):
                            num_items = len(os.listdir(subfolder_path))
                            subfolders.append(Folder(subfolder, num_items, []))

                    folders.append(Folder(folder, len(os.listdir(folder_path)), subfolders))
                except PermissionError:
                    # Handle directories that cannot be accessed due to permissions
                    folders.append(f"{folder} (Permission Denied)")
                except Exception as e:
                    # Handle other potential errors
                    folders.append(f"{folder} (Error: {e})")

        return folders

    def get_storage_info(self) -> dict[str, int] | None:
        mount_point = self.get_mount_point()

        try:
            total, used, free = shutil.disk_usage(mount_point)
            return {
                "total": total,
                "used": used,
                "free": free
            }
        except FileNotFoundError:
            print(f"Drive {self} not found.")
        except PermissionError:
            print(f"No permission to access disk usage for drive: {self}")
        except Exception as e:
            print(f"Error accessing drive {self}: {e}")

        return None

    def get_block_id(self, all_blocks) -> str | None:
        for block in all_blocks:
            if block.get("type") == "paragraph":
                try:
                    text: str = block['paragraph']['rich_text'][1]['text']['content']
                    if text == f'{self.name}\n':
                        return block['id']
                except IndexError:
                    pass

        return None

    def format_heading(self) -> dict:
        return {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": self.name,
                },
            }],
        }

    def format_body(self) -> dict:
        storage = self.get_storage_info()
        return {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Name: ",
                    },
                    "annotations": {
                        "bold": True,
                    },
                },
                {
                    "type": "text",
                    "text": {
                        "content": f"{self.name}\n",
                    },
                },
                {
                    "type": "text",
                    "text": {
                        "content": "ID: ",
                    },
                    "annotations": {
                        "bold": True,
                    },
                },
                {
                    "type": "text",
                    "text": {
                        "content": f"{self.id}\n",
                    },
                },
                {
                    "type": "text",
                    "text": {
                        "content": "Storage: ",
                    },
                    "annotations": {
                        "bold": True,
                    },
                },
                {
                    "type": "text",
                    "text": {
                        "content": '?\n' if storage is None else f"{Drive.format_bytes(storage['free'])} free / {Drive.format_bytes(storage['total'])} total\n",
                    },
                },
                {
                    "type": "text",
                    "text": {
                        "content": "Folders:\n",
                    },
                    "annotations": {
                        "bold": True,
                    },
                },
                {
                    "type": "text",
                    "text": {
                        "content": '\n'.join([folder.format() for folder in self.list_folders()]),
                    },
                },
            ],
        }
