
from copy import error
import sys
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel
)
import requests


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
                "http://127.0.0.1:8000/ask",
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

        self.chat = ChatWindow()
        self.drag_position = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.walk)
        self.timer.start(40)

    def walk(self):
        # Pause automatic walking while the user drags the doll
        if self.drag_position is not None:
            return

        step = 4
        next_x = self.x() + self.direction * step
        if next_x <= self.left_edge:
            next_x = self.left_edge
            self.direction = 1
        elif next_x >= self.right_edge:
            next_x = self.right_edge
            self.direction = -1
        self.move(next_x, self.y_position)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        # Mirror the character so it faces the direction it is walking.
        if self.direction < 0:
            painter.translate(self.width(), 0)
            painter.scale(-1, 1)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#49334f"))
        painter.drawEllipse(35, 25, 110, 120)

        painter.setBrush(QColor("#ffe0cf"))
        painter.drawEllipse(43, 35, 94, 105)

        painter.setBrush(QColor("#49334f"))
        painter.drawEllipse(40, 24, 100, 52)

        painter.setBrush(QColor("#34233c"))
        painter.drawEllipse(61, 72, 17, 23)
        painter.drawEllipse(102, 72, 17, 23)

        painter.setBrush(QColor("white"))
        painter.drawEllipse(65, 76, 5, 6)
        painter.drawEllipse(106, 76, 5, 6)

        painter.setBrush(QColor("#f5a5a5"))
        painter.drawEllipse(49, 96, 18, 9)
        painter.drawEllipse(112, 96, 18, 9)

        painter.setPen(QPen(QColor("#9e5360"), 2))
        painter.drawArc(78, 99, 25, 15, 200 * 16, 140 * 16)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#d8b4f8"))
        painter.drawRoundedRect(48, 139, 84, 65, 22, 22)

        painter.setBrush(QColor("#fff0fa"))
        from PySide6.QtGui import QPolygon
        painter.drawPolygon(QPolygon([
            QPoint(75, 143),
            QPoint(90, 166),
            QPoint(105, 143),
        ]))

        painter.setPen(QColor("#49334f"))
        painter.drawText(
            15, 222, self.width() - 30, 20,
            Qt.AlignmentFlag.AlignCenter,
            "Vanakkam! ♡"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.pos()
            )
            self.timer.stop()

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

                self.timer.start(40)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    doll = AnimeDoll()
    doll.show()
    sys.exit(app.exec())
