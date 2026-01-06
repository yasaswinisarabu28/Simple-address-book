import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QFrame, QDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# ================= Contact Dialog =================
class ContactDialog(QDialog):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.contact = contact
        self.setWindowTitle("👤 Contact Details")
        self.setFixedSize(500, 500)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Top Half: Circle + Logos
        top_frame = QFrame()
        top_frame.setStyleSheet("background-color: #E6E6FA; border-radius: 15px;")
        top_layout = QVBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)

        # Circle avatar
        circle_widget = QWidget()
        circle_layout = QVBoxLayout()
        circle_layout.setAlignment(Qt.AlignCenter)
        first_letter = self.contact['name'][0].upper() if self.contact['name'] else "?"
        circle = QLabel(first_letter)
        circle.setFixedSize(120, 120)
        circle.setAlignment(Qt.AlignCenter)
        circle.setStyleSheet("""
            background-color: #98FB98;
            border-radius: 60px;
            font-size: 48px;
            font-weight: bold;
            color: white;
        """)
        circle_layout.addWidget(circle)
        circle_widget.setLayout(circle_layout)
        top_layout.addWidget(circle_widget)
        top_layout.addSpacing(15)

        # Logos
        logos_layout = QHBoxLayout()
        logos_layout.setSpacing(25)
        logos_layout.setAlignment(Qt.AlignCenter)
        for logo in ["📞", "💬", "🎥", "📧"]:
            lbl = QLabel(logo)
            lbl.setFont(QFont("Segoe UI Emoji", 28))
            logos_layout.addWidget(lbl)
        top_layout.addLayout(logos_layout)
        top_frame.setLayout(top_layout)

        # Bottom Half: Contact Details
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("background-color: #F0FFF0; border-radius: 15px;")
        bottom_layout = QVBoxLayout()
        bottom_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        bottom_layout.setSpacing(10)

        # Name
        name_label = QLabel(self.contact['name'])
        name_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(name_label)

        # Phone
        phone_label = QLabel(f"📞 {self.contact['phone']}")
        phone_label.setFont(QFont("Segoe UI", 16))
        phone_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(phone_label)

        # Email
        email_label = QLabel(f"✉️ {self.contact['email']}")
        email_label.setFont(QFont("Segoe UI", 16))
        email_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(email_label)

        # Address
        address_label = QLabel(f"🏠 {self.contact['address']}")
        address_label.setFont(QFont("Segoe UI", 16))
        address_label.setAlignment(Qt.AlignCenter)
        address_label.setWordWrap(True)
        bottom_layout.addWidget(address_label)

        bottom_frame.setLayout(bottom_layout)

        main_layout.addWidget(top_frame, 2)
        main_layout.addWidget(bottom_frame, 3)
        self.setLayout(main_layout)


