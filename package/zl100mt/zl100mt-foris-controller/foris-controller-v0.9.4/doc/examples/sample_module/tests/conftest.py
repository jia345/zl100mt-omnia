import pytest
import os

# load common fixtures
from foris_controller_testtools.fixtures import (
    ubusd_acl_path, uci_config_default_path, cmdline_script_root,
    controller_modules, extra_module_paths, message_bus, backend
)


@pytest.fixture(scope="session")
def ubusd_acl_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "ubus-acl")


@pytest.fixture(scope="session")
def uci_config_default_path():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "uci_configs"
    )


@pytest.fixture(scope="session")
def cmdline_script_root():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "test_root"
    )


@pytest.fixture(scope="module")
def controller_modules():
    return ["sample"]


def pytest_addoption(parser):
    parser.addoption(
        "--backend", action="append",
        default=[],
        help=("Set test backend here. available values = (mock, openwrt)")
    )
    parser.addoption(
        "--debug-output", action="store_true",
        default=False,
        help=("Whether show output of foris-controller cmd")
    )


def pytest_generate_tests(metafunc):
    if 'backend' in metafunc.fixturenames:
        backend = set(metafunc.config.option.backend)
        if not backend:
            backend = ['mock']
        metafunc.parametrize("backend_param", backend, scope='module')
