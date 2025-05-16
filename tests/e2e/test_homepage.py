import unittest, time, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

class TestHomePage(unittest.TestCase):
    def setUp(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        gecko_path   = os.path.join(project_root, "geckodriver.exe")
        service      = Service(executable_path=gecko_path)

        self.driver = webdriver.Firefox(service=service)
        self.driver.get("http://localhost:5000")

    def test_homepage_message(self):
        time.sleep(1)
        self.assertIn("Pokemon TCG Collection API", self.driver.page_source)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