# ================= Contact List Dialog =================
class ContactListDialog(QDialog):
    def __init__(self, contacts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📇 Saved Contacts")
        self.setFixedSize(600, 800)
        self.contacts = contacts
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search bar at top
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍")
        search_label.setFont(QFont("Segoe UI Emoji", 16))
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or phone...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setFont(QFont("Segoe UI", 11))
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(230, 230, 250, 0.3);
                border: 2px solid rgba(230, 230, 250, 0.6);
                border-radius: 12px;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                background-color: rgba(230, 230, 250, 0.5);
                border: 2px solid #E6E6FA;
            }
        """)
        self.search_input.textChanged.connect(self.filter_contacts)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)

        # Contact list
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.show_contact_dialog)

        font = QFont("Arial", 14)
        font.setBold(True)
        self.list_widget.setFont(font)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #f8f8f8;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 12px;
                margin: 4px;
            }
            QListWidget::item:selected {
                background-color: #c3a6ff;
                color: black;
                border-radius: 5px;
            }
        """)

        self.refresh_list()
        layout.addWidget(self.list_widget)

        # Edit button (purple)
        self.edit_btn = QPushButton("✏️ Edit Contact")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.edit_btn.clicked.connect(self.edit_selected_contact)
        layout.addWidget(self.edit_btn)

        # Delete button (red)
        self.delete_btn = QPushButton("🗑 Delete Contact")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_contact)
        layout.addWidget(self.delete_btn)

        self.setLayout(layout)

    def refresh_list(self):
        """Refresh the contact list display"""
        self.list_widget.clear()
        self.contacts = self.parent.contacts if self.parent else []
        for contact in self.contacts:
            item = QListWidgetItem(f"{contact['name']}\n📞 {contact['phone']}")
            self.list_widget.addItem(item)

    def filter_contacts(self):
        """Filter contacts based on search input"""
        search_text = self.search_input.text().strip().lower()
        self.list_widget.clear()
        
        for contact in self.contacts:
            if (search_text in contact['name'].lower() or 
                search_text in contact['phone'].lower()):
                item = QListWidgetItem(f"{contact['name']}\n📞 {contact['phone']}")
                self.list_widget.addItem(item)

    def edit_selected_contact(self):
        index = self.list_widget.currentRow()
        if index < 0:
            QMessageBox.warning(self, "No Selection", "Please select a contact to edit.")
            return
        
        # Get the actual contact from filtered list
        selected_item = self.list_widget.item(index)
        selected_text = selected_item.text().split('\n')[0]  # Get name from item
        
        # Find the contact in the full list
        contact = None
        actual_index = None
        for idx, c in enumerate(self.parent.contacts):
            if c['name'] == selected_text:
                contact = c
                actual_index = idx
                break
        
        if contact and self.parent:
            self.parent.load_contact_into_form(contact, actual_index)
        self.close()

    def delete_selected_contact(self):
        index = self.list_widget.currentRow()
        if index < 0:
            QMessageBox.warning(self, "No Selection", "Please select a contact to delete.")
            return

        # Get the actual contact from filtered list
        selected_item = self.list_widget.item(index)
        selected_text = selected_item.text().split('\n')[0]  # Get name from item
        
        # Find the contact in the full list
        contact = None
        for c in self.contacts:
            if c['name'] == selected_text:
                contact = c
                break
        
        if not contact:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{contact['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            contact_id = contact['id']
            try:
                self.parent.cursor.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
                self.parent.conn.commit()
                self.parent.load_contacts_from_db()
                self.refresh_list()
                QMessageBox.information(self, "Deleted", "✅ Contact deleted successfully!")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete contact: {str(e)}")

    def show_contact_dialog(self, item):
        # Get the name from the item
        selected_text = item.text().split('\n')[0]
        
        # Find the contact in the full list
        contact = None
        for c in self.contacts:
            if c['name'] == selected_text:
                contact = c
                break
        
        if contact:
            dialog = ContactDialog(contact, self)
            dialog.exec_()


# ================= Main Window =================
class SimpleAddressBook(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💻 Simple Address Book System")
        screen = QApplication.primaryScreen()
        size = screen.size()
        self.setGeometry(0, 0, size.width(), size.height())

        self.setStyleSheet("background-color: #E6E6FA;")
        self.contacts = []
        self.selected_index = None

        self.init_db()
        self.load_contacts_from_db()
        self.init_ui()

    def init_db(self):
        """Initialize database connection and create table if not exists"""
        try:
            self.conn = sqlite3.connect("contacts.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    address TEXT
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to initialize database: {str(e)}")
            sys.exit(1)

    def load_contacts_from_db(self):
        """Load all contacts from database"""
        try:
            self.contacts.clear()
            self.cursor.execute("SELECT * FROM contacts")
            rows = self.cursor.fetchall()
            for row in rows:
                self.contacts.append({
                    "id": row[0],
                    "name": row[1],
                    "phone": row[2],
                    "email": row[3],
                    "address": row[4]
                })
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load contacts: {str(e)}")

    def save_contact_to_db(self, contact, contact_id=None):
        """Save or update contact in database"""
        try:
            if contact_id:
                self.cursor.execute("""
                    UPDATE contacts
                    SET name=?, phone=?, email=?, address=?
                    WHERE id=?
                """, (contact['name'], contact['phone'], contact['email'], contact['address'], contact_id))
            else:
                self.cursor.execute("""
                    INSERT INTO contacts (name, phone, email, address)
                    VALUES (?, ?, ?, ?)
                """, (contact['name'], contact['phone'], contact['email'], contact['address']))
            self.conn.commit()
            self.load_contacts_from_db()
            return True
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save contact: {str(e)}")
            return False

    def load_contact_into_form(self, contact, index):
        """Load contact data into form for editing"""
        self.selected_index = index
        self.name_input.setText(contact["name"])
        self.phone_input.setText(contact["phone"])
        self.email_input.setText(contact["email"])
        self.address_input.setText(contact["address"])
        self.add_btn.setText("💾 Save Changes")

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Form container
        form_container = QFrame()
        form_container.setFixedWidth(int(self.width() * 0.75))
        form_container.setStyleSheet("background-color: #F0FFF0; border-radius: 15px;")
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        # Header with 3-dots button
        header_layout = QHBoxLayout()
        header_label = QLabel("Simple Address Book System")
        header_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header_label.setStyleSheet("color: #32CD32;")
        header_layout.addWidget(header_label)

        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setFont(QFont("Segoe UI", 20))
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #98FB98;
                color: white;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
        """)
        self.menu_btn.clicked.connect(self.show_contact_list)
        header_layout.addStretch()
        header_layout.addWidget(self.menu_btn)

        form_layout.addLayout(header_layout)

        # Input field styling
        input_style = """
            QLineEdit {
                background-color: rgba(230, 230, 250, 0.3);
                border: 2px solid rgba(230, 230, 250, 0.6);
                border-radius: 15px;
                padding: 10px 15px;
            }
            QLineEdit:focus {
                background-color: rgba(230, 230, 250, 0.5);
                border: 2px solid #E6E6FA;
            }
        """
        
        textarea_style = """
            QTextEdit {
                background-color: rgba(230, 230, 250, 0.3);
                border: 2px solid rgba(230, 230, 250, 0.6);
                border-radius: 15px;
                padding: 10px 15px;
            }
            QTextEdit:focus {
                background-color: rgba(230, 230, 250, 0.5);
                border: 2px solid #E6E6FA;
            }
        """

        # Form inputs
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.name_input.setMinimumHeight(50)
        self.name_input.setFont(QFont("Segoe UI", 12))
        self.name_input.setStyleSheet(input_style)
        self.name_input.returnPressed.connect(self.add_or_update_contact)
        form_layout.addWidget(self.name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number")
        self.phone_input.setMinimumHeight(50)
        self.phone_input.setFont(QFont("Segoe UI", 12))
        self.phone_input.setStyleSheet(input_style)
        self.phone_input.returnPressed.connect(self.add_or_update_contact)
        form_layout.addWidget(self.phone_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.email_input.setMinimumHeight(50)
        self.email_input.setFont(QFont("Segoe UI", 12))
        self.email_input.setStyleSheet(input_style)
        self.email_input.returnPressed.connect(self.add_or_update_contact)
        form_layout.addWidget(self.email_input)

        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Address")
        self.address_input.setFixedHeight(90)
        self.address_input.setFont(QFont("Segoe UI", 12))
        self.address_input.setStyleSheet(textarea_style)
        form_layout.addWidget(self.address_input)

        self.add_btn = QPushButton("➕ Add Contact")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #98FB98;
                color: white; 
                font-weight: bold; 
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
        """)
        self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_or_update_contact)
        form_layout.addWidget(self.add_btn)

        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)
        self.setLayout(main_layout)

    def add_or_update_contact(self):
        """Add new contact or update existing one"""
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.toPlainText().strip()

        if not name or not phone:
            QMessageBox.warning(self, "Input Error", "Name and Phone are required.")
            return

        contact = {"name": name, "phone": phone, "email": email, "address": address}

        if self.selected_index is not None:
            contact_id = self.contacts[self.selected_index]['id']
            if self.save_contact_to_db(contact, contact_id):
                self.selected_index = None
                self.add_btn.setText("➕ Add Contact")
                QMessageBox.information(self, "Success", "✅ Contact updated successfully!")
                self.clear_form()
        else:
            if self.save_contact_to_db(contact):
                QMessageBox.information(self, "Success", "✅ Contact saved successfully!")
                self.clear_form()

    def clear_form(self):
        """Clear all form inputs"""
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()

    def show_contact_list(self):
        """Show contact list dialog"""
        dialog = ContactListDialog(self.contacts, self)
        dialog.exec_()

    def closeEvent(self, event):
        """Properly close database connection when closing application"""
        if hasattr(self, 'conn'):
            self.conn.close()
        event.accept()


# ================= Run App =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleAddressBook()
    window.showMaximized()
    sys.exit(app.exec_())
