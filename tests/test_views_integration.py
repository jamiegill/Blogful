import os 
import unittest
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TravisConfig"

from blog import app
from blog.database import Base, engine, session, User, Entry

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()
        
        # Set up the tables in the database
        Base.metadata.create_all(engine)
        
        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                        password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()
        
    def tearDown(self):
        #return
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)
                
    def simulate_login(self):
        with self.client.session_transaction() as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True
            
    def test_add_entry(self):
        self.simulate_login()
        
        response = self.client.post("/entry/add", data={
            "title": "Test Entry",
            "content": "Test content"
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 1)
        
        entry = entries[0]
        self.assertEqual(entry.title, "Test Entry")
        self.assertEqual(entry.content, "Test content")
        self.assertEqual(entry.author, self.user)
        
    def test_delete_entry(self):
        self.simulate_login()
        self.test_add_entry()
        session.query(Entry).filter(Entry.id == 1).delete()
        session.commit()
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 0)
        
    def test_edit_entry(self):
        self.simulate_login()
        self.test_add_entry()
        update_record = session.query(Entry).filter_by(id=1).first()
        update_record.title = "update_title"
        update_record.content = "update_content"
        session.commit()
        entry = session.query(Entry).filter_by(id=1).first()
        self.assertEqual(entry.title, "update_title")
        self.assertEqual(entry.content, "update_content")
        
        
if __name__ == "__main__":
    unittest.main()