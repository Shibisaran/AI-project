
from copy import error
import os
import sys
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QMovie, QTransform
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel
)
import requests


API_URL = os.environ.get("CHATBOT_API_URL", "http://0.0.0.0:8000").rstrip("/")


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tamil Anime Companion")
        self.resize(340, 420)

        layout = QVBoxLayout(self)

        title = QLabel("♡ Vanakkam! Let's chat ♡")
        layout.addWidget(title)

        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.append(
            "Doll: Vanakkam! I'm your anime companion.\n"
            "Doll: Soon, I'll be powered by a local AI model!"
        )
        layout.addWidget(self.history)

        self.message = QLineEdit()
        self.message.setPlaceholderText("Type in Tamil or English...")
        self.message.returnPressed.connect(self.send_message)
        layout.addWidget(self.message)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

    def send_message(self):
        text = self.message.text().strip()
        if not text:
            return

        self.history.append(f"You: {text}")

        try:
            response = requests.get(
                f"{API_URL}/ask",
                params={"question": text},
                timeout=120
            )
            response.raise_for_status()
            answer = response.json()["answer"]
            self.history.append(f"Doll: {answer}")
        except requests.RequestException as error:
            self.history.append(
                f"Doll: I couldn't reach the local AI service. {error}"
            )
        except (KeyError, ValueError):
            self.history.append("Doll: The AI service returned an unexpected response.")

        self.message.clear()


class AnimeDoll(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tamil Anime Companion")
        self.setFixedSize(180, 230)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        screen = QApplication.primaryScreen().availableGeometry()
        self.bounds = screen
        self.y_position = screen.bottom() - self.height() - 30
        self.left_edge = screen.left() + 20
        self.right_edge = screen.right() - self.width() + 1 - 20
        self.direction = 1  # 1 = right, -1 = left
        self.move(self.left_edge, self.y_position)
        self.sprite = QLabel(self)
        self.sprite.setGeometry(0, 0, self.width(), self.height())
        self.sprite.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        self.walk_movie = QMovie("assets/walk-right.gif")
        self.walk_movie.frameChanged.connect(self.animate_step)
        self.walk_movie.start()

        self.chat = ChatWindow()
        self.drag_position = None

    def walk(self):
        if self.drag_position is not None:
            return

        # Move once for every frame of the 12-fps GIF.
        step = 8
        next_x = self.x() + self.direction * step

        if next_x <= self.left_edge:
            next_x = self.left_edge
            self.direction = 1
        elif next_x >= self.right_edge:
            next_x = self.right_edge
            self.direction = -1

        self.move(next_x, self.y_position)

    def animate_step(self, frame_number):
        self.walk()

        frame = self.walk_movie.currentPixmap()
        if self.direction > 0:
            frame = frame.transformed(QTransform().scale(-1, 1))

        self.sprite.setPixmap(frame)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.pos()
            )

    def mouseMoveEvent(self, event):
        if (
            self.drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            new_pos = (
                event.globalPosition().toPoint()
                - self.drag_position
            )
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.drag_position is not None:
                distance = (
                    event.globalPosition().toPoint()
                    - self.drag_position
                    - self.pos()
                ).manhattanLength()

                self.drag_position = None

                # A simple click opens the chat;
                # a drag only moves the character.
                if distance < 8:
                    self.chat.show()
                    self.chat.raise_()
                    self.chat.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    doll = AnimeDoll()
    doll.show()
    sys.exit(app.exec())
