import requests

import secrets
from drive import Drive


class Notion:
    def __init__(self):
        auth_token = secrets.auth_token
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_all_blocks(self, page_id: str):
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('results', [])
        return []

    def search_for_page(self, page_title: str) -> str | None:
        url = "https://api.notion.com/v1/search"
        data = {
            "query": page_title,
            "filter": {
                "property": "object",
                "value": "page"
            }
        }

        response = requests.post(url, headers=self.headers, json=data)

        results = response.json()
        for page in results.get("results", []):
            if page.get("properties", {}).get("title", {}).get("title", [{}])[0].get("plain_text") == page_title:
                return page["id"]

        return None

    def append_drive_info(self, page_id: str, drive: Drive):
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        data = {
            "children": [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": drive.format_heading(),
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": drive.format_body(),
                }
            ]
        }

        response = requests.patch(url, headers=self.headers, json=data)
        if not response.ok:
            json = response.json()
            print(f'Error appending block for drive {drive}: {json["message"]}')
        else:
            print(f'Added Notion section for drive: {drive}')

    def update_drive_info(self, block_id: str, drive: Drive):
        url = f"https://api.notion.com/v1/blocks/{block_id}"
        data = {
            "paragraph": drive.format_body(),
        }

        response = requests.patch(url, headers=self.headers, json=data)
        if not response.ok:
            json = response.json()
            print(f'Error updating block for drive {drive}: {json["message"]}')
        else:
            print(f'Updated Notion section for drive: {drive}')
