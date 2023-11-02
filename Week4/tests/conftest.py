import pytest


@pytest.fixture
def account1(accounts):
    return accounts[0]


@pytest.fixture
def homework3_contract(account1, project):
    return account1.deploy(project.Homework3)
