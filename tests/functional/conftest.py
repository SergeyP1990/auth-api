import pytest
import sys
sys.path.append('/usr/src/tests/')
from settings import HTTPResponse, test_settings


#Загрузка тестовых данных
@pytest.fixture()
def load_test_data():
    pass
