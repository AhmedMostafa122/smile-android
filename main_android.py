"""
اِبْتَسِم (Smile) - Android Multimedia Download Manager
Kivy-based version for Android devices
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.spinner import Spinner
from kivy.garden.navigationdrawer import NavigationDrawer
from kivy.uix.rst import RstDocument
from kivy_garden.tabs import TabbedPanel, TabbedPanelItem
import threading
import os

# Set window size for mobile
Window.size = (480, 800)

from queue_system import add_to_queue, worker, pause, resume, cancel, get_queue_size, get_status_snapshot
from theme_android import get_theme_manager


class SmileAndroidApp(App):
    def build(self):
        self.title = 'اِبْتَسِم (Smile)'
        self.theme_manager = get_theme_manager()
        self.current_theme = 'dark_gold'
        
        # Start queue worker thread
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        main_layout.canvas.before.clear()
        
        # Set background color
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        # Header
        header = Label(text='اِبْتَسِم - Download Manager', size_hint_y=0.1, bold=True, font_size='20sp')
        main_layout.add_widget(header)
        
        # URL Input
        url_layout = BoxLayout(orientation='vertical', size_hint_y=0.15, spacing=5)
        url_label = Label(text='Enter URL or Search:', size_hint_y=0.3)
        self.url_input = TextInput(
            multiline=False,
            hint_text='Paste video/audio URL here...',
            size_hint_y=0.7
        )
        url_layout.add_widget(url_label)
        url_layout.add_widget(self.url_input)
        main_layout.add_widget(url_layout)
        
        # Format Selection
        format_layout = BoxLayout(size_hint_y=0.08, spacing=5)
        format_label = Label(text='Format:', size_hint_x=0.3)
        self.format_spinner = Spinner(
            text='MP4',
            values=('MP4', 'MP3', 'M4A', 'WebM', 'MKV', 'FLAC'),
            size_hint_x=0.7
        )
        format_layout.add_widget(format_label)
        format_layout.add_widget(self.format_spinner)
        main_layout.add_widget(format_layout)
        
        # Download Button
        btn_layout = BoxLayout(size_hint_y=0.08, spacing=5)
        download_btn = Button(text='📥 Download')
        download_btn.bind(on_press=self.start_download)
        btn_layout.add_widget(download_btn)
        main_layout.add_widget(btn_layout)
        
        # Progress and Status
        status_layout = BoxLayout(orientation='vertical', size_hint_y=0.15, spacing=5)
        self.status_label = Label(text='Status: Ready', size_hint_y=0.5)
        self.progress_bar = ProgressBar(value=0, size_hint_y=0.5)
        status_layout.add_widget(self.status_label)
        status_layout.add_widget(self.progress_bar)
        main_layout.add_widget(status_layout)
        
        # Queue Display
        queue_scroll = ScrollView(size_hint_y=0.35)
        self.queue_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        self.queue_layout.bind(minimum_height=self.queue_layout.setter('height'))
        queue_scroll.add_widget(self.queue_layout)
        main_layout.add_widget(queue_scroll)
        
        # Control Buttons
        control_layout = BoxLayout(size_hint_y=0.08, spacing=5)
        pause_btn = Button(text='⏸ Pause')
        pause_btn.bind(on_press=lambda x: pause())
        resume_btn = Button(text='▶ Resume')
        resume_btn.bind(on_press=lambda x: resume())
        cancel_btn = Button(text='✕ Cancel')
        cancel_btn.bind(on_press=lambda x: cancel())
        control_layout.add_widget(pause_btn)
        control_layout.add_widget(resume_btn)
        control_layout.add_widget(cancel_btn)
        main_layout.add_widget(control_layout)
        
        # Update status periodically
        Clock.schedule_interval(self.update_status, 1)
        
        return main_layout
    
    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup('Error', 'Please enter a URL')
            return
        
        format_choice = self.format_spinner.text.lower()
        add_to_queue(url, format_choice)
        self.url_input.text = ''
        self.show_popup('Added', f'Download queued as {format_choice.upper()}')
    
    def update_status(self, dt):
        status = get_status_snapshot()
        queue_size = get_queue_size()
        
        # Update status label
        if status:
            self.status_label.text = f"Status: {status['status']} - {status.get('speed', 'N/A')}"
            self.progress_bar.value = status.get('progress', 0)
        else:
            self.status_label.text = f"Queue: {queue_size} items pending"
            self.progress_bar.value = 0
        
        # Update queue display
        self.update_queue_display(queue_size)
    
    def update_queue_display(self, queue_size):
        self.queue_layout.clear_widgets()
        for i in range(min(queue_size, 5)):
            item_label = Label(
                text=f'Item {i+1} in queue',
                size_hint_y=None,
                height=40
            )
            self.queue_layout.add_widget(item_label)
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message))
        close_btn = Button(text='Close', size_hint_y=0.3)
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    SmileAndroidApp().run()
