import sys

from PyQt6.QtWidgets import QApplication, QDialog

from database import DatabaseManager
from dialogs import AuthWindow
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    db = DatabaseManager()
    auth_window = AuthWindow(db)

    if auth_window.exec() == QDialog.DialogCode.Accepted:
        profile_id = auth_window.profile_id
        if profile_id:
            main_window = MainWindow(profile_id, db)
            main_window.show()
            sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == "__main__":
    main()
