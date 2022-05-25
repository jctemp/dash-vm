from textual.app import App
from textual.widgets import Footer, Placeholder

class SmoothApp(App):
    """Demonstrates smooth animation. Press 'b' to see it in action."""

    def on_key(self, event):
        if event.key.isdigit():
            self.background = f"on color({event.key})"

    async def on_load(self) -> None:
        """Bind keys here."""
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        """Build layout here."""
        footer = Footer()

        await self.view.dock(footer, edge="bottom")
        await self.view.dock(Placeholder(), edge="left", size=40)
        await self.view.dock(Placeholder(), edge="right")

        # self.set_timer(10, lambda: self.action("quit"))b


SmoothApp.run(log="textual.log", log_verbosity=2)