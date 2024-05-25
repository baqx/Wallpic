import requests
import ctypes
import os
import flet as ft
import re

# Directory to save downloaded wallpapers
WALLPAPER_DIR = os.path.join(os.path.expanduser("~"), "Wallpapers")

# Create the directory if it does not exist
if not os.path.exists(WALLPAPER_DIR):
    os.makedirs(WALLPAPER_DIR)

PEXELS_API_KEY = ""  #Replace with your pexels api key
PEXELS_URL = "https://api.pexels.com/v1/search"

def fetch_images(query=""):
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": query,
        "per_page": 20
    }
    response = requests.get(PEXELS_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["photos"]
    return []

def sanitize_filename(filename):
    return re.sub(r'[^\w\-_\. ]', '_', filename)

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    return None

def set_wallpaper(image_path):
    # This is for Windows
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)

def main(page: ft.Page):
    page.title = "Wallpic"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    page.window_title_bar_hidden = True
    page.window_title_bar_buttons_hidden = True

    search_input = ft.TextField(label="Search Wallpapers", width=300)
    search_button = ft.ElevatedButton(text="Search", on_click=lambda _: search_images(search_input.value))
    search_row = ft.Row(controls=[search_input, search_button], alignment="center")

    page.add(
        ft.Row(
            [
                ft.WindowDragArea(ft.Container(ft.Text("Wallpic"), bgcolor=ft.colors.TRANSPARENT, padding=10), expand=True),
                ft.IconButton(ft.icons.CLOSE, on_click=lambda _: page.window_close())
            ]
        )
    )
    page.add(search_row)

    loading_indicator = ft.ProgressRing(width=50, height=50, visible=False)
    page.add(loading_indicator)

    images_grid = ft.GridView(
        expand=1,
        runs_count=5,
        max_extent=150,
        child_aspect_ratio=1.0,
        spacing=5,
        run_spacing=5
    )
    page.add(images_grid)

    def show_snackbar(message):
        page.show_snack_bar(ft.SnackBar(ft.Text(message), open=True))
        
    def search_images(query="nature"):
        images_grid.controls.clear()
        loading_indicator.visible = True
        page.update()

        images = fetch_images(query)
        loading_indicator.visible = False
        for image in images:
            img_url = image["src"]["large"]
            img_widget = ft.Container(
                content=ft.Image(
                    src=img_url,
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.border_radius.all(10),
                ),
                on_click=lambda e, img_url=img_url: show_fullscreen_image(img_url),
            )
            images_grid.controls.append(img_widget)
        page.update()

    def show_fullscreen_image(img_url):
        def close_modal(e):
            page.overlay.pop()
            page.update()

        def choose_wallpaper(e):
            sanitized_filename = sanitize_filename(f"{os.path.basename(img_url).split('?')[0]}.jpg")
            filename = os.path.join(WALLPAPER_DIR, sanitized_filename)
            image_path = download_image(img_url, filename)
            if image_path:
                set_wallpaper(image_path)
                show_snackbar("Wallpaper set successfully!")
            close_modal(e)

        img_modal = ft.Image(src=img_url, width=800, height=600)
        choose_button = ft.ElevatedButton(text="Choose Wallpaper", on_click=choose_wallpaper)
        close_button = ft.ElevatedButton(text="Close", on_click=close_modal)
        modal_content = ft.Row(
            controls=[
                img_modal, 
                ft.Row(controls=[choose_button, close_button], alignment="center")
            ], 
            alignment="center"
        )
        modal = ft.Container(content=modal_content, bgcolor=ft.colors.BLACK87, padding=50, alignment=ft.alignment.center)
        page.overlay.append(modal)
        page.update()

    search_images()  # Load initial images

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
