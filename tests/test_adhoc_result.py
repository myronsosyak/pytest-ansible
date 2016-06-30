import pytest
from pytest_ansible.results import ModuleResult


positive_host_patterns = {
    'all': 2,
    '*': 2,
    'localhost': 1,
    'local*': 1,
    'local*:&*host': 1,
    '!localhost': 1,
    'all[0]': 1,
    'all[-1]': 1,
    '*[0:1]': 2,  # this is confusing, but how host slicing works
    '*[0:]': 2,
}
negative_host_patterns = {
    'none': 0,
    'all[8:]': 0,
}

valid_hosts = ('localhost', 'another_host')
invalid_hosts = ('none', 'all', '*', 'local*')


@pytest.fixture()
def adhoc_result(hosts):
    return hosts.all.ping()


def test_len(adhoc_result):
    assert len(adhoc_result) == 2


def test_keys(adhoc_result):
    sorted_keys = adhoc_result.keys()
    sorted_keys.sort()
    assert sorted_keys == ['another_host', 'localhost']


@pytest.mark.parametrize("host", valid_hosts)
def test_contains(adhoc_result, host):
    assert host in adhoc_result


@pytest.mark.parametrize("host", invalid_hosts)
def test_not_contains(adhoc_result, host):
    assert host not in adhoc_result


@pytest.mark.parametrize("host_pattern", valid_hosts)
def test_getitem(adhoc_result, host_pattern):
    assert adhoc_result[host_pattern]
    assert isinstance(adhoc_result[host_pattern], ModuleResult)


@pytest.mark.parametrize("host_pattern", invalid_hosts)
def test_not_getitem(adhoc_result, host_pattern):
    with pytest.raises(KeyError):
        assert adhoc_result[host_pattern]


@pytest.mark.parametrize("host_pattern", valid_hosts)
def test_getattr(adhoc_result, host_pattern):
    assert hasattr(adhoc_result, host_pattern)
    assert isinstance(adhoc_result[host_pattern], ModuleResult)


@pytest.mark.parametrize("host_pattern", invalid_hosts)
def test_not_getattr(adhoc_result, host_pattern):
    assert not hasattr(adhoc_result, host_pattern)
    with pytest.raises(AttributeError):
        getattr(adhoc_result, host_pattern)


@pytest.mark.requires_ansible_v1
def test_connection_failure_v1():
    from pytest_ansible.host_manager import get_host_manager
    from pytest_ansible.errors import AnsibleConnectionFailure
    hosts = get_host_manager(inventory='unknown.example.com,', connection='smart')
    exc_info = pytest.raises(AnsibleConnectionFailure, hosts.all.ping)
    # Assert message
    assert exc_info.value.message == "Host unreachable"
    # Assert contacted
    assert exc_info.value.contacted == {}
    # Assert dark
    assert 'unknown.example.com' in exc_info.value.dark
    # Assert unreachable
    assert 'failed' in exc_info.value.dark['unknown.example.com']
    assert exc_info.value.dark['unknown.example.com']['failed']
    # Assert msg
    assert 'msg' in exc_info.value.dark['unknown.example.com']
    assert exc_info.value.dark['unknown.example.com']['msg'].startswith(u'SSH Error: ssh: Could not resolve hostname'
                                                                        ' unknown.example.com:')


@pytest.mark.requires_ansible_v2
def test_connection_failure_v2():
    from pytest_ansible.host_manager import get_host_manager
    from pytest_ansible.errors import AnsibleConnectionFailure
    hosts = get_host_manager(inventory='unknown.example.com,', connection='smart')
    exc_info = pytest.raises(AnsibleConnectionFailure, hosts.all.ping)
    # Assert message
    assert exc_info.value.message == "Host unreachable"
    # Assert contacted
    assert exc_info.value.contacted == {}
    # Assert dark
    assert 'unknown.example.com' in exc_info.value.dark
    # Assert unreachable
    assert 'unreachable' in exc_info.value.dark['unknown.example.com'], exc_info.value.dark.keys()
    assert exc_info.value.dark['unknown.example.com']['unreachable']
    # Assert msg
    assert 'msg' in exc_info.value.dark['unknown.example.com']
    assert exc_info.value.dark['unknown.example.com']['msg'] == u'Failed to connect to the host via ssh.'