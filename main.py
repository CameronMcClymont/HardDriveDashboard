import subprocess

from notion import Notion
from drive import Drive


def get_connected_drives() -> set[Drive]:
    result = subprocess.run(['diskutil', 'list', 'external', 'physical'], capture_output=True, text=True)
    drives = result.stdout.split('\n')[2:]
    return {Drive(driveInfo.strip()) for driveInfo in drives if driveInfo != ''}


def main():
    notion = Notion()
    notion_page_id = notion.search_for_page("Hard Drive Dashboard")
    notion_blocks = notion.get_all_blocks(notion_page_id)

    if notion_page_id is None:
        print("Couldn't find your Notion page! Make sure it's named 'Hard Drive Dashboard' and try again")
        return

    for drive in get_connected_drives():
        print(f'Detected drive: {drive}')
        if len(drive.list_folders()) == 0:
            print('No root folders, skipping...')
            continue

        block_id = drive.get_block_id(notion_blocks)
        if block_id is None:
            notion.append_drive_info(notion_page_id, drive)
        else:
            notion.update_drive_info(block_id, drive)


if __name__ == "__main__":
    main()
