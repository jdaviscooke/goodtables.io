import pytest
from goodtablesio.tests import factories
from goodtablesio.integrations.github.tasks.repos import sync_user_repos
pytestmark = pytest.mark.usefixtures('session_cleanup')


# Tests

def test_sync_user_repos(GitHubForIterRepos):
    user = factories.User(github_oauth_token='my-token')
    sync_user_repos(user.id)
    GitHubForIterRepos.assert_called_with(token='my-token')
    assert user.sources[0].conf['github_id'] == 'id1'
    assert user.sources[0].name == 'owner1/repo1'
    assert user.sources[0].active is True
    assert user.sources[1].conf['github_id'] == 'id2'
    assert user.sources[1].name == 'owner2/repo2'
    assert user.sources[1].active is False
