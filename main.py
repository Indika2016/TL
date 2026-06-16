from kivy.app import App
from kivy.uix.button import Button

class TestBuildApp(App):
    def build(self):
        # A simple, full-screen button to verify the APK runs and registers touches
        return Button(
            text="APK Build Successful!\nClick to Exit",
            font_size=24,
            halign="center",
            background_color=(0.2, 0.6, 1, 1), # Bright blue
            on_press=self.exit_app
        )

    def exit_app(self, instance):
        # Closes the app safely on Android when tapped
        App.get_running_app().stop()

if __name__ == '__main__':
    TestBuildApp().run()
