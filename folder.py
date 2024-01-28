class Folder:
    def __init__(self, name: str, num_items: int, subfolders: list):
        self.name = name
        self.num_items = num_items
        self.subfolders = subfolders

    def format(self) -> str:
        formatted = f'- {self.name} ({self.num_items})'

        for subfolder in self.subfolders:
            formatted += f'\n    {subfolder.format()}'

        return formatted
